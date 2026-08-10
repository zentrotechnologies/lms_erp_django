from django.db import migrations


def seed_roles(apps, schema_editor):
    Roles = apps.get_model("usermanagement", "Roles")
    roles = [
        {
            "role_code": "admin",
            "role_name": "Admin",
            "description": "College/system administrator with full management access.",
            "is_active": True,
        },
        {
            "role_code": "parent",
            "role_name": "Parent",
            "description": "Parent or guardian linked to one or more students.",
            "is_active": True,
        },
        {
            "role_code": "student",
            "role_name": "Student",
            "description": "Student enrolled in a program/class.",
            "is_active": True,
        },
        {
            "role_code": "faculty",
            "role_name": "Faculty",
            "description": "Faculty member (HOD/Teacher/Staff) of the college.",
            "is_active": True,
        },
    ]
    for role in roles:
        Roles.objects.update_or_create(
            role_code=role["role_code"],
            defaults=role,
        )


def unseed_roles(apps, schema_editor):
    Roles = apps.get_model("usermanagement", "Roles")
    Roles.objects.filter(
        role_code__in=["admin", "parent", "student", "faculty"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usermanagement', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
