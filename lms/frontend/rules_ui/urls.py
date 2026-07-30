from django.contrib import admin
from django.urls import path
from .import views as v


urlpatterns = [
    path('eligibility-rules-list',v.EligibilityRulesList,name="eligibility-rules-list"),


    
]