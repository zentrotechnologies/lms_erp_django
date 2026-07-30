from django.db import models
from helpers.models import *
from django.contrib.auth.models import AbstractBaseUser, UserManager
import uuid
from django.utils.translation import gettext_lazy as _
import jwt
from datetime import datetime,timedelta
from django.conf import settings
from django.utils import timezone
    
class UserAdminManager(UserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)


class UserAdmin(AbstractBaseUser, TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,null=True,blank=True)  #common for superadmin,pma,training center
    mobilenumber = models.BigIntegerField(null=True,blank=True) #for all common 
    alternate_mobilenumber = models.BigIntegerField(null=True,blank=True) #for training center and faculty
    password = models.CharField(max_length=150, default="Default@123",null=True, blank=True)
    email = models.EmailField(_('email address'), blank=False, null=True)  #for all common 
    status = models.BooleanField(default=False) #for verification
    source  = models.CharField(max_length=255,null=True,blank=True) #web or admin
    
    #for training center
    accreditation_number = models.CharField(max_length=150,null=True, blank=True)
    is_parent_training_center = models.BooleanField(default=False)
    parent_training_center = models.CharField(max_length=150,null=True, blank=True) #for faculty 
    no_of_classroom = models.BigIntegerField(default=0)
    
    #for faculty
    first_name = models.CharField(max_length=255,null=True,blank=True)
    middle_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True) 
    designation = models.CharField(max_length=255,null=True,blank=True) 
    reporting_to = models.CharField(max_length=255,null=True,blank=True) 
    dob = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=150,null=True, blank=True)
    years_of_experience = models.CharField(max_length=150,null=True, blank=True)
    previous_institute = models.CharField(max_length=150,null=True, blank=True)
    teaching_experience = models.CharField(max_length=150,null=True, blank=True)
    preferred_teaching_mode = models.CharField(max_length=150,null=True, blank=True)
    specialization = models.TextField(null=True,blank=True)
    languages = models.JSONField(null=True,blank=True)
    
    #common for training center and faculty
    address_line_one = models.TextField(null=True,blank=True) 
    address_line_two = models.TextField(null=True,blank=True) 
    country = models.BigIntegerField(null=True,blank=True)
    state = models.CharField(max_length=150,null=True, blank=True) 
    city = models.CharField(max_length=150,null=True, blank=True) 
    pincode = models.CharField(max_length=150,null=True, blank=True) 
    
    
    #common for superadmin,og,training center
    is_member = models.BooleanField(default=False)   #data['is_member'] = True
    member_type = models.BigIntegerField(null=True,blank=True)   #data['member_type'] = 3
    member_of = models.CharField(max_length=150,null=True, blank=True)   #data['member_of'] = str(request.user.id)
    joining_date = models.DateField(null=True)
    role = models.BigIntegerField(null=True,blank=True)
    



    #ALL    
    # is_superadmin = models.BooleanField(default=False) 
    # is_organisation = models.BooleanField(default=False) #organisation/pma
    # is_training_center = models.BooleanField(default=False) 
    # is_faculty = models.BooleanField(default=False) 


    user_type = models.BigIntegerField(null=True,blank=True)
    og_code = models.CharField(max_length=150,null=True, blank=True)
    og_id = models.CharField(max_length=150,null=True, blank=True)
    deactivate = models.BooleanField(default=True)
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserAdminManager()

    @property
    def token(self):
        token = jwt.encode(
            {'id': self.id.hex,
             'createdAt':timezone.now().isoformat()
            },
            settings.SECRET_KEY, algorithm='HS256')

        return token


