from rest_framework import serializers
from .models import *

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields ="__all__"

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModules
        fields ="__all__"

class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields ="__all__"

class TrainingModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingMode
        fields ="__all__"

class CourseEligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEligibility
        fields ="__all__"


class rankItemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = rankItemInfo
        fields ="__all__"

class customisedrankItemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = rankItemInfo
        fields =['id','course_id','eligibilityid','rank','mandatory','createdAt','isActive']

