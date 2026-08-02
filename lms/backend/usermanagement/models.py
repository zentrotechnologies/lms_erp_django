from django.db import models
from helpers.models import TrackingModel


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
