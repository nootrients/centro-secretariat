# Generated by Django 4.2.5 on 2023-10-12 11:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0013_userprofile_remove_scholar_applicant_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
    ]
