# Generated by Django 4.2.5 on 2023-11-24 15:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("index", "0019_alter_passwordreset_expires_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passwordreset",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 11, 24, 16, 1, 27, 511408, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
