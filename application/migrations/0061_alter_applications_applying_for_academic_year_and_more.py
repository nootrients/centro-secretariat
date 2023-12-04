# Generated by Django 4.2.5 on 2023-12-02 05:51

import application.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0029_alter_scholarprofile_scholarship_type"),
        ("application", "0060_alter_applications_applying_for_academic_year_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applications",
            name="applying_for_academic_year",
            field=application.models.AcademicYearField(
                default=application.models.AcademicYearField.calculate_academic_year,
                editable=False,
                max_length=9,
            ),
        ),
        migrations.AlterField(
            model_name="eligibilityconfig",
            name="applying_for_academic_year",
            field=application.models.AcademicYearField(
                default=application.models.AcademicYearField.calculate_academic_year,
                editable=False,
                max_length=9,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="applying_for_academic_year",
            field=application.models.AcademicYearField(
                default=application.models.AcademicYearField.calculate_academic_year,
                editable=False,
                max_length=9,
            ),
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action_type",
                    models.CharField(
                        choices=[("accepted", "Accepted"), ("rejected", "Rejected")],
                        max_length=20,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "application_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="application.applications",
                    ),
                ),
                (
                    "officer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.officer",
                    ),
                ),
            ],
        ),
    ]