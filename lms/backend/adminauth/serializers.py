from rest_framework import serializers
from .models import *

class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAdmin
        fields ="__all__"
        
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'

class MainRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainRoles
        fields = '__all__'

class UserDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        fields = '__all__'

class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Authority
        fields = '__all__'

        
class MenuDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuDetails 
        fields ="__all__"
        

class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permissions
        fields = "__all__"
        


class CustomUserAdminSerializer(serializers.ModelSerializer):

    designation_name = serializers.SerializerMethodField()
    def get_designation_name(self, obj):
        if str(obj.designation) is not None and str(obj.designation) !='':
            cor_obj=Country.objects.filter(id=obj.designation,isActive=True).first()
            if cor_obj is not None:
                return cor_obj.name
            else:
                return ''
        else:
            return ''

    class Meta:
        model = UserAdmin
        fields ="__all__"