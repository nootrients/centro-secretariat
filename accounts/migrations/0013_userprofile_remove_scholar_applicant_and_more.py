# Generated by Django 4.2.5 on 2023-10-12 10:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("demographics", "0012_remove_applicant_age"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("accounts", "0012_customuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("firstname", models.CharField(max_length=30)),
                ("lastname", models.CharField(max_length=30)),
                ("middlename", models.CharField(max_length=30)),
                ("contactnumber", models.CharField(max_length=13)),
                ("house_address", models.CharField(max_length=50)),
                ("barangay", models.CharField(max_length=30)),
                ("district", models.PositiveSmallIntegerField(null=True)),
                (
                    "gender",
                    models.ForeignKey(
                        default=3,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="demographics.gender",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="scholar",
            name="applicant",
        ),
        migrations.RemoveField(
            model_name="scholar",
            name="groups",
        ),
        migrations.RemoveField(
            model_name="scholar",
            name="role",
        ),
        migrations.RemoveField(
            model_name="scholar",
            name="scholarship_type",
        ),
        migrations.RemoveField(
            model_name="scholar",
            name="user_permissions",
        ),
        migrations.CreateModel(
            name="Head",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("accounts.customuser",),
        ),
        migrations.AlterModelOptions(
            name="customuser",
            options={},
        ),
        migrations.AlterModelManagers(
            name="customuser",
            managers=[],
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="is_staff",
        ),
        migrations.RemoveField(
            model_name="customuser",
            name="last_name",
        ),
        migrations.AddField(
            model_name="customuser",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="date_joined",
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="email address"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_active",
            field=models.BooleanField(default=True),
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
                default="ADMIN",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(
                blank=True, max_length=12, unique=True, verbose_name="username"
            ),
        ),
        migrations.CreateModel(
            name="HeadProfile",
            fields=[
                (
                    "userprofile_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="accounts.userprofile",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=("accounts.userprofile",),
        ),
        migrations.CreateModel(
            name="OfficerProfile",
            fields=[
                (
                    "userprofile_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="accounts.userprofile",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=("accounts.userprofile",),
        ),
        migrations.CreateModel(
            name="ScholarProfile",
            fields=[
                (
                    "userprofile_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="accounts.userprofile",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            bases=("accounts.userprofile",),
        ),
        migrations.DeleteModel(
            name="Officer",
        ),
        migrations.DeleteModel(
            name="Role",
        ),
        migrations.DeleteModel(
            name="Scholar",
        ),
        migrations.CreateModel(
            name="Officer",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("accounts.customuser",),
        ),
        migrations.CreateModel(
            name="Scholar",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("accounts.customuser",),
        ),
    ]
