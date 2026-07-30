from django.shortcuts import render,redirect
from django.contrib import messages
import requests
from helpers.validations import *
# Create your views here.

category_url = hostURL + '/api/master/category-list'
sub_category_url = hostURL + '/api/master/sub-category-list'
department_url = hostURL + '/api/master/department-list'
rank_url = hostURL + '/api/master/rank-list'
documents_url = hostURL + '/api/master/documents-list'
main_role_document_list_url = hostURL + '/api/adminauth/main-role-document-list'
course_url = hostURL + '/api/course/course-list'
course_module_list_url =  hostURL + '/api/course/course-modules-list'
question_dislikes_url =  hostURL + '/api/questionbank/get-dislike-reviews'
s3list_url = hostURL + '/api/master/s3uploads-list'
country_details_urls = hostURL + '/api/candidate/country-list'
vessel_details_url = hostURL + '/api/master/get-vessel-details'
country_url = hostURL + '/api/master/country-list'
feedback_category_url = hostURL + '/api/feedback/feedback-category-list'
ticket_category_url = hostURL + '/api/master/ticket-category-list'
feedback_sub_category_url = hostURL + '/api/master/feedback-sub-category-list'
educational_qualifications_url = hostURL + '/api/master/educational-qualifications-list'
language_list_url = hostURL + '/api/master/languages-list'
viewqueurl = hostURL + '/api/questionbank/question-details'



def categorylist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        category_request = requests.get(category_url,headers=headers)
        category_response = category_request.json()
        return render(request,'org_html/masters/categorylist.html',{'category':category_response['data']})
    else:
        return redirect('organisation:login')
    
def countrylist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        country_request = requests.get(country_url,headers=headers)
        country_response = country_request.json()
        return render(request,'org_html/masters/countrylist.html',{'country':country_response['data']})
    else:
        return redirect('organisation:login')

