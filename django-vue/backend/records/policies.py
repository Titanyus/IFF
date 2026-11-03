"""Single permission boundary for list, detail, updates and trash."""
from .models import CareCase


def has_group(user, name):
    return user.is_authenticated and user.groups.filter(name=name).exists()


def can_manage(user):
    return has_group(user, "Leitung") or has_group(user, "Verwaltung")


def can_trash(user):
    return has_group(user, "Leitung")


def visible_cases(user, *, include_trashed=False):
    if not user.is_authenticated:
        return CareCase.objects.none()
    if can_manage(user):
        qs = CareCase.objects.all()
    elif has_group(user, "Therapie"):
        qs = CareCase.objects.filter(assigned_therapists=user)
    else:
        return CareCase.objects.none()
    if not (include_trashed and can_trash(user)):
        qs = qs.filter(deleted_at__isnull=True)
    return qs.distinct()
