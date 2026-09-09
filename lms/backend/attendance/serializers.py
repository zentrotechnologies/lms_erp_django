from rest_framework import serializers
from .models import *
from datetime import datetime, time
from master.models import Branch
class CandidateAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateAttendance
        fields ="__all__"


class LeaveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = "__all__"


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class LeaveTypeAllotmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypeAllotment
        fields = "__all__"