# Generated by Django 4.2.5 on 2023-12-06 08:49

import application.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0067_alter_applications_applying_for_academic_year_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applications",
            name="application_status",
            field=models.CharField(
                choices=[
                    ("UNPROCESSED", "UNPROCESSED"),
                    ("PENDING", "PENDING"),
                    ("ACCEPTED", "ACCEPTED"),
                    ("REJECTED", "REJECTED"),
                ],
                default="PENDING",
                max_length=50,
                null=True,
            ),
        ),
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
    ]
