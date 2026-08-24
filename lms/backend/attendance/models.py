from django.db import models
from helpers.models import TrackingModel


class CandidateAttendance(TrackingModel):
    # Legacy attendance model retained for existing APIs/data.
    candidate_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    schedule_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    course_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    college_id = models.CharField(max_length=255, null=True, blank=True)
    faculty_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    attendance_date = models.DateField(null=True, blank=True, db_index=True)
    checkin_time = models.CharField(max_length=255, null=True, blank=True)
    checkout_time = models.CharField(max_length=255, null=True, blank=True)
    present = models.BooleanField(default=True)
    absent = models.BooleanField(default=False)


class LectureAttendanceSession(TrackingModel):
    lecture_entry_id = models.BigIntegerField(unique=True, db_index=True)
    academic_year_id = models.BigIntegerField(db_index=True)
    class_group_id = models.BigIntegerField(db_index=True)
    course_id = models.BigIntegerField(db_index=True)
    faculty_id = models.CharField(max_length=255, db_index=True)
    attendance_date = models.DateField(db_index=True,null=True, blank=True)
    total_students = models.PositiveIntegerField(default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    locked_by = models.CharField(max_length=255, null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)


class LectureAttendanceDetail(TrackingModel):
    attendance_session_id = models.BigIntegerField(db_index=True)
    student_id = models.CharField(max_length=255, db_index=True)
    attendance_status = models.CharField(max_length=20, db_index=True)
    marked_by = models.CharField(max_length=255)
    marked_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)




class FacultyAttendance(TrackingModel):
    faculty_id = models.CharField(max_length=255, db_index=True)
    attendance_date = models.DateField(db_index=True,null=True, blank=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    attendance_status = models.CharField(max_length=20, db_index=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)




class LeaveApplication(TrackingModel):
    applicant_type = models.CharField(max_length=20, db_index=True)
    applicant_id = models.CharField(max_length=255, db_index=True)
    leave_type = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    number_of_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, default="PENDING", db_index=True)
    reviewed_by = models.CharField(max_length=255, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_remarks = models.TextField(null=True, blank=True)
