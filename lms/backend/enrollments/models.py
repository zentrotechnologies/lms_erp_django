from django.db import models
from helpers.models import TrackingModel


class Enrollments(TrackingModel):
    # Candidate is UUID-backed, so it remains a string identifier.
    candidate = models.CharField(max_length=255, db_index=True)
    course = models.CharField(max_length=255, db_index=True)
    schedule = models.CharField(max_length=255, db_index=True)
    enrollments_status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    college_id = models.CharField(max_length=255, null=True, blank=True)
    declined_rsn = models.TextField(null=True, blank=True)

    # College allocation fields
    academic_year_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    class_group_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    enrollment_number = models.CharField(max_length=100, null=True, blank=True, unique=True)
    enrollment_date = models.DateField(null=True, blank=True)
    application_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    payment_status = models.CharField(
        max_length=50,
        default="Pending",
        db_index=True,
    )

    payment_gateway = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    gateway_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    payment_response = models.JSONField(
        null=True,
        blank=True,
    )

class EnrollPayment(TrackingModel):
    billing_address = models.TextField(null=True, blank=True)
    city = models.BigIntegerField(null=True, blank=True)
    state = models.BigIntegerField(null=True, blank=True)
    country = models.BigIntegerField(null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    college_id = models.CharField(max_length=255, null=True, blank=True)
    candidate_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    currency_type = models.CharField(default="INR", max_length=10)
    enrollment_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    schedule_id = models.BigIntegerField(null=True, blank=True, db_index=True)

    # Never store card number/CVC in the ERP database.
    payment_gateway = models.CharField(max_length=100, null=True, blank=True)
    gateway_payment_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default="PENDING", db_index=True)


class CandidateSubjectSelection(TrackingModel):
    candidate_id = models.CharField(
        max_length=255,
        db_index=True,
    )

    application_id = models.CharField(
        max_length=255,
        db_index=True,
    )

    academic_year_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    program_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    semester_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    subject_id = models.CharField(
        max_length=255,
        db_index=True,
    )

    subject_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    selection_status = models.CharField(
        max_length=50,
        default="Selected",
    )

    mandatory = models.BooleanField(default=False)


