from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _
from course.models import Course
from adminauth.models import UserAdmin

# Create your models here.
class Ticket(TrackingModel):
    subject = models.CharField(max_length=255,null=True,blank=True)
    priority =  models.CharField(max_length=255,null=True,blank=True)
    category =  models.CharField(max_length=255,null=True,blank=True)
    requestername =  models.CharField(max_length=255,null=True,blank=True)
    email =  models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    status =  models.CharField(max_length=255,null=True,blank=True)
    raisedate = models.DateField(auto_now=True,null=True,blank=True)
    raiseby = models.CharField(max_length=255,null=True,blank=True)
    ticketid =  models.CharField(max_length=255,null=True,blank=True)
    IPAddress =  models.CharField(max_length=255,null=True,blank=True)
    isduplicate = models.BooleanField(default=False,null=True,blank=True)
    parentticketid =  models.CharField(max_length=255,null=True,blank=True)
    parent_training_center_id =  models.CharField(max_length=255,null=True,blank=True)
    sub_training_center_id =  models.CharField(max_length=255,null=True,blank=True)
    og_code = models.CharField(max_length=150,null=True, blank=True)
    




class TicketAssign(TrackingModel):
    ticket = models.CharField(max_length=255,null=True,blank=True)
    username = models.CharField(max_length=255,null=True,blank=True)
    userid = models.CharField(max_length=255,null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    active = models.BooleanField(default=True,null=True,blank=True)



class TicketAttachments(TrackingModel):
    ticket = models.CharField(max_length=255,null=True,blank=True)
    attachment = models.FileField(upload_to='attachment/', blank=True, null=True,verbose_name='attachment')
    comment = models.TextField(null=True,blank=True)



class TicketActivity(TrackingModel):
    ticket = models.CharField(max_length=255,null=True,blank=True)
    username = models.CharField(max_length=255,null=True,blank=True)
    userid = models.CharField(max_length=255,null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    attachment = models.FileField(upload_to='media/activity/attachment/', blank=True, null=True,verbose_name='attachment')
    isread = models.BooleanField(default=False,null=True,blank=True)



class FAQTicket(TrackingModel):
    ticket = models.CharField(max_length=255,null=True,blank=True)
    categoryId = models.CharField(max_length=255,null=True,blank=True)
    departmentId = models.CharField(max_length=255,null=True,blank=True)
    tags =models.CharField(max_length=255,null=True,blank=True)
    attachment = models.FileField(upload_to='media/activity/attachment/', blank=True, null=True,verbose_name='attachment')
















