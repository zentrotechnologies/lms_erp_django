from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _
# Create your models here.


class FeedbackCategory(TrackingModel):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)
class FeedbackSubCategory(TrackingModel):
    name = models.CharField(max_length=255)
    parent_feedback_category = models.BigIntegerField(null=True,blank=True)
    status = models.BooleanField(default=False)
    
class FeedbackForm(TrackingModel):
    name = models.CharField(max_length=255)
    add_note = models.TextField()
    category_name = models.CharField(max_length=255)
    rating_type = models.CharField(max_length=255)
    question = models.TextField(null=True,blank=True)
    upload_img = models.TextField(null=True,blank=True)
    email = models.EmailField(('email address'), blank=False, null=True)
    
    
class FeedbackActivation(TrackingModel):
    course = models.CharField(max_length=255)
    training_center = models.CharField(max_length=255,null=True,blank=True)
    schedule = models.CharField(max_length=255,null=True,blank=True)
    candidate_feedbackform = models.TextField(null=True,blank=True)
    faculty_feedbackform = models.TextField(null=True,blank=True)
    training_center_feedbackform = models.TextField()
    send_via = models.CharField(max_length=255,null=True,blank=True)
    certification_choice = models.BooleanField(default=False)
    
    
class FeedbackQuestion(TrackingModel):
    feedback_form_id = models.BigIntegerField(null=True,blank=True)
    question = models.TextField(null=True,blank=True)
    upload_img = models.TextField(null=True,blank=True)    