from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _

class Question(TrackingModel):
    course = models.JSONField(null=True,blank=True)
    module = models.JSONField(null=True,blank=True)
    type_of_question = models.CharField(max_length=255,null=True)
    question_text = models.TextField(null=True)
    correct_option = models.BigIntegerField(null=True)
    time_to_solve = models.CharField(max_length=255,null=True)
    marks = models.CharField(max_length=255,null=True)
    difficulty_level = models.CharField(max_length=255,null=True)
    tags = models.TextField(null=True)
    note = models.TextField(null=True)
    is_archive = models.BooleanField(default=False)
    archive_reason = models.TextField(null=True)
    is_duplicate = models.BooleanField(default=False)
    tc_id = models.CharField(max_length=255,null=True)


class QuestionOption(TrackingModel):
    question_id = models.BigIntegerField(null=True)
    option = models.BigIntegerField(null=True)
    option_answer = models.TextField(null=True)
    option_image = models.TextField(null=True)
    
class QuestionImages(TrackingModel):
    question_id = models.BigIntegerField(null=True)
    image = models.TextField(null=True)

class QuestionLike(TrackingModel):
    question_id = models.BigIntegerField(null=True)
    actionby = models.CharField(max_length=255, null=True, blank=True)
    is_like = models.BooleanField(default=False)
    is_dislike = models.BooleanField(default=False)
    dislike_reason = models.TextField(null=True)

class DuplicateQuestion(TrackingModel):
    question_id = models.BigIntegerField(null=True)
    duplicate_of = models.JSONField(null=True,blank=True)
    course_id = models.BigIntegerField(null=True,blank=True)
    module_id = models.BigIntegerField(null=True,blank=True)
    severity_level = models.CharField(max_length=255,null=True)
    type_of_question = models.CharField(max_length=255,null=True)
