# Generated by Django 4.2.5 on 2023-10-24 13:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "application",
            "0002_courses_eligibilityconfig_partnereduniversities_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="applications",
            name="is_archived",
        ),
        migrations.RemoveField(
            model_name="applications",
            name="is_graduated",
        ),
        migrations.AlterField(
            model_name="partnereduniversities",
            name="university_name",
            field=models.CharField(max_length=100),
        ),
    ]