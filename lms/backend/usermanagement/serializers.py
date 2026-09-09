from rest_framework import serializers
from .models import *

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = "__all__"


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = "__all__"


class ParentTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentToken
        fields = "__all__"


class UsereRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsereRole
        fields ="__all__"
        

# class MemberSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Member
#         fields ="__all__"