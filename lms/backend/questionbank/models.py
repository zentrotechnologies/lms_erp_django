from django.db import models
from helpers.models import TrackingModel


class Question(TrackingModel):
    course = models.JSONField(default=list, blank=True)
    subject = models.JSONField(default=list, blank=True)
    type_of_question = models.CharField(max_length=50, null=True)
    question_text = models.TextField(null=True)
    correct_option = models.BigIntegerField(null=True)
    time_to_solve = models.PositiveIntegerField(default=0)
    marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    difficulty_level = models.CharField(max_length=50, null=True, db_index=True)
    tags = models.TextField(null=True)
    note = models.TextField(null=True)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null=True)
    is_duplicate = models.BooleanField(default=False)
    tc_id = models.CharField(max_length=255, null=True)

    # Plain IDs for direct college filtering.
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    subject_id = models.BigIntegerField(null=True, blank=True, db_index=True)


class QuestionOption(TrackingModel):
    question_id = models.BigIntegerField(null=True, db_index=True)
    option = models.PositiveIntegerField(null=True)
    option_answer = models.TextField(null=True)
    option_image = models.TextField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question_id", "option"], name="uniq_question_option_number"
            )
        ]


class QuestionImages(TrackingModel):
    question_id = models.BigIntegerField(null=True, db_index=True)
    image = models.TextField(null=True)


class QuestionLike(TrackingModel):
    question_id = models.BigIntegerField(null=True, db_index=True)
    actionby = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    is_like = models.BooleanField(default=False)
    is_dislike = models.BooleanField(default=False)
    dislike_reason = models.TextField(null=True)


class DuplicateQuestion(TrackingModel):
    question_id = models.BigIntegerField(null=True, db_index=True)
    duplicate_of = models.JSONField(default=list, blank=True)
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    subject_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    severity_level = models.CharField(max_length=50, null=True)
    type_of_question = models.CharField(max_length=50, null=True)
