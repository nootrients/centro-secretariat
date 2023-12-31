# Generated by Django 4.2.5 on 2023-11-10 14:50

import application.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0018_alter_applications_applying_for_academic_year_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="applications",
            name="course_duration",
            field=models.CharField(
                choices=[
                    ("THREE YEARS", "THREE (3) YEARS"),
                    ("FOUR YEARS", "FOUR (4) YEARS"),
                    ("FIVE YEARS", "FIVE (5) YEARS"),
                ],
                max_length=15,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="applications",
            name="course_taking",
            field=models.ForeignKey(
                max_length=50,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="application.courses",
            ),
        ),
        migrations.AddField(
            model_name="applications",
            name="is_graduating",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="applications",
            name="is_ladderized",
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name="applications",
            name="registration_form",
            field=models.FileField(
                help_text="Insert your Registration/Enrollment Form for the current semester.",
                null=True,
                upload_to="applicant/registration_form",
            ),
        ),
        migrations.AddField(
            model_name="applications",
            name="total_units_enrolled",
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="applications",
            name="university_attending",
            field=models.ForeignKey(
                max_length=40,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="application.partnereduniversities",
            ),
        ),
        migrations.AddField(
            model_name="applications",
            name="year_level",
            field=models.CharField(
                choices=[
                    ("FIRST YEAR", "FIRST YEAR"),
                    ("SECOND YEAR", "SECOND YEAR"),
                    ("THIRD YEAR", "THIRD YEAR"),
                    ("FOURTH YEAR", "FOURTH YEAR"),
                    ("FIFTH YEAR", "FIFTH YEAR"),
                ],
                max_length=15,
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
            name="academic_year",
            field=application.models.AcademicYearField(
                default=application.models.AcademicYearField.calculate_academic_year,
                editable=False,
                max_length=9,
            ),
        ),
    ]
