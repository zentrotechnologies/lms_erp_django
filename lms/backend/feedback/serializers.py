from rest_framework import serializers
from .models import *

class FeedbackCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackCategory
        fields ="__all__"
class FeedbackSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSubCategory
        fields ="__all__"
        
        

class FeedbackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields ="__all__"
        
        

class FeedbackActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackActivation
        fields ="__all__"
        

        