def feedback_category(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        category_request = requests.get(feedback_category_url,headers=headers)
        feedbackcategory_response = category_request.json()
        
        return render(request,'org_html/masters/feedback-category.html',{'feedbackcategory':feedbackcategory_response['data']})
    else:
        return redirect('organisation:login')
    


def FeedbackSubCategory(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        feedback_category_request = requests.get(feedback_category_url,headers=headers)
        feedback_category_response = feedback_category_request.json()
        feedback_sub_category_request = requests.get(feedback_sub_category_url,headers=headers)
        feedback_sub_category_response = feedback_sub_category_request.json()
        return render(request,'org_html/masters/feedback-sub-category.html',{
            'feedback_sub_category':feedback_sub_category_response['data'],
            'feedback_category':feedback_category_response['data']})
    else:
        return redirect('organisation:login')
     


def ticket_category(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        category_request = requests.get(ticket_category_url,headers=headers)
        ticketcategory_response = category_request.json()
        
        return render(request,'org_html/masters/ticket-category.html',{'ticketcategory':ticketcategory_response['data']})
    else:
        return redirect('organisation:login')


def sub_categorylist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        category_request = requests.get(category_url,headers=headers)
        category_response = category_request.json()
        
        sub_category_request = requests.get(sub_category_url,headers=headers)
        sub_category_response = sub_category_request.json()
        return render(request,'org_html/masters/sub-category.html',{'sub_category':sub_category_response['data'],'category':category_response['data']})
    else:
        return redirect('organisation:login')
    

    
def department(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        department_request = requests.get(department_url,headers=headers)
        department_response = department_request.json()
        return render(request,'org_html/masters/department.html',{'department':department_response['data']})
    else:
        return redirect('organisation:login')
    
    

def rank(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        department_request = requests.get(department_url,headers=headers)
        department_response = department_request.json()
        
        rank_request = requests.get(rank_url,headers=headers)
        rank_response = rank_request.json()
        return render(request,'org_html/masters/rank.html',{'rank':rank_response['data'],'department':department_response['data']})
    else:
        return redirect('organisation:login')
        
def documents(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        documents_request = requests.get(documents_url,headers=headers)
        documents_response = documents_request.json()
        main_role_list = requests.get(main_role_document_list_url,headers=headers)
        mail_role_response = main_role_list.json()
        return render(request,'org_html/masters/documents.html',{'documents':documents_response['data'],'mail_role_data':mail_role_response['data']})
    else:
        return redirect('organisation:login')

    
def add_question_bank(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        data['course_status'] = 'Approved'
        course_request = requests.post(course_url,headers=headers,data=data)
        course_response = course_request.json()

        return render(request,'org_html/questionbank/add-question.html',{'course_list':course_response['data']})
    else:
        return redirect('organisation:login')
    
def view_question_bank(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        data['course_status'] = 'Approved'
        course_request = requests.post(course_url,headers=headers,data=data)
        course_response = course_request.json()

        module_request = requests.get(course_module_list_url,headers=headers)
        module_response = module_request.json()

        reqdata = {}
        reqdata['question_id'] = id
        quedetails_request =  requests.post(viewqueurl,headers=headers,data=reqdata)
        quedetails_response = quedetails_request.json()


        return render(request,'org_html/questionbank/view-question.html',{'course_list':course_response['data'],'que_data':quedetails_response['data'],'module_list':module_response['data']})
    else:
        return redirect('organisation:login')
    
def question_bank(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        return render(request,'org_html/questionbank/question-bank.html')
    else:
        return redirect('organisation:login')
     
def question_bank_validation(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        
        data={}
        data['course_status'] = 'Approved'
        course_request = requests.post(course_url,headers=headers,data=data)
        course_response = course_request.json()

        return render(request,'org_html/questionbank/question-bank-validation.html',{'course_list':course_response['data']})
    else:
        return redirect('organisation:login')
     
def archieve_question(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        return render(request,'org_html/questionbank/archive-questions.html')
    else:
        return redirect('organisation:login')

def bank_summary(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        return render(request,'org_html/questionbank/bank-summary.html')
    else:
        return redirect('organisation:login')
    
    
def dislike_comments(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        que_request = requests.post(question_dislikes_url,headers=headers,data={'id':id})       
        que_response = que_request.json()
        
        return render(request,'org_html/questionbank/dislike-comments.html',{'quedata':que_response['data']['quedata'],'commentslist':que_response['data']['comments']})
    else:
        return redirect('organisation:login')
    

def s3upload(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        data={}
        data['course_status'] = 'Approved'
        course_request = requests.post(course_url,headers=headers,data=data)
        course_response = course_request.json()

        s3_request = requests.get(s3list_url,headers=headers)
        s3_response = s3_request.json()


        return render(request,'org_html/masters/s3files.html',{'course_list':course_response['data'],'s3_list':s3_response['data']})
    else:
        return redirect('organisation:login')


def enquiries(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        return render(request,'org_html/masters/enquiries.html')
    else:
        return redirect('organisation:login')


def vessel_list(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}


        return render(request,'org_html/masters/vessel-list.html')
    else:
        return redirect('organisation:login')
    
def add_vessel(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        category_request = requests.get(category_url,headers=headers)
        category_response = category_request.json()

        country_request = requests.get(country_details_urls)
        country_response = country_request.json()
        
        return render(request,'org_html/masters/add-vessel.html',{'category':category_response['data'],'countrylist':country_response['data']})
    else:
        return redirect('organisation:login')
    
def update_vessel(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        category_request = requests.get(category_url,headers=headers)
        category_response = category_request.json()

        country_request = requests.get(country_details_urls)
        country_response = country_request.json()

        vessel_request = requests.post(vessel_details_url,headers=headers,data={'id':id})       
        vessel_response = vessel_request.json()
        
        return render(request,'org_html/masters/update-vessel.html',{'category':category_response['data'],'countrylist':country_response['data'],'vessel_data':vessel_response['data']})
    else:
        return redirect('organisation:login')
    

def view_vessel(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
       
        vessel_request = requests.post(vessel_details_url,headers=headers,data={'id':id})       
        vessel_response = vessel_request.json()
        
        return render(request,'org_html/masters/view-vessel.html',{'vessel_data':vessel_response['data']})
    else:
        return redirect('organisation:login')
    

def educationalqualificationlist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        educationalqualification_request = requests.get(educational_qualifications_url,headers=headers)
        educationalqualification_response = educationalqualification_request.json()
        return render(request,'org_html/masters/educational-qualification-list.html',{'educationalqualifications':educationalqualification_response['data']})
    else:
        return redirect('organisation:login')

def languagelist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        language_request = requests.get(language_list_url,headers=headers)
        language_response = language_request.json()
        return render(request,'org_html/masters/language-list.html',{'languages':language_response['data']})
    else:
        return redirect('organisation:login')
















