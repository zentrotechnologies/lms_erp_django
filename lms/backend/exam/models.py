from django.db import models
from helpers.models import *

class ExamSet(TrackingModel): #Exam 
    name = models.CharField(max_length=255)
    course = models.BigIntegerField(null=True)
    time_to_solve = models.BigIntegerField(default=0)
    difficulty_level = models.CharField(max_length=255,null=True)
    question_type = models.CharField(max_length=255,null=True)
    exam_mode = models.BigIntegerField(null=True)
    total_marks = models.FloatField(default=0)
    passing_marks = models.FloatField(default=0)
    description = models.TextField(null=True)
    no_of_questions = models.BigIntegerField(default=0)
    no_of_sets = models.BigIntegerField(default=0)
    module_list = models.TextField(null=True)
    training_center = models.CharField(max_length=255,null=True,blank=True)
    easy_questions_percentage = models.BigIntegerField(default=0)
    medium_questions_percentage = models.BigIntegerField(default=0)
    hard_questions_percentage = models.BigIntegerField(default=0)

class QuestionExamSet(TrackingModel):  #Exam set
    exam_id = models.BigIntegerField(null=True)
    question_id = models.JSONField(null=True,blank=True)
    set_number = models.CharField(max_length=255,null=True)
    
class ScheduleExam(TrackingModel):
    training_center = models.CharField(max_length=255) 
    course = models.BigIntegerField(null=True)
    schedule = models.BigIntegerField(null=True)
    exam_set = models.BigIntegerField(null=True)
    exam_mode = models.BigIntegerField(null=True)
    mandatory_questions = models.BigIntegerField(default=0)
    total_marks = models.BigIntegerField(default=0)
    passing_marks = models.BigIntegerField(default=0)
    exam_duration = models.BigIntegerField(default=0)
    start_time = models.CharField(max_length=255) 
    end_time = models.CharField(max_length=255) 
    schedule_exam_date = models.DateField(null=True)
    exam_note = models.TextField(null=True)
    attempt = models.BigIntegerField(null=True) #attempt number for the exam

class ExamCandidateSetRelation(TrackingModel):
    exam_schedule_id = models.BigIntegerField(null=True)
    exam_id = models.BigIntegerField(null=True)
    exam_set = models.BigIntegerField(null=True)
    candidate_id = models.CharField(max_length=255) 
    exam_link = models.TextField(null=True) 



class ExamCandidateResult(TrackingModel):
    exam_schedule_id = models.BigIntegerField(null=True)
    exam_id = models.BigIntegerField(null=True)
    exam_set = models.BigIntegerField(null=True)
    candidate_id = models.CharField(max_length=255,null=True) 
    start_created_time = models.DateTimeField(null=True)
    end_created_time = models.DateTimeField(null=True)
    all_data = models.TextField(null=True,blank=True)
    marks_obtained = models.FloatField(default=0)
    is_passed = models.BooleanField(default=False)
    certificate_link = models.TextField(default='')
    final_submit = models.BooleanField(default=False)

class ExamCandidateResultAnswer(TrackingModel):
    exam_candidate_result_id = models.BigIntegerField(null=True,blank=True)
    question_data = models.TextField(null=True,blank=True)
    question_id =  models.BigIntegerField(null=True,blank=True)
    candidate_option_id = models.BigIntegerField(null=True,blank=True)
    candidate_option_answer = models.TextField(null=True,blank=True)
    mark_for_review = models.BooleanField(default=False)
    correct_answer_option = models.BigIntegerField(null=True,blank=True)
    marks = models.FloatField(default=0)
    
class CertificateTemplateMaster(TrackingModel):
    tc_id = models.CharField(max_length=255) 
    tc_name = models.CharField(max_length=255) 
    template_name = models.CharField(max_length=255) 
    language = models.CharField(max_length=255,default='English') 
    tc_logo = models.TextField(null=True)
    email = models.CharField(max_length=255,null=True) 
    mobilenumber = models.CharField(max_length=255,null=True) 
    address_line_one = models.TextField(null=True,blank=True) 
    address_line_two = models.TextField(null=True,blank=True) 
    country = models.TextField(null=True,blank=True) 
    state = models.CharField(max_length=150,null=True, blank=True) 
    city = models.CharField(max_length=150,null=True, blank=True) 
    pincode = models.CharField(max_length=150,null=True, blank=True) 
    auth_sign = models.TextField(null=True)
    auth_person_name = models.CharField(max_length=150,null=True, blank=True) 
    

















class MockExamQuestionSet(TrackingModel):
    question_id = models.JSONField(null=True,blank=True)
    set_number = models.CharField(max_length=255,null=True)
    difficulty_level = models.CharField(max_length=255,null=True)
    course = models.BigIntegerField(null=True)
    exam_schedule_id = models.BigIntegerField(null=True) #ScheduleExam
    exam_id = models.BigIntegerField(null=True) #ScheduleExam
    training_center = models.CharField(max_length=255,null=True,blank=True)
    no_of_questions = models.BigIntegerField(default=0)
    exam_duration= models.BigIntegerField(default=0)
    mandatory_questions = models.BigIntegerField(default=0)


class MockExamCandidateResult(TrackingModel):
    exam_schedule_id = models.BigIntegerField(null=True)
    exam_id = models.BigIntegerField(null=True)
    mock_exam_set = models.BigIntegerField(null=True)
    candidate_id = models.CharField(max_length=255,null=True) 
    start_created_time = models.DateTimeField(null=True)
    end_created_time = models.DateTimeField(null=True)
    all_data = models.TextField(null=True,blank=True)
    marks_obtained = models.FloatField(default=0)
    is_passed = models.BooleanField(default=False)
    final_submit = models.BooleanField(default=False)

class MockExamCandidateResultAnswer(TrackingModel):
    mock_exam_candidate_result_id = models.BigIntegerField(null=True,blank=True)
    question_data = models.TextField(null=True,blank=True)
    question_id =  models.BigIntegerField(null=True,blank=True)
    candidate_option_id = models.BigIntegerField(null=True,blank=True)
    candidate_option_answer = models.TextField(null=True,blank=True)
    mark_for_review = models.BooleanField(default=False)
    correct_answer_option = models.BigIntegerField(null=True,blank=True)
    marks = models.FloatField(default=0)
  
    

