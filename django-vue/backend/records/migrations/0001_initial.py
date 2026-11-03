from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Child", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("first_name", models.CharField(max_length=100)),
            ("last_name", models.CharField(max_length=100)),
            ("birth_date", models.DateField(blank=True, null=True)),
        ]),
        migrations.CreateModel(name="Guardian", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("full_name", models.CharField(max_length=200)),
            ("phone", models.CharField(blank=True, max_length=80)),
        ]),
        migrations.CreateModel(name="ChildGuardian", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("relation", models.CharField(default="Sorgeberechtigt", max_length=50)),
            ("child", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="guardian_links", to="records.child")),
            ("guardian", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="child_links", to="records.guardian")),
        ], options={"constraints": [models.UniqueConstraint(fields=("child", "guardian"), name="unique_child_guardian")]}),
        migrations.CreateModel(name="CareCase", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("status", models.CharField(choices=[("waiting", "Wartend"), ("active", "Aktiv"), ("closed", "Abgeschlossen")], default="waiting", max_length=10)),
            ("requested_on", models.DateField()),
            ("started_on", models.DateField(blank=True, null=True)),
            ("ended_on", models.DateField(blank=True, null=True)),
            ("deleted_at", models.DateTimeField(blank=True, null=True)),
            ("child", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="cases", to="records.child")),
            ("assigned_therapists", models.ManyToManyField(blank=True, related_name="assigned_care_cases", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ["-requested_on", "-pk"]}),
        migrations.CreateModel(name="AuditEvent", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False)),
            ("action", models.CharField(max_length=30)),
            ("from_status", models.CharField(blank=True, max_length=10)),
            ("to_status", models.CharField(blank=True, max_length=10)),
            ("at", models.DateTimeField(auto_now_add=True)),
            ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ("case", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="events", to="records.carecase")),
        ], options={"ordering": ["-at", "-pk"]}),
    ]
