from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
import requests
from helpers.validations import *
# Create your views here.

login_url = hostURL + '/api/adminauth/login'
logout_url = hostURL + '/api/adminauth/logout'
user_details_url = hostURL + '/api/adminauth/user-details'
training_details_url = hostURL + '/api/adminauth/training-center-details'
user_upload_docs_url = hostURL + '/api/adminauth/user-upload-docs'
main_role_document_list_url = hostURL + '/api/adminauth/main-role-document-list'
sub_training_center_list = hostURL + '/api/adminauth/sub-training-center-list'
training_center_list = hostURL + '/api/adminauth/training-center-list'

faculty_list_url = hostURL + '/api/adminauth/faculty-list'
language_list_url = hostURL + '/api/master/languages-list'
branch_list_url =  hostURL + '/api/master/branch-list'
all_tc_list_url =  hostURL + '/api/adminauth/all-training-center-list'
branch_info_url =  hostURL + '/api/master/branch-list'
branch_detail_url =  hostURL + '/api/master/branch-detail'
country_details_urls = hostURL + '/api/candidate/country-list'
non_eligible_country_details_urls = hostURL + '/api/candidate/non-eligible-country-list'
course_url = hostURL + '/api/course/course-list'

def EligibilityRulesList(request):

    country_request = requests.get(non_eligible_country_details_urls)
    country_response = country_request.json()

    
    return render(request,'org_html/rules/eligibility-rules.html',{'country':country_response['data']})
