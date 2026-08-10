from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import jwt
import uuid

from helpers.models import TrackingModel


class Roles(models.Model):
    role_code = models.CharField(max_length=50, unique=True, db_index=True)
    role_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.role_name


class ParentManager(UserManager):
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


class Parent(AbstractBaseUser, TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_pic = models.TextField(null=True, blank=True)
    parent_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(_("email address"), null=True, blank=False, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    alternate_mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=30, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    parent_relationship = models.CharField(max_length=100, null=True, blank=True)
    address_line_one = models.TextField(null=True, blank=True)
    address_line_two = models.TextField(null=True, blank=True)
    country = models.BigIntegerField(null=True, blank=True, db_index=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    college_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    role_code = models.CharField(max_length=50, null=True, blank=True, default="parent", db_index=True)
    student_ids = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = ParentManager()

    @property
    def token(self):
        return jwt.encode(
            {"id": self.id.hex, "createdAt": timezone.now().isoformat()},
            settings.SECRET_KEY,
            algorithm="HS256",
        )


class ParentToken(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    authToken = models.TextField(null=True, blank=True)
    apptoken = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)


class UsereRole(TrackingModel):
    name = models.CharField(max_length=255)
    remark = models.TextField(blank=True)
    member_type = models.BigIntegerField(null=True, blank=True)
    member_of = models.CharField(max_length=150, null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    role_code = models.CharField(max_length=50, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)


class RoleModulePermission(TrackingModel):
    role_id = models.BigIntegerField(db_index=True)
    module_code = models.CharField(max_length=100, db_index=True)
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role_id", "module_code"], name="uniq_role_module_permission"
            )
        ]
