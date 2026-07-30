from django.db import models
from helpers.models import *
from django.contrib.auth.models import AbstractBaseUser, UserManager
import uuid
from django.utils.translation import gettext_lazy as _
import jwt
from datetime import datetime,timedelta
from django.conf import settings
from django.utils import timezone
    
class CandidateManager(UserManager):
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


class Candidate(AbstractBaseUser, TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_pic = models.TextField(null=True,blank=True)
    first_name = models.CharField(max_length=255,null=True,blank=True)
    middle_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)
    email = models.EmailField(_('email address'), blank=False, null=True)
    password = models.CharField(max_length=150, default="Default@123",null=True, blank=True)
    country_code = models.CharField(max_length=255,null=True,blank=True)
    mobilenumber = models.BigIntegerField(null=True,blank=True)
    alternate_mobilenumber = models.BigIntegerField(null=True,blank=True)
    highest_qualification = models.CharField(max_length=255,null=True,blank=True)
    qualification_year = models.CharField(max_length=255,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    passport_expiry_date = models.DateField(null=True,blank=True)
    passport_number  = models.CharField(max_length=255,null=True,blank=True)
    nationality  = models.CharField(max_length=255,null=True,blank=True)
    # Location
    country = models.BigIntegerField(null=True,blank=True)
    state = models.BigIntegerField(null=True, blank=True) 
    city = models.CharField(max_length=150,null=True, blank=True) 
    pincode = models.CharField(max_length=150,null=True, blank=True) 
    address_line_one = models.TextField(null=True,blank=True) 
    address_line_two = models.TextField(null=True,blank=True) 
    # Details
    vessel_name = models.CharField(max_length=150,null=True, blank=True) 
    next_vessel = models.CharField(max_length=150,null=True, blank=True) 
    sign_on_date = models.DateField(null=True,blank=True)
    sign_of_date = models.DateField(null=True,blank=True)
    seaman_book_number = models.CharField(max_length=255,null=True,blank=True) 
    department = models.CharField(max_length=255,null=True,blank=True) 
    rank = models.CharField(max_length=255,null=True,blank=True) 
    source = models.CharField(max_length=255,null=True,blank=True)
    # 
    candidate_status  = models.CharField(max_length=255,null=True,blank=True)
    action_takenby = models.CharField(max_length=255,null=True,blank=True)
    action_takenby_user_type = models.BigIntegerField(null=True,blank=True)
    application_number  = models.CharField(max_length=255,null=True,blank=True)
    decline_reason = models.TextField(null=True,blank=True)
    # 
    certificate_name = models.CharField(max_length=255,null=True)
    educational_certificate = models.TextField(null=True)
    deleted_by = models.CharField(max_length=255,null=True)
    walkin_by = models.CharField(max_length=255,null=True)

    #
    coc= models.CharField(max_length=255,null=True,blank=True)


    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CandidateManager()

    @property
    def token(self):
        token = jwt.encode(
            {'id': self.id.hex,
             'createdAt':timezone.now().isoformat()
            },
            settings.SECRET_KEY, algorithm='HS256')

        return token

class candidatelog(TrackingModel):
    candidate_id = models.CharField( max_length=255,null=True, blank=True)
    action_takenbyid = models.CharField( max_length=255,null=True, blank=True)
    action_usertype = models.BigIntegerField(null=True,blank=True)
    action = models.CharField( max_length=255,null=True, blank=True)
    decline_reason = models.TextField(null=True,blank=True)


class CandidateToken(TrackingModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user_id = models.CharField( max_length=255,null=True, blank=True)
    authToken = models.TextField(null=True, blank=True)
    apptoken = models.TextField(null=True, blank=True)
    source  = models.CharField(max_length=255,null=True,blank=True)
    
    
class CandidateDocuments(TrackingModel):
    user_id = models.CharField(max_length=255,null=True)
    document_id = models.IntegerField(null=True)
    document_name = models.CharField(max_length=255,null=True)
    document_url = models.TextField(null=True)
    status = models.BooleanField(default=False)
    reject_reason = models.TextField(null=True)


class candidateOtp(TrackingModel):
    candidate = models.CharField(max_length=255,null=True, blank=True)
    mobile_number = models.BigIntegerField(null=True, blank=True)
    email = models.CharField(max_length=255,null=True, blank=True)
    mobileotp = models.CharField(max_length=255,null=True, blank=True)
    emailotp = models.CharField(max_length=255,null=True, blank=True)
    
