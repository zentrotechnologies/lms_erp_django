from rest_framework import serializers
from .models import *

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields ="__all__"
        
        
class CandidateDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateDocuments 
        fields ="__all__"


class AdmissionApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionApplication
        fields = "__all__"


class CandidateEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateEducation
        fields = "__all__"


class CandidatePhotoSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatePhotoSignature
        fields = "__all__"
        
   