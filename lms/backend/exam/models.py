from django.db import models
from helpers.models import TrackingModel


class ExamSet(TrackingModel):
    name = models.CharField(max_length=255)
    course = models.BigIntegerField(null=True, db_index=True)
    time_to_solve = models.PositiveIntegerField(default=0)
    difficulty_level = models.CharField(max_length=50, null=True)
    question_type = models.CharField(max_length=50, null=True)
    exam_mode = models.BigIntegerField(null=True)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    passing_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(null=True)
    no_of_questions = models.PositiveIntegerField(default=0)
    no_of_sets = models.PositiveIntegerField(default=0)
    module_list = models.TextField(null=True)
    training_center = models.CharField(max_length=255, null=True, blank=True)
    easy_questions_percentage = models.PositiveIntegerField(default=0)
    medium_questions_percentage = models.PositiveIntegerField(default=0)
    hard_questions_percentage = models.PositiveIntegerField(default=0)

    # College exam scope
    academic_year_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    program_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    semester_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    class_group_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    exam_type = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=30, default="DRAFT", db_index=True)


class QuestionExamSet(TrackingModel):
    exam_id = models.BigIntegerField(null=True, db_index=True)
    question_id = models.JSONField(default=list, blank=True)
    set_number = models.CharField(max_length=50, null=True)


class ScheduleExam(TrackingModel):
    training_center = models.CharField(max_length=255, null=True, blank=True)
    course = models.BigIntegerField(null=True, db_index=True)
    schedule = models.BigIntegerField(null=True, db_index=True)
    exam_set = models.BigIntegerField(null=True, db_index=True)
    exam_mode = models.BigIntegerField(null=True)
    mandatory_questions = models.PositiveIntegerField(default=0)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    passing_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    exam_duration = models.PositiveIntegerField(default=0)
    start_time = models.CharField(max_length=255, null=True, blank=True)
    end_time = models.CharField(max_length=255, null=True, blank=True)
    schedule_exam_date = models.DateField(null=True, db_index=True)
    exam_note = models.TextField(null=True)
    attempt = models.PositiveIntegerField(default=1)


class ExamCandidateSetRelation(TrackingModel):
    exam_schedule_id = models.BigIntegerField(null=True, db_index=True)
    exam_id = models.BigIntegerField(null=True, db_index=True)
    exam_set = models.BigIntegerField(null=True, db_index=True)
    candidate_id = models.CharField(max_length=255, db_index=True)
    exam_link = models.TextField(null=True)


class ExamCandidateResult(TrackingModel):
    exam_schedule_id = models.BigIntegerField(null=True, db_index=True)
    exam_id = models.BigIntegerField(null=True, db_index=True)
    exam_set = models.BigIntegerField(null=True, db_index=True)
    candidate_id = models.CharField(max_length=255, null=True, db_index=True)
    start_created_time = models.DateTimeField(null=True, blank=True)
    end_created_time = models.DateTimeField(null=True, blank=True)
    all_data = models.JSONField(default=dict, blank=True)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_passed = models.BooleanField(default=False)
    grade = models.CharField(max_length=20, null=True, blank=True)
    certificate_link = models.TextField(default="", blank=True)
    final_submit = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam_schedule_id", "candidate_id"],
                name="uniq_exam_schedule_candidate_result",
            )
        ]


class ExamCandidateResultAnswer(TrackingModel):
    exam_candidate_result_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    question_data = models.JSONField(default=dict, blank=True)
    question_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    candidate_option_id = models.BigIntegerField(null=True, blank=True)
    candidate_option_answer = models.TextField(null=True, blank=True)
    mark_for_review = models.BooleanField(default=False)
    correct_answer_option = models.BigIntegerField(null=True, blank=True)
    marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)


class CertificateTemplateMaster(TrackingModel):
    tc_id = models.CharField(max_length=255, null=True, blank=True)
    tc_name = models.CharField(max_length=255, null=True, blank=True)
    template_name = models.CharField(max_length=255)
    language = models.CharField(max_length=255, default="English")
    tc_logo = models.TextField(null=True)
    email = models.EmailField(null=True)
    mobilenumber = models.CharField(max_length=20, null=True)
    address_line_one = models.TextField(null=True, blank=True)
    address_line_two = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    auth_sign = models.TextField(null=True)
    auth_person_name = models.CharField(max_length=150, null=True, blank=True)


class MockExamQuestionSet(TrackingModel):
    question_id = models.JSONField(default=list, blank=True)
    set_number = models.CharField(max_length=255, null=True)
    difficulty_level = models.CharField(max_length=255, null=True)
    course = models.BigIntegerField(null=True, db_index=True)
    exam_schedule_id = models.BigIntegerField(null=True, db_index=True)
    exam_id = models.BigIntegerField(null=True, db_index=True)
    training_center = models.CharField(max_length=255, null=True, blank=True)
    no_of_questions = models.PositiveIntegerField(default=0)
    exam_duration = models.PositiveIntegerField(default=0)
    mandatory_questions = models.PositiveIntegerField(default=0)


class MockExamCandidateResult(TrackingModel):
    exam_schedule_id = models.BigIntegerField(null=True, db_index=True)
    exam_id = models.BigIntegerField(null=True, db_index=True)
    mock_exam_set = models.BigIntegerField(null=True, db_index=True)
    candidate_id = models.CharField(max_length=255, null=True, db_index=True)
    start_created_time = models.DateTimeField(null=True, blank=True)
    end_created_time = models.DateTimeField(null=True, blank=True)
    all_data = models.JSONField(default=dict, blank=True)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_passed = models.BooleanField(default=False)
    final_submit = models.BooleanField(default=False)


class MockExamCandidateResultAnswer(TrackingModel):
    mock_exam_candidate_result_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    question_data = models.JSONField(default=dict, blank=True)
    question_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    candidate_option_id = models.BigIntegerField(null=True, blank=True)
    candidate_option_answer = models.TextField(null=True, blank=True)
    mark_for_review = models.BooleanField(default=False)
    correct_answer_option = models.BigIntegerField(null=True, blank=True)
    marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
