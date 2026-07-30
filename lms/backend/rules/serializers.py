from rest_framework import serializers
from .models import *

class GeneralEligibilityRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralEligibilityRules
        fields ="__all__"