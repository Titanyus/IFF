from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from records.models import Child, Guardian, ChildGuardian, CareCase, AuditEvent


class Command(BaseCommand):
    help = "Seed fictional PoC records (idempotent)"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        User = get_user_model()
        accounts = [
            ("leitung", "Leitung"), ("verwaltung", "Verwaltung"),
            ("therapie1", "Therapie"), ("therapie2", "Therapie"),
        ]
        members = {}
        for username, role in accounts:
            group, _ = Group.objects.get_or_create(name=role)
            user, created = User.objects.get_or_create(username=username + "@example.test")
            if created:
                user.set_password("DemoPass-2026!")
                user.save(update_fields=["password"])
            user.groups.add(group)
            members[username] = user
        if CareCase.objects.exists():
            self.stdout.write("PoC seed exists; leaving data intact.")
            return
        shared_guardian = Guardian.objects.create(full_name="Alex Beispiel")
        cases = [
            ("Emma", "Beispiel", date(2026, 10, 12), "waiting", "therapie1"),
            ("Leon", "Muster", date(2026, 9, 18), "active", "therapie2"),
            ("Mia", "Demo", date(2026, 8, 25), "closed", "therapie1"),
        ]
        for first, last, day, status, therapist in cases:
            child = Child.objects.create(first_name=first, last_name=last)
            guardian = shared_guardian if first in ("Emma", "Mia") else Guardian.objects.create(full_name="Pat Demo")
            ChildGuardian.objects.create(child=child, guardian=guardian)
            case = CareCase.objects.create(child=child, requested_on=day, status=status,
                                           started_on=(date(2026, 9, 25) if status != "waiting" else None),
                                           ended_on=(date(2026, 10, 30) if status == "closed" else None))
            case.assigned_therapists.add(members[therapist])
            AuditEvent.objects.create(case=case, actor=members["leitung"], action="seed", to_status=status)
        self.stdout.write(self.style.SUCCESS("Fictional PoC demo data created."))
