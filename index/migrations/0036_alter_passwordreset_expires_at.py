# Generated by Django 4.2.5 on 2024-01-05 14:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("index", "0035_alter_passwordreset_expires_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passwordreset",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 1, 5, 15, 15, 26, 345795, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
