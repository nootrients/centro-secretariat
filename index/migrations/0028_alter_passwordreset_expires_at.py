# Generated by Django 4.2.5 on 2023-12-02 10:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("index", "0027_alter_passwordreset_expires_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passwordreset",
            name="expires_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 12, 2, 11, 51, 43, 561686, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
