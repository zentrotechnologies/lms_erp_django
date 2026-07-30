from django.db import models
from helpers.models import *
from django.utils.translation import gettext_lazy as _


# Create your models here.


class GeneralEligibilityRules(TrackingModel): #company multiple rules
    country_id = models.BigIntegerField(null=True,blank=True)
    country_name =  models.CharField(max_length=255,null=True,blank=True)
    rule_no = models.BigIntegerField(null=True,blank=True)

class GeneralEligibilityDepartmentRankCombinations(TrackingModel):
    general_eligibility_rule_id = models.BigIntegerField(null=True,blank=True)
    departments =  models.BigIntegerField(null=True,blank=True)
    ranks =  models.BigIntegerField(null=True,blank=True)
    minimum_age =  models.CharField(max_length=255,null=True,blank=True)



class GeneralEligibilityEducationalQualifications(TrackingModel):
    general_eligibility_rule_id = models.BigIntegerField(null=True,blank=True)
    educational_qualification_id = models.BigIntegerField(null=True,blank=True)


class GeneralEligibilityMandatoryDocuments(TrackingModel):
    general_eligibility_rule_id = models.BigIntegerField(null=True,blank=True)
    document_id = models.BigIntegerField(null=True,blank=True)
    document_name =  models.CharField(max_length=255,null=True,blank=True)


# class CourseSpecificEligibilityRules(TrackingModel):
#     country_id = models.BigIntegerField(null=True,blank=True)
#     courses =  models.JSONField(null=True,blank=True)
#     ranks =  models.JSONField(null=True,blank=True)
#     prior_certification =  models.JSONField(null=True,blank=True)
#     sea_service_experience  =  models.CharField(max_length=255,null=True,blank=True)
#     passport_required = models.BooleanField(default=False)
#     seafarer_id_or_CDC_required = models.BooleanField(default=False)
#     medical_fitness_certificate_required = models.BooleanField(default=False)
#     basic_STCW_course_completion_required = models.BooleanField(default=False)


# class PriorCertification(TrackingModel):
#     certification_name =  models.CharField(max_length=555,null=True,blank=True)

# class RankProgressionEligibilityRules(TrackingModel):
#     country_id = models.BigIntegerField(null=True,blank=True)
#     ranks =  models.JSONField(null=True,blank=True)
#     prior_certification =  models.JSONField(null=True,blank=True)
#     sea_service_experience  =  models.CharField(max_length=255,null=True,blank=True)
#     passport_required = models.BooleanField(default=False)
#     seafarer_id_or_CDC_required = models.BooleanField(default=False)
#     medical_fitness_certificate_required = models.BooleanField(default=False)
#     basic_STCW_course_completion_required = models.BooleanField(default=False)

























