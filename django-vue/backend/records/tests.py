import json
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from .models import Child, CareCase, AuditEvent


class AccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.manager = User.objects.create_user(username="office", password="SafeDemoTest1!")
        cls.therapist = User.objects.create_user(username="thera", password="SafeDemoTest1!")
        cls.stranger = User.objects.create_user(username="stranger", password="SafeDemoTest1!")
        cls.leader = User.objects.create_user(username="leader", password="SafeDemoTest1!")
        for user, role in ((cls.manager, "Verwaltung"), (cls.therapist, "Therapie"),
                           (cls.stranger, "Therapie"), (cls.leader, "Leitung")):
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)
        cls.case = CareCase.objects.create(child=Child.objects.create(first_name="Test", last_name="Kind"),
                                           requested_on=date(2026, 10, 1))
        cls.case.assigned_therapists.add(cls.therapist)

    def post_json(self, url, data=None):
        return self.client.post(url, data=json.dumps(data or {}), content_type="application/json")

    def test_anonymous_cannot_list(self):
        self.assertNotEqual(self.client.get("/api/cases/").status_code, 200)

    def test_only_assigned_therapist_can_see_case(self):
        self.client.force_login(self.therapist)
        self.assertEqual(len(self.client.get("/api/cases/?status=all").json()["cases"]), 1)
        self.client.force_login(self.stranger)
        self.assertEqual(len(self.client.get("/api/cases/?status=all").json()["cases"]), 0)
        self.assertEqual(self.client.get(f"/api/cases/{self.case.pk}/").status_code, 404)

    def test_therapist_cannot_change_status_even_with_direct_post(self):
        self.client.force_login(self.therapist)
        res = self.post_json(f"/api/cases/{self.case.pk}/transition/", {"to": "active", "effectiveOn": "2026-10-02"})
        self.assertEqual(res.status_code, 403)
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, "waiting")

    def test_status_transition_requires_date_and_audits(self):
        self.client.force_login(self.manager)
        path = f"/api/cases/{self.case.pk}/transition/"
        self.assertEqual(self.post_json(path, {"to": "active"}).status_code, 400)
        self.assertEqual(self.post_json(path, {"to": "active", "effectiveOn": "2026-10-02"}).status_code, 200)
        self.assertTrue(AuditEvent.objects.filter(case=self.case, action="status", actor=self.manager).exists())
        self.assertEqual(self.post_json(path, {"to": "closed", "effectiveOn": "2026-09-01"}).status_code, 400)

    def test_trash_leader_only(self):
        self.client.force_login(self.manager)
        self.assertEqual(self.post_json(f"/api/cases/{self.case.pk}/trash/").status_code, 403)
        self.client.force_login(self.leader)
        self.assertEqual(self.post_json(f"/api/cases/{self.case.pk}/trash/").status_code, 200)
        self.assertEqual(self.client.get("/api/cases/?status=all").json()["cases"], [])
        self.assertEqual(self.post_json(f"/api/cases/{self.case.pk}/restore/").status_code, 200)
        self.assertEqual(len(self.client.get("/api/cases/?status=all").json()["cases"]), 1)
