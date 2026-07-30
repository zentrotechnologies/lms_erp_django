from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Course(TrackingModel):
    course_name =  models.CharField(max_length=255,null=True,blank=True)
    course_code =  models.CharField(max_length=255,null=True,blank=True)
    training_mode = models.CharField(max_length=255,null=True,blank=True) #online/offline/blearning
    duration = models.CharField(max_length=255,null=True,blank=True)
    expiry = models.DateField(null=True,blank=True)
    followed_by = models.BigIntegerField(null=True,blank=True)
    topics_covered =  models.TextField(default='',blank=True)
    pricing = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(default='',blank=True)
    course_status = models.CharField(max_length=255,null=True,blank=True,default='Pending')
    info_status = models.CharField(max_length=255,null=True,blank=True)
    languages = models.JSONField(null=True,blank=True)
    og_code = models.CharField(max_length=150,null=True, blank=True) 
    og_approved = models.BooleanField(default=False)#org
    og_approvedby = models.CharField(max_length=255,null=True,blank=True)
    ptc_approved = models.BooleanField(default=False)#parent training center
    ptc_approvedby = models.CharField(max_length=255,null=True,blank=True)



class CourseModules(TrackingModel):
    course_id = models.BigIntegerField(null=True,blank=True)
    module_name = models.TextField(default='')
    module_description = models.TextField(default='')
    module_hours = models.CharField(max_length=255,null=True,blank=True)


class CourseMaterial(TrackingModel):
    course_id = models.BigIntegerField(null=True,blank=True)
    module_id = models.BigIntegerField(null=True,blank=True)
    language = models.BigIntegerField(null=True,blank=True)
    material_type = models.CharField(max_length=255,null=True,blank=True)
    material_label = models.CharField(max_length=255,null=True,blank=True)
    material_link = models.TextField(default='')
    material_file = models.TextField(null=True)

class CourseEligibility(TrackingModel):
    course_id = models.BigIntegerField(null=True,blank=True)
    category =  models.JSONField(null=True,blank=True)
    subcategory =  models.JSONField(null=True,blank=True)
    department =  models.JSONField(null=True,blank=True)
    rank =  models.JSONField(null=True,blank=True)


class rankItemInfo(TrackingModel):
    course_id = models.BigIntegerField(null=True,blank=True)
    eligibilityid = models.BigIntegerField(null=True,blank=True)
    rank = models.BigIntegerField(null=True,blank=True)
    # rank_name = models.CharField(max_length=255,null=True,blank=True)
    mandatory = models.BooleanField(default=False)
    

class TrainingMode(TrackingModel):
    training_mode = models.CharField(max_length=255,null=True,blank=True)