from rest_framework import serializers
from .models import *

class UsereRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsereRole
        fields ="__all__"
        

# class MemberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Member
#         fields ="__all__"