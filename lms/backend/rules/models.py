from django.db import models
from helpers.models import TrackingModel


# Legacy Navy eligibility tables are retained for backward compatibility only.
class GeneralEligibilityRules(TrackingModel):
    country_id = models.BigIntegerField(null=True, blank=True)
    country_name = models.CharField(max_length=255, null=True, blank=True)
    rule_no = models.BigIntegerField(null=True, blank=True)


class GeneralEligibilityDepartmentRankCombinations(TrackingModel):
    general_eligibility_rule_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    departments = models.BigIntegerField(null=True, blank=True)
    ranks = models.BigIntegerField(null=True, blank=True)
    minimum_age = models.PositiveIntegerField(null=True, blank=True)


class GeneralEligibilityEducationalQualifications(TrackingModel):
    general_eligibility_rule_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    educational_qualification_id = models.BigIntegerField(null=True, blank=True)


class GeneralEligibilityMandatoryDocuments(TrackingModel):
    general_eligibility_rule_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    document_id = models.BigIntegerField(null=True, blank=True)
    document_name = models.CharField(max_length=255, null=True, blank=True)


class AdmissionEligibilityRule(TrackingModel):
    academic_year_id = models.BigIntegerField(db_index=True)
    program_id = models.BigIntegerField(db_index=True)
    rule_name = models.CharField(max_length=255)
    minimum_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    minimum_age = models.PositiveIntegerField(null=True, blank=True)
    maximum_age = models.PositiveIntegerField(null=True, blank=True)
    qualification_id = models.BigIntegerField(null=True, blank=True)
    required_documents = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
