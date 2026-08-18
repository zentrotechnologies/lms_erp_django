from django.db import models
from helpers.models import TrackingModel


class Schedule(TrackingModel):
    # Existing class retained but M2M relations replaced by mapping tables.
    branch_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    faculty_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    faculty2_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    academic_year_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    class_group_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    end_time = models.CharField(max_length=255, null=True, blank=True)
    max_capacity = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=50, null=True, blank=True)
    schedulename = models.CharField(max_length=255, null=True, blank=True)
    action_status = models.CharField(max_length=50, default="Approved", db_index=True)
    decline_reason = models.TextField(null=True, blank=True)


class ScheduleCourseMapping(TrackingModel):
    schedule_id = models.BigIntegerField(db_index=True)
    course_id = models.BigIntegerField(db_index=True)



class ScheduleCollegeMapping(TrackingModel):
    schedule_id = models.BigIntegerField(db_index=True)
    college_id = models.CharField(max_length=255, db_index=True)




class TimetableTemplate(TrackingModel):
    academic_year_id = models.BigIntegerField(db_index=True)
    semister_id = models.BigIntegerField(db_index=True)
    class_id = models.BigIntegerField(db_index=True)
    template_name = models.CharField(max_length=150)


class TimetableSlot(TrackingModel):
    timetable_template_id = models.BigIntegerField(db_index=True)
    day_of_week = models.PositiveSmallIntegerField()
    period_number = models.PositiveSmallIntegerField()
    start_time =models.CharField(max_length=250, null=True, blank=True)
    end_time =models.CharField(max_length=250, null=True, blank=True)
    course_id = models.BigIntegerField(db_index=True)
    faculty_id = models.CharField(max_length=255, db_index=True)#logined user
    entry_for = models.CharField(default="lecture",max_length=50, null=True, blank=True)#lecture/longbreak/shortbrak
    lecture_type = models.CharField(max_length=30, default="THEORY")




class LectureEntry(TrackingModel):
    academic_year_id = models.BigIntegerField(db_index=True)
    class_group_id = models.BigIntegerField(db_index=True)
    course_id = models.BigIntegerField(db_index=True)
    faculty_id = models.CharField(max_length=255, db_index=True)
    timetable_slot_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    lecture_date = models.DateField(db_index=True)
    start_time =models.CharField(max_length=250, null=True, blank=True)
    end_time =models.CharField(max_length=250, null=True, blank=True)
    topic = models.CharField(max_length=500)
    teaching_method = models.CharField(max_length=150, null=True, blank=True)
    lecture_status = models.CharField(max_length=30, default="SCHEDULED", db_index=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.CharField(max_length=255)


class RescheduleLog(TrackingModel):
    schedule_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    old_start_date = models.DateField(null=True, blank=True)
    old_end_date = models.DateField(null=True, blank=True)
    old_start_time = models.CharField(max_length=255, null=True, blank=True)
    old_end_time = models.CharField(max_length=255, null=True, blank=True)
    new_start_date = models.DateField(null=True, blank=True)
    new_end_date = models.DateField(null=True, blank=True)
    new_start_time = models.CharField(max_length=255, null=True, blank=True)
    new_end_time = models.CharField(max_length=255, null=True, blank=True)
    reschedule_reason = models.TextField(null=True, blank=True)
