# Generated by Django 4.2.5 on 2023-10-12 10:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0013_userprofile_remove_scholar_applicant_and_more"),
        ("demographics", "0012_remove_applicant_age"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Applicant",
        ),
    ]
