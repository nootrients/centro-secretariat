# Generated by Django 4.2.5 on 2023-11-07 06:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0012_alter_applications_guardian_complete_address_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="applications",
            name="academic_year",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="course_duration",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="course_taking",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="elementary_school",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="elementary_school_address",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="elementary_school_type",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="elementary_start_end",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardian_complete_address",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardian_complete_name",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardian_contact_number",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardian_educational_attainment",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardian_occupation",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardian_place_of_work",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="guardians_voter_certificate",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="informative_copy_of_grades",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="is_applying_for_merit",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="is_graduating",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="is_ladderized",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="jhs_school",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="jhs_school_address",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="jhs_school_type",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="jhs_start_end",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="number_of_semesters_before_graduating",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="registration_form",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="semester",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="shiftee",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="shs_school",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="shs_school_address",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="shs_school_type",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="shs_start_end",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="student_status",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="total_units_enrolled",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="transferee",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="university_attending",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="voter_certificate",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="year_level",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="years_of_residency",
        ),
    ]
