from django.db import migrations
from django.contrib.auth.hashers import make_password


FACULTY_SEED = [
    ("74f063fb-a855-44da-b9a1-5c316b1f192a", "EMP101"),
    ("adefc763-9c36-403e-acce-8c75a4bc162b", "EMP102"),
    ("6c4a1368-a21a-4417-ae2c-bf57db250229", "EMP103"),
    ("3faf9fcd-99d3-400d-851f-9df07516c7fc", "EMP104"),
    ("6361d0c0-2abf-43db-977e-37bdab092b23", "EMP105"),
    ("37242ea1-6e7c-4246-94c0-7d0fb6e275ec", "EMP106"),
]

HOLIDAYS = [
    ("2026-10-02", "Gandhi Jayanti"),
    ("2026-12-25", "Christmas"),
]


def seed_faculty_attendance_data(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        default_pw = make_password("12345")
        for (uid, emp_code) in FACULTY_SEED:
            cursor.execute(
                "UPDATE adminauth_useradmin "
                "SET employee_code = %s, designation = 4, \"updatedAt\" = now() "
                "WHERE id = %s AND \"isActive\" = true",
                [emp_code, uid])
            cursor.execute(
                "UPDATE adminauth_useradmin SET password = %s "
                "WHERE id = %s AND (password IS NULL OR password = '')",
                [default_pw, uid])
        for (hdate, hname) in HOLIDAYS:
            cursor.execute(
                "INSERT INTO attendance_holiday (holiday_date, name, \"createdAt\", \"isActive\") "
                "SELECT %s, %s, now(), true "
                "WHERE NOT EXISTS (SELECT 1 FROM attendance_holiday WHERE holiday_date = %s)",
                [hdate, hname, hdate])


def unseed_faculty_attendance_data(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        for (uid, _) in FACULTY_SEED:
            cursor.execute(
                "UPDATE adminauth_useradmin "
                "SET employee_code = NULL, designation = NULL, \"updatedAt\" = now() WHERE id = %s",
                [uid])
        for (hdate, _) in HOLIDAYS:
            cursor.execute("DELETE FROM attendance_holiday WHERE holiday_date = %s", [hdate])


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_faculty_attendance_fields'),
    ]

    operations = [
        migrations.RunPython(seed_faculty_attendance_data, unseed_faculty_attendance_data),
    ]