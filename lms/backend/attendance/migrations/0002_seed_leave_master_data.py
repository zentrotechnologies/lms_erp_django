from django.db import migrations


LEAVE_TYPES = [
    (2, 'Emergency Leave', 'Days', ''),
    (4, 'Sick Leave', 'Days', ''),
    (7, 'Paid Leave', 'Days', ''),
    (9, 'Casual Leave', 'Days', ''),
]

ALLOTMENTS = [
    (7, 2, 3, 2, 20.50, 0.00),
    (9, 4, 3, 2, 10.00, 0.00),
    (6, 7, 3, 2, 20.50, 8.00),
    (8, 9, 3, 2, 0.00, 0.00),
]

DEMO_USERS = [
    ("74f063fb-a855-44da-b9a1-5c316b1f192a", "Rohit Sharma", "rohit@lms.com",
     "pbkdf2_sha256$870000$SYnhBxu7eyObHRrGWUHIXc$J5BkA6YzbAv00DZkNkPBRuqTsOKhe94pjDt3ZlWPRWg=", None, None, 5, None, "306e6a17-14e8-405e-af3b-5c4edca18ed3", False),
    ("adefc763-9c36-403e-acce-8c75a4bc162b", "Sapana Jain", "sapana@lms.com",
     "", None, None, 5, None, "306e6a17-14e8-405e-af3b-5c4edca18ed3", False),
    ("6c4a1368-a21a-4417-ae2c-bf57db250229", "Rahul Verma", "rahul@lms.com",
     "", None, None, 5, None, "306e6a17-14e8-405e-af3b-5c4edca18ed3", False),
    ("3faf9fcd-99d3-400d-851f-9df07516c7fc", "Anita Kulkarni", "anita@lms.com",
     "", None, None, 5, None, "306e6a17-14e8-405e-af3b-5c4edca18ed3", False),
    ("6361d0c0-2abf-43db-977e-37bdab092b23", "Deepak Pawar", "deepak@lms.com",
     "", None, None, 5, None, "306e6a17-14e8-405e-af3b-5c4edca18ed3", False),
    ("37242ea1-6e7c-4246-94c0-7d0fb6e275ec", "Teacher Member", "faculty2@lms.com",
     "pbkdf2_sha256$870000$azeIl23I1rBeaBZdKgAipF$57393cJgwdFCvxkf304SDOPMLdKBZEvtQ8cwHfbcVuA=", 5, "hr", 5, None, None, False),
    ("306e6a17-14e8-405e-af3b-5c4edca18ed3", "Sonya Taylor", "sonyataylor231@gmail.com",
     "pbkdf2_sha256$870000$ML9wmpQMT9QcpIoCUVm4cy$U+rzl1R/k/g0l5qrgiYh6aPsdDWVFVypKtjcLQyZEp8=", 1, None, 1, 3, None, True),
]

TEMPLATES = [
    (7, 2, 2, "Demo Class Timetable A", "2026-06-01", "2026-12-31", 't', 't'),
    (8, 2, 1, "Demo Class Timetable B", "2026-06-01", "2026-12-31", 't', 't'),
]

SLOTS = [
    (9, 7, 0, 3, "09:00", "10:00", 3, "74f063fb-a855-44da-b9a1-5c316b1f192a"),
    (10, 7, 2, 5, "01:00", "02:00", 6, "74f063fb-a855-44da-b9a1-5c316b1f192a"),
    (11, 7, 3, 3, "10:00", "11:00", 4, "74f063fb-a855-44da-b9a1-5c316b1f192a"),
    (12, 7, 3, 4, "11:00", "12:00", 2, "74f063fb-a855-44da-b9a1-5c316b1f192a"),
    (13, 7, 4, 6, "03:00", "04:00", 5, "74f063fb-a855-44da-b9a1-5c316b1f192a"),
    (14, 8, 0, 3, "09:00", "10:00", 4, "adefc763-9c36-403e-acce-8c75a4bc162b"),
    (15, 8, 3, 3, "10:00", "11:00", 6, "6c4a1368-a21a-4417-ae2c-bf57db250229"),
    (16, 8, 2, 5, "01:00", "02:00", 2, "3faf9fcd-99d3-400d-851f-9df07516c7fc"),
    (17, 8, 4, 6, "03:00", "04:00", 4, "adefc763-9c36-403e-acce-8c75a4bc162b"),
]


def seed_leave_data(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for (pk, name, units, desc) in LEAVE_TYPES:
            cursor.execute(
                "INSERT INTO attendance_leave_type (id, leave_type_name, units, description, \"isActive\") "
                "SELECT %s, %s, %s, %s, true "
                "WHERE NOT EXISTS (SELECT 1 FROM attendance_leave_type WHERE leave_type_name = %s)",
                [pk, name, units, desc, name])

        for (pk, type_id, desig_id, acad_id, allowed, opening) in ALLOTMENTS:
            cursor.execute(
                "INSERT INTO attendance_leave_type_allotment "
                "(id, leave_type_id, designation_id, academic_year_id, allowed, opening_balance, \"isActive\") "
                "SELECT %s, %s, %s, %s, %s, %s, true "
                "WHERE NOT EXISTS (SELECT 1 FROM attendance_leave_type_allotment "
                "WHERE leave_type_id = %s AND designation_id = %s AND academic_year_id = %s)",
                [pk, type_id, desig_id, acad_id, allowed, opening, type_id, desig_id, acad_id])

        for (uid, name, email, pwd, role, role_code, user_type, designation, reporting_to, status) in DEMO_USERS:
            cursor.execute(
                "INSERT INTO adminauth_useradmin "
                "(id, name, email, password, role, role_code, user_type, designation, reporting_to, status, \"isActive\") "
                "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true "
                "WHERE NOT EXISTS (SELECT 1 FROM adminauth_useradmin WHERE email = %s)",
                [uid, name, email, pwd, role, role_code, user_type, designation, reporting_to, status, email])

        for (tid, acad_id, class_group_id, tname, eff_from, eff_to, pub, act) in TEMPLATES:
            cursor.execute(
                "INSERT INTO schedule_timetabletemplate "
                "(id, academic_year_id, class_group_id, template_name, effective_from, effective_to, "
                "is_published, is_active, created_by, \"isActive\") "
                "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, true "
                "WHERE NOT EXISTS (SELECT 1 FROM schedule_timetabletemplate WHERE id = %s)",
                [tid, acad_id, class_group_id, tname, eff_from, eff_to, pub, act,
                 "74f063fb-a855-44da-b9a1-5c316b1f192a", tid])

        for (sid, tid, dow, period, st, et, course_id, fac_id) in SLOTS:
            cursor.execute(
                "INSERT INTO schedule_timetableslot "
                "(id, timetable_template_id, day_of_week, period_number, start_time, end_time, "
                "course_id, faculty_id, room_number, is_active, \"isActive\") "
                "SELECT %s, %s, %s, %s, %s, %s, %s, %s, NULL, true, true "
                "WHERE NOT EXISTS (SELECT 1 FROM schedule_timetableslot WHERE id = %s)",
                [sid, tid, dow, period, st, et, course_id, fac_id, sid])

        cursor.execute(
            "UPDATE adminauth_useradmin SET role_code = 'hr' WHERE email = 'faculty2@lms.com' "
            "AND NOT (role_code = 'hr')")


def unseed_leave_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        ('adminauth', '0001_initial'),
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_leave_data, unseed_leave_data),
    ]