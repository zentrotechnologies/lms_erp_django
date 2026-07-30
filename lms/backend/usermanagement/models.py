from django.db import models
from helpers.models import *
# Create your models here.


class UsereRole(TrackingModel):
    name = models.CharField(max_length=255)
    remark = models.TextField()
    member_type = models.BigIntegerField(null=True,blank=True)   #data['member_type'] = 3
    member_of = models.CharField(max_length=150,null=True, blank=True)   #data['member_of'] = str(request.user.id)
    og_code = models.CharField(max_length=150,null=True, blank=True)


    
    
# class Member(TrackingModel):
#     name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     middle_name = models.CharField(max_length=255)
#     designation = CharField(max_length=255)
#     email = CharField(max_length=255)
#     contact_no = CharField(max_length=255)
#     password = CharField(max_length=255)
#     Confirm Password =
#     Reporting To = 
#     Gender =
#     Date of Birth = 
#     Country =
#     State