class UserAdminToken(TrackingModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user_id = models.CharField( max_length=255,null=True, blank=True)
    authToken = models.TextField(null=True, blank=True)
    apptoken = models.TextField(null=True, blank=True)
    source  = models.CharField(max_length=255,null=True,blank=True)


class UserAdminOtp(TrackingModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user_id = models.CharField(max_length=255,null=True, blank=True)
    mobile_number = models.BigIntegerField(null=True, blank=True)
    email = models.CharField(max_length=255,null=True, blank=True)
    mobileotp = models.CharField(max_length=255,null=True, blank=True)
    emailotp = models.CharField(max_length=255,null=True, blank=True)
    source  = models.CharField(max_length=255,null=True,blank=True)

class MainRoles(models.Model):
    name = models.CharField(max_length=255)
    documents_required = models.BooleanField(default=False)
    
class Country(models.Model):
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=255,null=True,blank=True)
    numeric_code = models.CharField(max_length=255,null=True,blank=True)
    iso2 = models.CharField(max_length=255,null=True,blank=True)
    phonecode = models.CharField(max_length=255)
    capital = models.CharField(max_length=255,null=True,blank=True)
    currency = models.CharField(max_length=255)
    currency_symbol = models.CharField(max_length=255,null=True,blank=True)
    tld = models.CharField(max_length=255,null=True,blank=True)
    native = models.CharField(max_length=255,null=True,blank=True)
    region = models.CharField(max_length=255,null=True,blank=True)
    subregion = models.CharField(max_length=255,null=True,blank=True)
    timezones = models.TextField(null=True,blank=True)
    translations = models.TextField(null=True,blank=True)
    latitude = models.CharField(max_length=255,null=True,blank=True)
    longitude = models.CharField(max_length=255,null=True,blank=True)
    emoji = models.CharField(max_length=255,null=True,blank=True)
    emojiU =models.CharField(max_length=255,null=True,blank=True)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255,null=True,blank=True)
    sequence = models.CharField(max_length=255,null=True,blank=True)
    wikiDataId = models.CharField(max_length=255,null=True,blank=True)
    is_eligibile = models.BooleanField(default=False)
    is_black_list = models.BooleanField(default=False)
    flag_image = models.FileField(upload_to='media/Country/flag_image/', blank=True, null=True,verbose_name='flag_image')

    isActive = models.BooleanField(default=True)


    def __str__(self):

        return self.name

class State(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country,on_delete=models.CASCADE)
    country_code = models.CharField(max_length=255)
    state_code = models.CharField(max_length=255,null=True)
    TIN = models.CharField(max_length=255)
    iso2 = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)
    wikiDataId = models.CharField(max_length=255)
 

    def __str__(self):

        return self.name

class Cities(models.Model):
    name = models.CharField(max_length=255)
    state_code = models.CharField(max_length=255)
    country_code = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255)
    wikiDataId = models.CharField(max_length=255,null=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE)
    country = models.ForeignKey(Country,on_delete=models.CASCADE)

 

    def __str__(self):

        return self.name

class UserDocuments(TrackingModel):
    user_id = models.CharField(max_length=255,null=True)
    document_id = models.IntegerField(null=True)
    branch_id = models.IntegerField(null=True)
    document_name = models.CharField(max_length=255,null=True)
    document_url = models.TextField(null=True)
    status = models.BooleanField(default=False)
    reject_reason = models.TextField(null=True)


class Authority(TrackingModel):
    user_id = models.CharField(max_length=255,null=True)
    authority_name = models.CharField(max_length=255,null=True)
    authority_number = models.CharField(max_length=255,null=True)
    authority_email = models.CharField(max_length=255,null=True)
    authority_designation = models.CharField(max_length=255,null=True)


class MenuDetails(TrackingModel):
    menu_name = models.CharField(max_length=255)
    menu_path = models.CharField(max_length=255,null=True,blank=True)
    parent_id = models.IntegerField()
    sort_order = models.IntegerField(null=True,blank=True)
    menu_icon = models.CharField(max_length=255,null=True,blank=True)
    og_code = models.CharField(max_length=255,null=True,blank=True)
    user_type = models.CharField(max_length=255,null=True,blank=True) 
    

class Permissions(TrackingModel):
    role_id = models.IntegerField()
    menu_id = models.IntegerField()
    all = models.BooleanField(default=False)
    add = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    approve = models.BooleanField(default=False)


class TrainingCenterCourses(TrackingModel):
    course_id = models.IntegerField()
    training_center_id = models.CharField(max_length=255,null=True,blank=True)