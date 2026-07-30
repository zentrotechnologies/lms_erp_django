from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _
from course.models import Course
from adminauth.models import UserAdmin

# Create your models here.
class Schedule(TrackingModel):
    course_ids = models.ManyToManyField(Course, blank=True)
    training_center_ids = models.ManyToManyField(UserAdmin, blank=True)
    branch_id =  models.CharField(max_length=255,null=True,blank=True)
    faculty_id =  models.CharField(max_length=255,null=True,blank=True)
    faculty2_id =  models.CharField(max_length=255,null=True,blank=True)
    start_date = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    start_time = models.CharField(max_length=255,null=True,blank=True)
    end_time = models.CharField(max_length=255,null=True,blank=True)
    max_capacity = models.CharField(max_length=255,null=True,blank=True)
    mode =  models.CharField(max_length=255,null=True,blank=True)
    schedulename =  models.CharField(max_length=255,null=True,blank=True)
    action_status =  models.CharField(default="Approved",max_length=255,null=True,blank=True)
    decline_reason = models.TextField(null=True,blank=True)

class RescheduleLog(TrackingModel):
    schedule_id =  models.CharField(max_length=255,null=True,blank=True)
    old_start_date = models.DateField(null=True,blank=True)
    old_end_date = models.DateField(null=True,blank=True)
    old_start_time = models.CharField(max_length=255,null=True,blank=True)
    old_end_time = models.CharField(max_length=255,null=True,blank=True)
    new_start_date = models.DateField(null=True,blank=True)
    new_end_date = models.DateField(null=True,blank=True)
    new_start_time = models.CharField(max_length=255,null=True,blank=True)
    new_end_time = models.CharField(max_length=255,null=True,blank=True)
    reschedule_reason = models.TextField(null=True,blank=True)

