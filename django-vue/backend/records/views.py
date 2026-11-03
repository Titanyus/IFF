"""Small same-origin JSON API; Django sessions & CSRF, no DRF required."""
import json
from functools import wraps
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db import transaction
from django.http import Http404, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Child, Guardian, ChildGuardian, CareCase, AuditEvent
from .policies import can_manage, can_trash, visible_cases
from .services import change_status, InvalidTransition, parse_iso_day


def api_login_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Anmeldung erforderlich."}, status=401)
        return view(request, *args, **kwargs)
    return wrapped


def payload(request):
    try:
        value = json.loads(request.body or b"{}")
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        return value
    except (ValueError, UnicodeDecodeError):
        raise ValueError("Ungültige JSON-Daten.")


def error(message, status=400):
    return JsonResponse({"error": str(message)}, status=status)


@require_GET
@ensure_csrf_cookie
def session_info(request):
    user = request.user
    return JsonResponse({
        "authenticated": user.is_authenticated,
        "csrfToken": get_token(request),
        "user": ({"username": user.username, "groups": list(user.groups.values_list("name", flat=True)),
                  "canManage": can_manage(user), "canTrash": can_trash(user)} if user.is_authenticated else None),
    })


@require_POST
def login(request):
    try:
        data = payload(request)
    except ValueError as exc:
        return error(exc)
    user = authenticate(request, username=str(data.get("username", "")), password=str(data.get("password", "")))
    if not user:
        return error("Anmeldung fehlgeschlagen.", 401)
    auth_login(request, user)
    return JsonResponse({"ok": True})


@require_POST
def logout(request):
    auth_logout(request)
    return JsonResponse({"ok": True})


def serialize_case(case, detail=False):
    links = list(case.child.guardian_links.select_related("guardian").all())
    value = {
        "id": case.pk, "status": case.status, "requestedOn": case.requested_on.isoformat(),
        "startedOn": case.started_on.isoformat() if case.started_on else None,
        "endedOn": case.ended_on.isoformat() if case.ended_on else None,
        "deleted": case.deleted_at is not None,
        "child": {"id": case.child_id, "name": str(case.child)},
        "guardians": [{"id": l.guardian_id, "name": l.guardian.full_name} for l in links],
    }
    if detail:
        value["events"] = [{"action": e.action, "from": e.from_status, "to": e.to_status,
                             "actor": e.actor.username, "at": e.at.isoformat()}
                            for e in case.events.select_related("actor").all()]
    return value


@require_http_methods(["GET", "POST"])
@api_login_required
def cases(request):
    if request.method == "GET":
        status = request.GET.get("status", "waiting")
        if status not in ["waiting", "active", "closed", "all", "trashed"]:
            return error("Unbekannter Filter.")
        if status == "trashed" and not can_trash(request.user):
            return error("Keine Berechtigung.", 403)
        qs = visible_cases(request.user, include_trashed=status == "trashed")
        qs = qs.filter(deleted_at__isnull=False) if status == "trashed" else qs.filter(deleted_at__isnull=True)
        if status in ["waiting", "active", "closed"]:
            qs = qs.filter(status=status)
        return JsonResponse({"cases": [serialize_case(c) for c in qs.select_related("child")]})

    if not can_manage(request.user):
        return error("Keine Berechtigung.", 403)
    try:
        data = payload(request)
        first = str(data.get("firstName", "")).strip()
        last = str(data.get("lastName", "")).strip()
        guardian_id = data.get("guardianId")
        guardian_name = str(data.get("guardianName", "")).strip()
        if not first or not last or len(first) > 100 or len(last) > 100:
            raise ValueError("Vor- und Nachname sind erforderlich (max. 100 Zeichen).")
        if not guardian_id and (not guardian_name or len(guardian_name) > 200):
            raise ValueError("Sorgeberechtigte Person auswählen oder Namen eingeben.")
        requested_on = parse_iso_day(data.get("requestedOn"))
        with transaction.atomic():
            guardian = get_object_or_404(Guardian, pk=guardian_id) if guardian_id else Guardian.objects.create(full_name=guardian_name)
            child = Child.objects.create(first_name=first, last_name=last)
            ChildGuardian.objects.create(child=child, guardian=guardian)
            case = CareCase.objects.create(child=child, requested_on=requested_on)
            AuditEvent.objects.create(case=case, actor=request.user, action="created", to_status="waiting")
        return JsonResponse({"case": serialize_case(case)}, status=201)
    except (InvalidTransition, ValueError) as exc:
        return error(exc)


@require_GET
@api_login_required
def guardians(request):
    if not can_manage(request.user):
        return error("Keine Berechtigung.", 403)
    return JsonResponse({"guardians": [{"id": g.pk, "name": g.full_name} for g in Guardian.objects.order_by("full_name")]})


@require_GET
@api_login_required
def case_detail(request, case_id):
    case = get_object_or_404(visible_cases(request.user, include_trashed=can_trash(request.user)), pk=case_id)
    return JsonResponse({"case": serialize_case(case, detail=True)})


@require_POST
@api_login_required
def transition(request, case_id):
    if not can_manage(request.user):
        return error("Keine Berechtigung.", 403)
    get_object_or_404(visible_cases(request.user), pk=case_id)
    try:
        data = payload(request)
        case = change_status(case_id=case_id, actor=request.user,
                             target=data.get("to"), effective_on=data.get("effectiveOn"))
        return JsonResponse({"case": serialize_case(case)})
    except (InvalidTransition, ValueError) as exc:
        return error(exc)


@require_POST
@api_login_required
def trash(request, case_id):
    if not can_trash(request.user):
        return error("Keine Berechtigung.", 403)
    with transaction.atomic():
        case = get_object_or_404(CareCase.objects.select_for_update(), pk=case_id, deleted_at__isnull=True)
        case.deleted_at = timezone.now()
        case.save(update_fields=["deleted_at"])
        AuditEvent.objects.create(case=case, actor=request.user, action="trash")
    return JsonResponse({"ok": True})


@require_POST
@api_login_required
def restore(request, case_id):
    if not can_trash(request.user):
        return error("Keine Berechtigung.", 403)
    with transaction.atomic():
        case = get_object_or_404(CareCase.objects.select_for_update(), pk=case_id, deleted_at__isnull=False)
        case.deleted_at = None
        case.save(update_fields=["deleted_at"])
        AuditEvent.objects.create(case=case, actor=request.user, action="restore")
    return JsonResponse({"ok": True})
