# Generated by Django 4.2.5 on 2023-11-26 11:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("index", "0021_alter_passwordreset_expires_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passwordreset",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 11, 26, 12, 20, 13, 957598, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
