from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import jwt
import uuid
from helpers.models import TrackingModel

class UserAdminManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)


class UserAdmin(AbstractBaseUser, TrackingModel):
    FACULTY_SUB_ROLE_CHOICES = (
        ("HOD", "HOD"),
        ("TEACHER", "Teacher"),
        ("STAFF", "Staff"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Existing identity fields
    name = models.CharField(max_length=255, null=True, blank=True)
    mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    alternate_mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(_("email address"), null=True, blank=False, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False)
    source = models.CharField(max_length=50, null=True, blank=True)

    # Legacy college fields retained for data migration
    is_parent_college = models.BooleanField(default=False)
    is_parent_training_center = models.BooleanField(default=False)
    parent_college = models.CharField(max_length=150, null=True, blank=True)
    no_of_classroom = models.PositiveIntegerField(default=0)

    # Faculty profile
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    reporting_to = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, null=True, blank=True)
    years_of_experience = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    previous_institute = models.CharField(max_length=255, null=True, blank=True)
    teaching_experience = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    specialization = models.TextField(null=True, blank=True)
    languages = models.JSONField(default=list, blank=True)

    address_line_one = models.TextField(null=True, blank=True)
    address_line_two = models.TextField(null=True, blank=True)
    country = models.BigIntegerField(null=True, blank=True, db_index=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)

    is_member = models.BooleanField(default=False)
    member_type = models.BigIntegerField(null=True, blank=True, db_index=True)
    member_of = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    joining_date = models.DateField(null=True, blank=True)
    role = models.BigIntegerField(null=True, blank=True, db_index=True)
    role_code = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    # College faculty fields
    marital_status = models.CharField(max_length=100, null=True, blank=True)
    blood_group = models.CharField(max_length=100, null=True, blank=True)
    religion  = models.CharField(max_length=250, null=True, blank=True)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    caste = models.CharField(max_length=100, null=True, blank=True)
    pan_number  = models.CharField(max_length=250, null=True, blank=True)
    adhar_number  = models.CharField(max_length=250, null=True, blank=True)
    faculty_sub_role = models.CharField(max_length=20, choices=FACULTY_SUB_ROLE_CHOICES, null=True, blank=True, db_index=True)
    college_id = models.CharField(max_length=250, null=True, blank=True)
    department_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    work_group = models.CharField(max_length=100, null=True, blank=True)
    work_category = models.CharField(max_length=100, null=True, blank=True)
    employment_type = models.CharField(max_length=50, null=True, blank=True)
    official_email = models.EmailField(_("official email address"), null=True, blank=True)
    pf_no = models.CharField(max_length=100, null=True, blank=True)
    employee_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    bank_name  = models.CharField(max_length=250, null=True, blank=True)
    account_number  = models.CharField(max_length=250, null=True, blank=True)

    user_type = models.BigIntegerField(null=True, blank=True, db_index=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    deactivate = models.BooleanField(default=False)
    is_organisation=models.BooleanField(default=False)
    
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserAdminManager()

    @property
    def token(self):
        return jwt.encode(
            {"id": self.id.hex, "createdAt": timezone.now().isoformat()},
            settings.SECRET_KEY,
            algorithm="HS256",
        )


class UserAdminToken(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    authToken = models.TextField(null=True, blank=True)
    apptoken = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)


class UserAdminOtp(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobileotp = models.CharField(max_length=10, null=True, blank=True)
    emailotp = models.CharField(max_length=10, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)


class MainRoles(models.Model):
    name = models.CharField(max_length=100, unique=True)
    documents_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


class Country(models.Model):
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=10, null=True, blank=True)
    numeric_code = models.CharField(max_length=10, null=True, blank=True)
    iso2 = models.CharField(max_length=10, null=True, blank=True)
    phonecode = models.CharField(max_length=20)
    capital = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=50)
    currency_symbol = models.CharField(max_length=20, null=True, blank=True)
    tld = models.CharField(max_length=50, null=True, blank=True)
    native = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    subregion = models.CharField(max_length=100, null=True, blank=True)
    timezones = models.TextField(null=True, blank=True)
    translations = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    emoji = models.CharField(max_length=50, null=True, blank=True)
    emojiU = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.CharField(max_length=255)
    flag = models.CharField(max_length=255, null=True, blank=True)
    sequence = models.CharField(max_length=255, null=True, blank=True)
    wikiDataId = models.CharField(max_length=255, null=True, blank=True)
    is_eligibile = models.BooleanField(default=False)
    is_black_list = models.BooleanField(default=False)
    flag_image = models.FileField(upload_to="media/Country/flag_image/", blank=True, null=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=255)
    country_id = models.BigIntegerField(db_index=True)
    country_code = models.CharField(max_length=20)
    state_code = models.CharField(max_length=20, null=True, blank=True)
    TIN = models.CharField(max_length=100, blank=True)
    iso2 = models.CharField(max_length=20, blank=True)
    latitude = models.CharField(max_length=50, blank=True)
    longitude = models.CharField(max_length=50, blank=True)
    created_at = models.CharField(max_length=255, blank=True)
    flag = models.CharField(max_length=255, blank=True)
    wikiDataId = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Cities(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.BigIntegerField(db_index=True)
    country_id = models.BigIntegerField(db_index=True)
    state_code = models.CharField(max_length=20)
    country_code = models.CharField(max_length=20)
    latitude = models.CharField(max_length=50, blank=True)
    longitude = models.CharField(max_length=50, blank=True)
    created_at = models.CharField(max_length=255, blank=True)
    flag = models.CharField(max_length=255, blank=True)
    wikiDataId = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class UserDocuments(TrackingModel):
    user_id = models.CharField(max_length=255, null=True, db_index=True)
    document_id = models.IntegerField(null=True, db_index=True)
    branch_id = models.IntegerField(null=True, db_index=True)
    document_name = models.CharField(max_length=255, null=True)
    document_url = models.TextField(null=True)
    status = models.BooleanField(default=False)
    reject_reason = models.TextField(null=True)


class Authority(TrackingModel):
    user_id = models.CharField(max_length=255, null=True, db_index=True)
    authority_name = models.CharField(max_length=255, null=True)
    authority_number = models.CharField(max_length=255, null=True)
    authority_email = models.EmailField(null=True)
    authority_designation = models.CharField(max_length=255, null=True)


class MenuDetails(TrackingModel):
    menu_name = models.CharField(max_length=255)
    menu_path = models.CharField(max_length=255, null=True, blank=True)
    parent_id = models.IntegerField(default=0, db_index=True)
    sort_order = models.IntegerField(null=True, blank=True)
    menu_icon = models.CharField(max_length=255, null=True, blank=True)
    og_code = models.CharField(max_length=255, null=True, blank=True)
    user_type = models.CharField(max_length=255, null=True, blank=True)


class Permissions(TrackingModel):
    role_id = models.IntegerField(db_index=True)
    menu_id = models.IntegerField(db_index=True)
    all = models.BooleanField(default=False)
    add = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    approve = models.BooleanField(default=False)




class CollegeCourses(TrackingModel):
    course_id = models.IntegerField(db_index=True)
    college_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
