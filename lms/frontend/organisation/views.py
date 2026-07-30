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
course_url = hostURL + '/api/course/course-list'
rolepermissionURL = hostURL + "/api/adminauth/get-permission"
org_all_training_center_list_url = hostURL + "/api/adminauth/org-all-training-center-list"
certificate_template_list_url = hostURL + "/api/exam/template-list"
view_all_certificate_url = hostURL + "/api/exam/view-all-certificate"


def login(request):
    if request.method == "POST":
        data={}
        data['email'] = request.POST.get('email')
        data['password'] = request.POST.get('password')
 
        login_request = requests.post(login_url,data=data)
        login_response = login_request.json()
     
        if login_response['n'] == 1:
            if login_response['data']['user_type'] == 2:
                menu_list_request = requests.post(rolepermissionURL,data={'roleid':login_response['data']['role']})
                menu_list_response = menu_list_request.json()   

                request.session['og_token'] = login_response['token']
                request.session['user_type'] = login_response['data']['user_type']
                request.session['is_parent_training_center'] = login_response['data']['is_parent_training_center']
                request.session['parent_training_center'] = login_response['data']['parent_training_center']
                request.session['user_id'] = login_response['data']['id']
                request.session['role'] = login_response['data']['role']

                request.session['name'] = (login_response['data'].get('first_name') or '') + ' ' + (login_response['data'].get('last_name') or '')
                request.session['email'] = login_response['data']['email']
                
                request.session['usertype_menuItems'] = login_response['menuItems']
                request.session['menuItems'] = menu_list_response['data']
                
                if login_response['data']['user_type'] == 5:
                    return redirect('organisation:dashboard')
                else:
                    return redirect('organisation:dashboard')    
            else:
                messages.warning(request,'Cant access the site')
                return redirect('organisation:login') 
        else:
            messages.warning(request,login_response['msg'])
            return redirect('organisation:login')
        

    return render(request,'sign-in.html')

def logout(request):
        try:

            og_token = request.session.get('og_token')
            if og_token:

                token = 'Bearer {}'.format(og_token)
                headers = {'Authorization':token}
               
                logout_request = requests.post(logout_url,headers=headers,data={'token':og_token})
                logout_response = logout_request.json()
                if logout_response['n'] == 1: 
                    del request.session['og_token']
                    del request.session['menuItems']
                    return redirect('organisation:login')
                else:
                    return redirect('organisation:login')
            else:
                messages.warning(request,"Login again")
                return redirect('organisation:login')

        except Exception as e:
            # return HttpResponse('logout failed')
            messages.warning(request,"logout failed")
            return redirect('organisation:login')

        

def org_base(request):
    return render(request,'org_base.html')


def dashboard(request):
    return render(request,'org_html/admin/dashboard.html')


