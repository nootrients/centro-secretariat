# Generated by Django 4.2.5 on 2023-10-09 09:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("demographics", "0009_applicant_testfield"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="applicant",
            name="testField",
        ),
    ]
