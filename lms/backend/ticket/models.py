from django.db import models
from helpers.models import TrackingModel


class Ticket(TrackingModel):
    subject = models.CharField(max_length=255, null=True, blank=True)
    priority = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    requestername = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    raisedate = models.DateField(auto_now_add=True)
    raiseby = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    ticketid = models.CharField(max_length=100, null=True, blank=True, unique=True)
    IPAddress = models.GenericIPAddressField(null=True, blank=True)
    isduplicate = models.BooleanField(default=False)
    parentticketid = models.CharField(max_length=255, null=True, blank=True)
    parent_training_center_id = models.CharField(max_length=255, null=True, blank=True)
    sub_training_center_id = models.CharField(max_length=255, null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)

    # College communication scope
    requester_type = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    related_student_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    department_id = models.BigIntegerField(null=True, blank=True, db_index=True)


class TicketAssign(TrackingModel):
    ticket = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    userid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    comment = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)


class TicketAttachments(TrackingModel):
    ticket = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    attachment = models.FileField(upload_to="attachment/", blank=True, null=True)
    comment = models.TextField(null=True, blank=True)


class TicketActivity(TrackingModel):
    ticket = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    userid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    comment = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to="media/activity/attachment/", blank=True, null=True)
    isread = models.BooleanField(default=False)


class FAQTicket(TrackingModel):
    ticket = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    categoryId = models.CharField(max_length=255, null=True, blank=True)
    departmentId = models.CharField(max_length=255, null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    attachment = models.FileField(upload_to="media/activity/attachment/", blank=True, null=True)
