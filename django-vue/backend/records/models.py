from django.conf import settings
from django.db import models


class Child(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Guardian(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.full_name


class ChildGuardian(models.Model):
    child = models.ForeignKey(Child, on_delete=models.PROTECT, related_name="guardian_links")
    guardian = models.ForeignKey(Guardian, on_delete=models.PROTECT, related_name="child_links")
    relation = models.CharField(max_length=50, default="Sorgeberechtigt")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["child", "guardian"], name="unique_child_guardian")]


class CareCase(models.Model):
    WAITING, ACTIVE, CLOSED = "waiting", "active", "closed"
    STATUSES = [(WAITING, "Wartend"), (ACTIVE, "Aktiv"), (CLOSED, "Abgeschlossen")]
    child = models.ForeignKey(Child, on_delete=models.PROTECT, related_name="cases")
    status = models.CharField(max_length=10, choices=STATUSES, default=WAITING)
    requested_on = models.DateField()
    started_on = models.DateField(null=True, blank=True)
    ended_on = models.DateField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    assigned_therapists = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="assigned_care_cases")

    class Meta:
        ordering = ["-requested_on", "-pk"]


class AuditEvent(models.Model):
    case = models.ForeignKey(CareCase, on_delete=models.PROTECT, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=30)
    from_status = models.CharField(max_length=10, blank=True)
    to_status = models.CharField(max_length=10, blank=True)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-at", "-pk"]
