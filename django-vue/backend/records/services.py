"""Business actions: transitions are validated, atomic and audited."""
from datetime import date
from django.db import transaction
from .models import AuditEvent, CareCase


class InvalidTransition(ValueError):
    pass


def parse_iso_day(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise InvalidTransition("Ein gültiges Datum (JJJJ-MM-TT) ist erforderlich.")


@transaction.atomic
def change_status(*, case_id, actor, target, effective_on):
    case = CareCase.objects.select_for_update().get(pk=case_id, deleted_at__isnull=True)
    old = case.status
    day = parse_iso_day(effective_on)
    if old == CareCase.WAITING and target == CareCase.ACTIVE:
        if day < case.requested_on:
            raise InvalidTransition("Förderbeginn darf nicht vor Anmeldung liegen.")
        case.started_on = day
    elif old == CareCase.ACTIVE and target == CareCase.CLOSED:
        if not case.started_on or day < case.started_on:
            raise InvalidTransition("Enddatum muss ab Förderbeginn liegen.")
        case.ended_on = day
    else:
        raise InvalidTransition("Dieser Statuswechsel ist nicht erlaubt.")
    case.status = target
    case.full_clean()
    case.save(update_fields=["status", "started_on", "ended_on"])
    AuditEvent.objects.create(case=case, actor=actor, action="status", from_status=old, to_status=target)
    return case
