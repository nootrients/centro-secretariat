# Generated by Django 4.2.5 on 2023-10-27 08:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0007_eligibilityconfig_academic_year_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="eligibilityconfig",
            old_name="voters_issuance_year",
            new_name="voters_validity_year_start",
        ),
        migrations.AddField(
            model_name="eligibilityconfig",
            name="voters_validity_year_end",
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