def addtrainingcenter(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        courses_request = requests.post(course_url,headers=headers,data={'course_status':'Approved'})
        courses_response = courses_request.json()
        context={
                'courses':courses_response['data'],
            }

        return render(request,'org_html/trainingcenter/add-training-center.html',context)
    else:
        return redirect('organisation:login')



def addsubtrainingcenter(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}

        parent_training_center_request = requests.get(training_center_list,headers=headers)
        parent_training_center_response = parent_training_center_request.json()
        context={
                'parent_training_centers':parent_training_center_response['data'],
            }

        return render(request,'org_html/trainingcenter/add-sub-training-center.html',context)
    else:
        return redirect('organisation:login')
    
def updatesubtrainingcenter(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        if request.method =="POST":
            user_id = request.POST.get('user_id')
            doc_id = request.POST.getlist('doc_id')
            doc_name = request.POST.getlist('doc_name')
            data = {}
            file = {}
            
            uploaded_data = []  
            
            files_dict  = []
            uploaded_files = request.FILES.getlist('docsUpload')  
            for file_field in uploaded_files:
                files_dict.append(("docsUpload",file_field))
         
            
                
            user_upload_docs_request = requests.post(
                user_upload_docs_url, 
                headers=headers, 
                files=files_dict,
                data={"user_id": user_id,"doc_id":doc_id,"doc_name":doc_name} 
            )     
            user_upload_docs_response = user_upload_docs_request.json()

            if user_upload_docs_response['n'] == 1:
                messages.success(request,user_upload_docs_response['msg'])
            else:
                messages.warning(request,user_upload_docs_response['msg'])

            return redirect('organisation:subtrainingcenterlist')
                        

        else:
            user_request = requests.post(training_details_url,headers=headers,data={'id':id})       
            user_response = user_request.json()
            courses_request = requests.post(course_url,headers=headers,data={'course_status':'Approved'})
            courses_response = courses_request.json()
            parent_training_center_request = requests.get(training_center_list,headers=headers)
            parent_training_center_response = parent_training_center_request.json()
            return render(request,'org_html/trainingcenter/edit-sub-training-center.html',{
                'user_data':user_response['data'],
                'courses':courses_response['data'],
                'parent_training_centers':parent_training_center_response['data'],
            })
        
    else:
        return redirect('organisation:login')
    

def TrainingCenterProfile(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        user_request = requests.post(training_details_url,headers=headers,data={'id':id})       
        user_response = user_request.json()

        
        return render(request,'org_html/reports/training-center-profile.html',{

            'training_center':user_response['data']
            
            })
    else:
        return redirect('organisation:login')



def updatetrainingcenter(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        if request.method =="POST":
            user_id = request.POST.get('user_id')
            doc_id = request.POST.getlist('doc_id')
            doc_name = request.POST.getlist('doc_name')
            data = {}
            file = {}
            
            uploaded_data = []  
            
            files_dict  = []
            uploaded_files = request.FILES.getlist('docsUpload')  
            for file_field in uploaded_files:
                files_dict.append(("docsUpload",file_field))
         
            
                
            user_upload_docs_request = requests.post(
                user_upload_docs_url, 
                headers=headers, 
                files=files_dict,
                data={"user_id": user_id,"doc_id":doc_id,"doc_name":doc_name} 
            )     
            user_upload_docs_response = user_upload_docs_request.json()
            if user_upload_docs_response['n'] == 1:
                messages.success(request,user_upload_docs_response['msg'])
            else:
                messages.warning(request,user_upload_docs_response['msg'])     
                       
            return redirect('organisation:trainingcenterlist')
            
        else:
            user_request = requests.post(training_details_url,headers=headers,data={'id':id})       
            user_response = user_request.json()
            courses_request = requests.post(course_url,headers=headers,data={'course_status':'Approved'})
            courses_response = courses_request.json()
            return render(request,'org_html/trainingcenter/edit-training-center.html',{'user_data':user_response['data'],'courses':courses_response['data'],})
        
    else:
        return redirect('organisation:login')
    

def trainingcenterlist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        training_center_request = requests.get(training_center_list,headers=headers)       
        training_center_response = training_center_request.json()
        return render(request,'org_html/trainingcenter/training-center-list.html',{'training_center_list':training_center_response['data']})
    else:
        return redirect('organisation:login')
    
def subtrainingcenterlist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        subtraining_center_request = requests.get(sub_training_center_list,headers=headers)       
        subtraining_center_response = subtraining_center_request.json()
        return render(request,'org_html/trainingcenter/sub-training-center-list.html',{'training_center_list':subtraining_center_response['data']})
    else:
        return redirect('organisation:login')
    
def templatelist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        
        training_center_request = requests.get(org_all_training_center_list_url,headers=headers)       
        training_center_response = training_center_request.json()
        certificate_template_request = requests.post(certificate_template_list_url,headers=headers)       
        certificate_template_response = certificate_template_request.json()
        return render(request,'org_html/certificate/templates.html',{'training_center_list':training_center_response['data'],'template_list':certificate_template_response['data']})
    else:
        return redirect('organisation:login')
    
def viewallcertificate(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        certificate_all_request = requests.post(view_all_certificate_url,headers=headers)       
        certificate_all_response = certificate_all_request.json()
        return render(request,'org_html/certificate/view-all-certificate.html',{'certificate_list':certificate_all_response['data']})
    else:
        return redirect('organisation:login')