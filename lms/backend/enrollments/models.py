from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _
# Create your models here.





class Enrollments(TrackingModel):
    candidate = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    schedule = models.CharField(max_length=255)
    enrollments_status  = models.CharField(max_length=255,null=True,blank=True)
    source  = models.CharField(max_length=255,null=True,blank=True)
    trainingcenter_id = models.CharField(max_length=255,null=True,blank=True)
    declined_rsn = models.TextField(null=True,blank=True)



    
class EnrollPayment(TrackingModel):
    billing_address = models.TextField(null=True,blank=True)
    city = models.BigIntegerField(null=True,blank=True)
    state = models.BigIntegerField(null=True,blank=True)
    country = models.BigIntegerField(null=True,blank=True)
    pincode = models.CharField(max_length=255,null=True,blank=True) 
    payment_method = models.TextField(null=True,blank=True) #upi/card
    transaction_id = models.TextField(null=True,blank=True) #upi id
    subtotal_amount = models.FloatField(default=0,null=True,blank=True)
    discount_amount = models.FloatField(default=0,null=True,blank=True)
    final_amount = models.FloatField(default=0,null=True,blank=True)
    trainingcenter_id = models.CharField(max_length=255,null=True,blank=True)
    candidate_id = models.BigIntegerField(null=True,blank=True)
    course_id = models.BigIntegerField(null=True,blank=True)
    currency_type = models.CharField(default="USD",max_length=255,null=True,blank=True)
    enrollment_id = models.BigIntegerField(null=True,blank=True)
    schedule_id = models.BigIntegerField(null=True,blank=True)
    card_number =models.CharField(max_length=255,null=True,blank=True)
    expiry_date = models.DateField(null=True,blank=True)
    cvc = models.CharField(max_length=255,null=True,blank=True)
    name_on_card = models.CharField(max_length=255,null=True,blank=True)


    
    
    