from rest_framework import serializers
from .models import *

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields ="__all__"

class QuestionImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImages
        fields ="__all__"

class customised_QuestionImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionImages
        fields =['id','question_id','image']

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields ="__all__"


class QuestionLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionLike
        fields ="__all__"

class DuplicateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DuplicateQuestion
        fields ="__all__"