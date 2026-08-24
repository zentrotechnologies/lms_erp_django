from rest_framework import serializers
from .models import *
from adminauth.models import *
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields ="__all__"
        

class Sub_CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Sub_Category
        fields ="__all__"
        

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields ="__all__"
        

class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields ="__all__"
        
    
class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documents
        fields ="__all__"
        
        
class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields ="__all__"
        
        
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields ="__all__"
        
        
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields ="__all__"
        
class CoordinatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinator
        fields ="__all__"

class S3UploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3Upload
        fields ="__all__"

class EnquiriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiries
        fields ="__all__"

class VesselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vessel
        fields ="__all__"
class EducationalQualificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalQualifications
        fields ="__all__"

class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields ="__all__"

class  CustomBranchSerializer(serializers.ModelSerializer):

    coordinators = serializers.SerializerMethodField()
    def get_coordinators(self, obj):
        if str(obj.id) is not None and str(obj.id) !='':
            cor_obj=Coordinator.objects.filter(branch_id=obj.id,isActive=True).first()
            seri_data=CoordinatorSerializer(cor_obj)
            return seri_data.data
        else:
            return {}   

    country_name = serializers.SerializerMethodField()
    def get_country_name(self, obj):
        if str(obj.country) is not None and str(obj.country) !='':
            cor_obj=Country.objects.filter(id=obj.country,isActive=True).first()
            if cor_obj is not None:

                return cor_obj.name
            else:

                return ''
            
        else:
            return ''
    state_name = serializers.SerializerMethodField()
    def get_state_name(self, obj):
        if str(obj.state) is not None and str(obj.state) !='':
            cor_obj=State.objects.filter(id=obj.state).first()
            if cor_obj is not None:
                return cor_obj.name
            else:
                return ''
        else:
            return ''
         
    class Meta:
        model = Branch
        fields ="__all__"




class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = "__all__"


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"





class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = "__all__"


class ClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = "__all__"















