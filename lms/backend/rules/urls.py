from . import views
from django.urls import include, path


urlpatterns = [

    path('get-eligibile-country-pagination-list',views.GetEligibileCountryPaginationList.as_view(), name='post'),
    path('get-country-rule-form-details',views.GetCountryRuleFormDetails.as_view(), name='post'),
    path('delete-general-eligibility-rules',views.DeleteGeneralEligibilityRules.as_view(), name='post'),
    path('save-country-rule-details',views.SaveCountryRuleDetails.as_view(), name='post'),
    path('get-country-existing-rule-ids',views.GetCountryExistingRuleIds.as_view(), name='post'),
    path('get-unmapped-ranks',views.GetUnmappedRanks.as_view(), name='post'),

]