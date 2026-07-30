from rest_framework import serializers
from .models import *
from datetime import datetime, time
from master.models import Branch
class CandidateAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateAttendance
        fields ="__all__"