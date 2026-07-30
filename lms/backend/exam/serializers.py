from rest_framework import serializers
from .models import *

class ExamSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSet
        fields ="__all__"

class QuestionExamSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionExamSet
        fields ="__all__"

class ScheduleExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleExam
        fields ="__all__"

class ExamCandidateSetRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCandidateSetRelation
        fields ="__all__"

class ExamCandidateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCandidateResult
        fields ="__all__"

class ExamCandidateResultAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCandidateResultAnswer
        fields ="__all__"

class CertificateTemplateMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplateMaster
        fields ="__all__"
class MockExamQuestionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockExamQuestionSet
        fields ="__all__"
class MockExamCandidateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockExamCandidateResult
        fields ="__all__"
class MockExamCandidateResultAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockExamCandidateResultAnswer
        fields ="__all__"





