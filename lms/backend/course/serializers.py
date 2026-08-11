from rest_framework import serializers
from .models import *

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields ="__all__"



class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields ="__all__"



class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields ="__all__"

class CourseSubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubjects
        fields ="__all__"


