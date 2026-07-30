from django.shortcuts import render,redirect
from django.contrib import messages
import requests
from helpers.validations import *
# Create your views here.

course_url = hostURL + '/api/course/course-list'
sub_cat_url = hostURL + '/api/master/subcat-category-list'


add_course_url = hostURL + '/api/course/add-course'
course_details_url = hostURL + '/api/course/get-course-details'
trainingmode_url = hostURL + '/api/course/training-modelist'

language_url = hostURL + '/api/master/languages-list'
category_url = hostURL + '/api/master/category-list'
department_url = hostURL + '/api/master/department-list'


def courselist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        data['course_status'] = 'Approved'
        # course_request = requests.post(course_url,headers=headers,data=data)
        # course_response = course_request.json()
        return render(request,'org_html/course/list-of-course.html')
    else:
        return redirect('organisation:login')
    

def addcourse(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        data['course_status'] = 'Approved'
        course_request = requests.post(course_url,headers=headers,data=data)
        course_response = course_request.json()

        trainingmode_request =  requests.get(trainingmode_url,headers=headers)
        trainingmode_response = trainingmode_request.json()

        language_request =  requests.get(language_url,headers=headers)
        language_response = language_request.json()

       

        return render(request,'org_html/course/courses-add-course.html',{'course':course_response['data'],'TrainingMode':trainingmode_response['data'],'languages':language_response['data']})
    else:
        return redirect('organisation:login')
    

def updatecourse(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        if request.method =="POST":
            return redirect('trainingcenter:updatetrainingcenter')
        else:
            data={}
            data['course_status'] = 'Approved'
            courselist_request = requests.post(course_url,headers=headers,data=data)
            courselist_response = courselist_request.json()

            course_request = requests.post(course_details_url,headers=headers,data={'id':id})       
            course_response = course_request.json()

            trainingmode_request =  requests.get(trainingmode_url,headers=headers)
            trainingmode_response = trainingmode_request.json()

            language_request =  requests.get(language_url,headers=headers)
            language_response = language_request.json()

            category_request =  requests.get(sub_cat_url,headers=headers)
            catgeory_response = category_request.json()

            department_request =  requests.get(department_url,headers=headers)
            department_response = department_request.json()
            
            return render(request,'org_html/course/course-update.html',{'course_data':course_response['data'],'course':courselist_response['data'],'TrainingMode':trainingmode_response['data'],'languages':language_response['data'],'catgeorylist':catgeory_response['data'],'departmentlist':department_response['data']})
    else:
        return redirect('organisation:login')
    
def studymaterial(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        data['course_status'] = 'Approved'
        courselist_request = requests.post(course_url,headers=headers,data=data)
        courselist_response = courselist_request.json()
        return render(request,'org_html/course/study-material.html',{'course_list':courselist_response['data']})
    else:
        return redirect('organisation:login')