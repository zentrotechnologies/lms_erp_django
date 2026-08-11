from rest_framework import serializers
from .models import *

class EnrollmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollments
        fields ="__all__"
        
        
class EnrollPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollPayment
        fields = "__all__"


class CandidateSubjectSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSubjectSelection
        fields = "__all__"
