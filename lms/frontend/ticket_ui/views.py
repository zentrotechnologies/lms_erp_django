from django.shortcuts import render,redirect
from django.contrib import messages
import requests
from helpers.validations import *
# Create your views here.

ticket_url = hostURL + '/api/ticket/ticket-list'
add_ticket_url = hostURL + '/api/ticket/add-ticket'
ticket_details_url = hostURL + '/api/ticket/get-ticket-details'
get_ticket_by_id_url = hostURL + '/api/ticket/get-ticket-by-id'

course_url = hostURL + '/api/course/course-list'
branches_url = hostURL + '/api/master/branch-list'
all_training_center_url = hostURL + '/api/adminauth/all-training-center-list'
faculty_list_url = hostURL + '/api/adminauth/faculty-list'
member_url = hostURL + '/api/usermanagement/member-list'
ticket_info_url = hostURL + '/api/ticket/ticket-info'
userlist_url= hostURL + '/api/ticket/assign-user-list'
assign_userlist_url = hostURL + '/api/ticket/assign-ticket-user-list'

# tag_list_url
department_list_url = hostURL + '/api/master/department-list'
category_list_url = hostURL + '/api/master/category-list'
ticket_category_list_url= hostURL + '/api/master/ticket-category-list'

def ticketlist(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        ticket_category_request = requests.get(ticket_category_list_url,headers=headers)
        ticket_category_response = ticket_category_request.json()
        context={
          'ticket_category':ticket_category_response['data']
            }
        return render(request,'org_html/ticket/list-of-ticket.html',context)
    else:
        return redirect('organisation:login')
    
def ticketinfo(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        ticket_info_request = requests.post(ticket_info_url,headers=headers,data={'ticket_id':id})
        ticket_info_response = ticket_info_request.json()


        userlist_request = requests.post(userlist_url,headers=headers,data={'ticket':id})
        userlist_response = userlist_request.json()

        assign_userlist_request = requests.post(assign_userlist_url,headers=headers,data={'ticket':id})
        assign_userlist_response = assign_userlist_request.json()


        category_list_request = requests.get(ticket_category_list_url,headers=headers,)
        category_list_response = category_list_request.json()
        department_list_request = requests.get(department_list_url,headers=headers,)
        department_list_response = department_list_request.json()


        
        context={

                'ticket':ticket_info_response['data'],
                'userlist':userlist_response['data'],
                'categories':category_list_response['data'],
                'departments':department_list_response['data'],
                'assignusers':assign_userlist_response['data'],

            }
        return render(request,'org_html/ticket/ticket-info.html',context)
    else:
        return redirect('organisation:login')

