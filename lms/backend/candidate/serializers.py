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
        
   