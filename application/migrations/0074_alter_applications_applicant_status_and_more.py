# Generated by Django 4.2.5 on 2024-01-13 02:35

import application.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0073_alter_applications_applicant_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applications",
            name="applicant_status",
            field=models.CharField(
                choices=[
                    ("NEW APPLICANT", "NEW APPLICANT"),
                    ("RENEWING APPLICANT", "RENEWING APPLICANT"),
                ],
                default="NEW APPLICANT",
                max_length=18,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="application_reference_id",
            field=models.CharField(max_length=20, null=True),
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
            model_name="applications",
            name="barangay",
            field=models.CharField(
                choices=[
                    ("BAGUMBAYAN", "Bagumbayan"),
                    ("BAMBANG", "Bambang"),
                    ("CALZADA", "Calzada"),
                    ("HAGONOY", "Hagonoy"),
                    ("IBAYO TIPAS", "Ibayo Tipas"),
                    ("LIGID TIPAS", "Ligid Tipas"),
                    ("LOWER BICUTAN", "Lower Bicutan"),
                    ("NEW LOWER BICUTAN", "New Lower Bicutan"),
                    ("NAPINDAN", "Napindan"),
                    ("PALINGON", "Palingon"),
                    ("SAN MIGUEL", "San Miguel"),
                    ("SANTA ANA", "Santa Ana"),
                    ("TUKTUKAN", "Tuktukan"),
                    ("USUSAN", "Ususan"),
                    ("WAWA", "Wawa"),
                    ("BAGONG TANYAG", "Bagong Tanyag"),
                    ("CENTRAL BICUTAN", "Central Bicutan"),
                    ("CENTRAL SIGNAL VILLAGE", "Central Signal Village"),
                    ("FORT BONIFACIO", "Fort Bonifacio"),
                    ("KATUPARAN", "Katuparan"),
                    ("MAHARLIKA VILLAGE", "Maharlika Village"),
                    ("NORTH DAANG_HARI", "North Daang Hari"),
                    ("NORTH SIGNAL VILLAGE", "North Signal Village"),
                    ("PINAGSAMA", "Pinagsama"),
                    ("SOUTH DAANG HARI", "South Daang Hari"),
                    ("SOUTH SIGNAL VILLAGE", "South Signal Village"),
                    ("UPPER BICUTAN", "Upper Bicutan"),
                    ("WESTERN BICUTAN", "Western Bicutan"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
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
        migrations.AlterField(
            model_name="applications",
            name="course_taking",
            field=models.ForeignKey(
                max_length=50,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="application.courses",
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="elementary_school",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="elementary_start_end",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="firstname",
            field=models.CharField(
                blank=True,
                default="Unable to extract from image.",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardian_complete_address",
            field=models.TextField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardian_complete_name",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardian_contact_number",
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardian_educational_attainment",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardian_occupation",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardian_place_of_work",
            field=models.TextField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardians_voters_issuance_date",
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardians_voters_issued_at",
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="guardians_years_of_residency",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="house_address",
            field=models.TextField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="jhs_school",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="jhs_start_end",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="lastname",
            field=models.CharField(
                blank=True,
                default="Unable to extract from image.",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="middlename",
            field=models.CharField(
                blank=True,
                default="Unable to extract from image.",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="personalized_facebook_link",
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="religion",
            field=models.CharField(
                choices=[
                    ("ROMAN CATHOLIC", "ROMAN CATHOLIC"),
                    ("PROTESTANT", "PROTESTANT"),
                    ("BAPTIST", "BAPTIST"),
                    ("IGLESIA NI CRISTO", "IGLESIA NI CRISTO"),
                    ("ISLAM", "ISLAM"),
                    ("EVANGELICAL CHRISTIAN", "EVANGELICAL CHRISTIAN"),
                ],
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="scholarship_type",
            field=models.CharField(
                choices=[
                    ("BASIC PLUS SUC", "BASIC PLUS SUC"),
                    ("SUC_LCU", "SUC/LCU"),
                    ("BASIC SCHOLARSHIP", "BASIC SCHOLARSHIP"),
                    ("HONORS", "HONORS (FULL)"),
                    ("PRIORITY", "PRIORITY"),
                    ("PREMIER", "PREMIER"),
                ],
                default="BASIC SCHOLARSHIP",
                help_text="Kindly refer to the guidelines. Fraudulent inputs will deem your application as void.",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="semester",
            field=models.CharField(
                choices=[
                    ("FIRST SEMESTER", "FIRST SEMESTER"),
                    ("SECOND SEMESTER", "SECOND SEMESTER"),
                ],
                default="FIRST SEMESTER",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="shiftee",
            field=models.CharField(
                default="N/A",
                help_text="Title of your previous course (if shiftee).",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="shs_school",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="shs_start_end",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="transferee",
            field=models.CharField(
                default="N/A",
                help_text="Name of your previous school/university.",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="university_attending",
            field=models.ForeignKey(
                max_length=40,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="application.partnereduniversities",
            ),
        ),
        migrations.AlterField(
            model_name="applications",
            name="voters_issuance_date",
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name="applications",
            name="voters_issued_at",
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
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
            name="years_of_residency",
            field=models.CharField(max_length=30, null=True),
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
            name="applicant_status",
            field=models.CharField(
                choices=[
                    ("NEW APPLICANT", "NEW APPLICANT"),
                    ("RENEWING APPLICANT", "RENEWING APPLICANT"),
                ],
                default="NEW APPLICANT",
                max_length=18,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="application_reference_id",
            field=models.CharField(max_length=20, null=True),
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
            name="barangay",
            field=models.CharField(
                choices=[
                    ("BAGUMBAYAN", "Bagumbayan"),
                    ("BAMBANG", "Bambang"),
                    ("CALZADA", "Calzada"),
                    ("HAGONOY", "Hagonoy"),
                    ("IBAYO TIPAS", "Ibayo Tipas"),
                    ("LIGID TIPAS", "Ligid Tipas"),
                    ("LOWER BICUTAN", "Lower Bicutan"),
                    ("NEW LOWER BICUTAN", "New Lower Bicutan"),
                    ("NAPINDAN", "Napindan"),
                    ("PALINGON", "Palingon"),
                    ("SAN MIGUEL", "San Miguel"),
                    ("SANTA ANA", "Santa Ana"),
                    ("TUKTUKAN", "Tuktukan"),
                    ("USUSAN", "Ususan"),
                    ("WAWA", "Wawa"),
                    ("BAGONG TANYAG", "Bagong Tanyag"),
                    ("CENTRAL BICUTAN", "Central Bicutan"),
                    ("CENTRAL SIGNAL VILLAGE", "Central Signal Village"),
                    ("FORT BONIFACIO", "Fort Bonifacio"),
                    ("KATUPARAN", "Katuparan"),
                    ("MAHARLIKA VILLAGE", "Maharlika Village"),
                    ("NORTH DAANG_HARI", "North Daang Hari"),
                    ("NORTH SIGNAL VILLAGE", "North Signal Village"),
                    ("PINAGSAMA", "Pinagsama"),
                    ("SOUTH DAANG HARI", "South Daang Hari"),
                    ("SOUTH SIGNAL VILLAGE", "South Signal Village"),
                    ("UPPER BICUTAN", "Upper Bicutan"),
                    ("WESTERN BICUTAN", "Western Bicutan"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
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
        migrations.AlterField(
            model_name="tempapplications",
            name="course_taking",
            field=models.ForeignKey(
                max_length=50,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="application.courses",
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="elementary_school",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="elementary_start_end",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="firstname",
            field=models.CharField(
                blank=True,
                default="Unable to extract from image.",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardian_complete_address",
            field=models.TextField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardian_complete_name",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardian_contact_number",
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardian_educational_attainment",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardian_occupation",
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="guardian_place_of_work",
            field=models.TextField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="house_address",
            field=models.TextField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="jhs_school",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="jhs_start_end",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="lastname",
            field=models.CharField(
                blank=True,
                default="Unable to extract from image.",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="middlename",
            field=models.CharField(
                blank=True,
                default="Unable to extract from image.",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="religion",
            field=models.CharField(
                choices=[
                    ("ROMAN CATHOLIC", "ROMAN CATHOLIC"),
                    ("PROTESTANT", "PROTESTANT"),
                    ("BAPTIST", "BAPTIST"),
                    ("IGLESIA NI CRISTO", "IGLESIA NI CRISTO"),
                    ("ISLAM", "ISLAM"),
                    ("EVANGELICAL CHRISTIAN", "EVANGELICAL CHRISTIAN"),
                ],
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="scholarship_type",
            field=models.CharField(
                choices=[
                    ("BASIC PLUS SUC", "BASIC PLUS SUC"),
                    ("SUC_LCU", "SUC/LCU"),
                    ("BASIC SCHOLARSHIP", "BASIC SCHOLARSHIP"),
                    ("HONORS", "HONORS (FULL)"),
                    ("PRIORITY", "PRIORITY"),
                    ("PREMIER", "PREMIER"),
                ],
                default="BASIC SCHOLARSHIP",
                help_text="Kindly refer to the guidelines. Fraudulent inputs will deem your application as void.",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="semester",
            field=models.CharField(
                choices=[
                    ("FIRST SEMESTER", "FIRST SEMESTER"),
                    ("SECOND SEMESTER", "SECOND SEMESTER"),
                ],
                default="FIRST SEMESTER",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="shiftee",
            field=models.CharField(
                default="N/A",
                help_text="Title of your previous course (if shiftee).",
                max_length=30,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="shs_school",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="shs_start_end",
            field=models.CharField(max_length=9, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="student_status",
            field=models.CharField(
                choices=[
                    ("REGULAR", "REGULAR"),
                    ("IRREGULAR", "IRREGULAR"),
                    ("OCTOBERIAN", "OCTOBERIAN"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="transferee",
            field=models.CharField(
                default="N/A",
                help_text="Name of your previous school/university.",
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="university_attending",
            field=models.ForeignKey(
                max_length=40,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="application.partnereduniversities",
            ),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="voters_issuance_date",
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
            name="voters_issued_at",
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name="tempapplications",
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
            model_name="tempapplications",
            name="years_of_residency",
            field=models.CharField(max_length=30, null=True),
        ),
    ]
