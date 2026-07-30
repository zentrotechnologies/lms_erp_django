from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Category(TrackingModel):
    category_name = models.CharField(max_length=255,null=True,blank=True)
    tags = models.TextField(null=True,blank=True)
    status = models.BooleanField(default=True)


class TicketCategory(TrackingModel):
    name = models.CharField(max_length=255,null=True,blank=True)
    status = models.BooleanField(default=True)

class Sub_Category(TrackingModel):
    category_name = models.IntegerField(null=True,blank=True)
    sub_name = models.CharField(max_length=255)
    tags = models.TextField(null=True,blank=True)
    status = models.BooleanField(default=True)    


class Department(TrackingModel):
    department_name = models.CharField(max_length=255)
    tags = models.TextField(null=True,blank=True)
    status = models.BooleanField(default=True)
    

class Rank(TrackingModel):
    department_name = models.IntegerField()
    rank = models.CharField(max_length=255)
    tags = models.TextField(null=True,blank=True)
    status = models.BooleanField(default=True)
    

class Documents(TrackingModel):
    role = models.CharField(max_length=255)
    document_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)


class Languages(TrackingModel):
    languages_name = models.CharField(max_length=255)
    
    
class Specialization(TrackingModel):    
    specialization_name = models.CharField(max_length=255)
    
    
class Branch(TrackingModel):
    name = models.CharField(max_length=255,null=True,blank=True)  
    training_center = models.CharField(max_length=255,null=True,blank=True)  
    mobilenumber = models.BigIntegerField(null=True,blank=True) 
    alternate_mobilenumber = models.BigIntegerField(null=True,blank=True)
    email = models.CharField(max_length=255,null=True,blank=True)  

    address_line_one = models.TextField(null=True,blank=True) 
    address_line_two = models.TextField(null=True,blank=True) 
    country = models.BigIntegerField(null=True,blank=True)
    state = models.CharField(max_length=150,null=True, blank=True) 
    city = models.CharField(max_length=150,null=True, blank=True) 
    pincode = models.CharField(max_length=150,null=True, blank=True) 
    landmark = models.CharField(max_length=150,null=True, blank=True) 

    og_code = models.CharField(max_length=150,null=True, blank=True)
    
class Coordinator(TrackingModel):
    branch_id = models.BigIntegerField(null=True,blank=True)
    coordinator_name = models.CharField(max_length=255,null=True)
    coordinator_number = models.CharField(max_length=255,null=True)
    coordinator_email = models.CharField(max_length=255,null=True)
    coordinator_designation = models.CharField(max_length=255,null=True)


class S3Upload(TrackingModel):
    course = models.JSONField(null=True,blank=True)
    module = models.JSONField(null=True,blank=True)
    s3_tags = models.TextField(default='')
    s3_file = models.TextField(null=True)


class Enquiries(TrackingModel):
    name = models.CharField(max_length=255,null=True)
    contact = models.BigIntegerField(null=True,blank=True)
    email = models.EmailField(_('email address'), blank=False, null=True)
    message = models.TextField(null=True)
    status = models.CharField(max_length=255,null=True)
    

class Vessel(TrackingModel):
    name = models.CharField(max_length=255,null=True,blank=True)
    code = models.CharField(max_length=255,null=True,blank=True)
    category = models.BigIntegerField(null=True,blank=True)
    subcategory = models.BigIntegerField(null=True,blank=True)
    imo_number = models.CharField(max_length=255,null=True,blank=True)
    mmsi_number =  models.CharField(max_length=255,null=True,blank=True)
    flag_state =  models.BigIntegerField(null=True,blank=True)
    registry_port = models.CharField(max_length=255,null=True,blank=True)
    built_year = models.DateField(null=True,blank=True)
    shipyard_builder = models.CharField(max_length=255,null=True,blank=True)
    class_society = models.CharField(max_length=255,null=True,blank=True)
    #ownership & management
    owner_name = models.CharField(max_length=255,null=True,blank=True)
    technical_manager = models.CharField(max_length=255,null=True,blank=True)
    commercial_manager = models.CharField(max_length=255,null=True,blank=True)
    operator = models.CharField(max_length=255,null=True,blank=True)
    PI_club = models.CharField(max_length=255,null=True,blank=True)
    #operational details
    last_dry_dock_date =  models.DateField(null=True,blank=True)
    next_dry_dock_date =  models.DateField(null=True,blank=True)
    last_survey_date = models.DateField(null=True,blank=True)
    next_survey_due_date = models.DateField(null=True,blank=True)
    #maintenance & performance records
    fuel_consumption_rates = models.TextField(null=True)
    maintenance_history = models.TextField(null=True)
    status = models.BooleanField(default=True) #activated/deactivated



class EducationalQualifications(TrackingModel):
    qualification_name =  models.CharField(max_length=555,null=True,blank=True)









