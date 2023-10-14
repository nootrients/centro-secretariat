# Generated by Django 4.2.5 on 2023-10-08 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("demographics", "0002_alter_applicant_gender"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicant",
            name="gender",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                to="demographics.gender",
            ),
        ),
    ]
