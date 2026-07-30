from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _
from course.models import Course
from adminauth.models import UserAdmin

# Create your models here.
class CandidateAttendance(TrackingModel):
    candidate_id =  models.CharField(max_length=255,null=True,blank=True)
    schedule_id = models.CharField(max_length=255,null=True,blank=True)
    course_id = models.CharField(max_length=255,null=True,blank=True)
    training_center_id = models.CharField(max_length=255,null=True,blank=True)
    faculty_id =  models.CharField(max_length=255,null=True,blank=True)
    attendance_date = models.DateField(null=True,blank=True)
    checkin_time = models.CharField(max_length=255,null=True,blank=True)
    checkout_time = models.CharField(max_length=255,null=True,blank=True)
    present=models.BooleanField(default=True,)
    absent=models.BooleanField(default=False,)

