from django.db import models
from helpers.models import TrackingModel


class FeedbackCategory(TrackingModel):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)


class FeedbackSubCategory(TrackingModel):
    name = models.CharField(max_length=255)
    parent_feedback_category = models.BigIntegerField(null=True, blank=True, db_index=True)
    status = models.BooleanField(default=False)


class FeedbackForm(TrackingModel):
    name = models.CharField(max_length=255)
    add_note = models.TextField(blank=True)
    category_name = models.CharField(max_length=255)
    rating_type = models.CharField(max_length=50)
    question = models.TextField(null=True, blank=True)
    upload_img = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


class FeedbackActivation(TrackingModel):
    course = models.CharField(max_length=255, db_index=True)
    college = models.CharField(max_length=255, null=True, blank=True)
    schedule = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    class_group_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    candidate_feedbackform = models.TextField(null=True, blank=True)
    faculty_feedbackform = models.TextField(null=True, blank=True)
    college_feedbackform = models.TextField(null=True, blank=True)
    send_via = models.CharField(max_length=50, null=True, blank=True)
    certification_choice = models.BooleanField(default=False)


class FeedbackQuestion(TrackingModel):
    feedback_form_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    question = models.TextField(null=True, blank=True)
    upload_img = models.TextField(null=True, blank=True)
    sequence_number = models.PositiveIntegerField(default=1)


class FeedbackResponse(TrackingModel):
    feedback_activation_id = models.BigIntegerField(db_index=True)
    feedback_question_id = models.BigIntegerField(db_index=True)
    respondent_type = models.CharField(max_length=30, db_index=True)
    respondent_id = models.CharField(max_length=255, db_index=True)
    rating_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    response_text = models.TextField(null=True, blank=True)
