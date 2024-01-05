# Generated by Django 4.2.5 on 2024-01-05 14:43

import application.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0071_alter_applications_applying_for_academic_year_and_more"),
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
            model_name="applications",
            name="guardians_voters_issuance_date",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardians_voters_issued_at",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardians_years_of_residency",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="voters_issuance_date",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="voters_issued_at",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="years_of_residency",
            field=models.CharField(max_length=100, null=True),
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
        migrations.AlterField(
            model_name="tempapplications",
            name="guardians_voters_issuance_date",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardians_voters_issued_at",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardians_years_of_residency",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="voters_issuance_date",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="voters_issued_at",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="years_of_residency",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
