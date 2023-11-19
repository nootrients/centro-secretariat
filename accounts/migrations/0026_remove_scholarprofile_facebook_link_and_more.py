# Generated by Django 4.2.5 on 2023-11-17 06:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0025_alter_userprofile_gender"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="scholarprofile",
            name="facebook_link",
        ),
        migrations.RemoveField(
            model_name="scholarprofile",
            name="is_archived",
        ),
        migrations.RemoveField(
            model_name="scholarprofile",
            name="religion",
        ),
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Admin"),
                    ("HEAD", "Head Officer"),
                    ("OFFICER", "Officer"),
                    ("SCHOLAR", "Scholar"),
                ],
                default="SCHOLAR",
                max_length=20,
            ),
        ),
    ]
