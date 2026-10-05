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
    og_code = models.CharField(max_length=150, null=True, blank=True)


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
    og_code = models.CharField(max_length=150, null=True, blank=True)


class LectureAttendanceDetail(TrackingModel):
    attendance_session_id = models.BigIntegerField(db_index=True)
    student_id = models.CharField(max_length=255, db_index=True)
    attendance_status = models.CharField(max_length=20, db_index=True)
    marked_by = models.CharField(max_length=255)
    marked_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)



class FacultyAttendance(TrackingModel):
    faculty_id = models.CharField(max_length=255, db_index=True)
    attendance_date = models.DateField(db_index=True,null=True, blank=True)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_late = models.BooleanField(default=False)
    is_early = models.BooleanField(default=False)
    day_status = models.CharField(max_length=20, default='PRESENT', db_index=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    class Meta:
        unique_together = ('faculty_id', 'attendance_date')


class AttendanceHoliday(TrackingModel):
    holiday_date = models.DateField(unique=True, db_index=True)
    name = models.CharField(max_length=150)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    class Meta:
        db_table = 'attendance_holiday'
        ordering = ('holiday_date',)




class LeaveApplication(TrackingModel):
    applicant_type = models.CharField(max_length=20, db_index=True)
    applicant_id = models.CharField(max_length=255, db_index=True)
    leave_type = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    number_of_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    day_type = models.CharField(max_length=20, default="Full Day")
    document = models.CharField(max_length=500, null=True, blank=True)
    application_date = models.DateField(null=True, blank=True)
    hod_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    hr_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    admin_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, default="PENDING", db_index=True)
    approval_level = models.CharField(max_length=20, default="HOD")
    hod_status = models.CharField(max_length=20, default="PENDING")
    hr_status = models.CharField(max_length=20, default="PENDING")
    reviewed_by = models.CharField(max_length=255, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_remarks = models.TextField(null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)

class LeaveAdjacentLecture(TrackingModel):
    leave_application_id = models.CharField(max_length=255, db_index=True)
    lecture_date = models.DateField(db_index=True)
    period_number = models.PositiveSmallIntegerField()
    subject_id = models.BigIntegerField(null=True, blank=True)
    slot_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    primary_faculty_id = models.CharField(max_length=255, db_index=True)
    adjacent_faculty_id = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=20, default='PENDING')
    og_code = models.CharField(max_length=150, null=True, blank=True)
    class Meta:
        db_table = 'attendance_leave_adjacent_lecture'


class LeaveType(TrackingModel):
    leave_type_name = models.CharField(max_length=255, unique=True, db_index=True)
    units = models.CharField(max_length=50, default="Days")
    description = models.TextField(null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    class Meta:
        db_table = 'attendance_leave_type'


class LeaveTypeAllotment(TrackingModel):
    leave_type_id = models.BigIntegerField(db_index=True)
    designation_id = models.BigIntegerField(db_index=True)
    academic_year_id = models.BigIntegerField(db_index=True)
    allowed = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    opening_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    class Meta:
        db_table = 'attendance_leave_type_allotment'
        unique_together = ('leave_type_id', 'designation_id', 'academic_year_id')
