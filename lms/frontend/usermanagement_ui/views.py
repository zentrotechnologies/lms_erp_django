from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
import requests
from helpers.validations import *
# Create your views here.

role_url = hostURL + '/api/usermanagement/role-list'
add_member_url = hostURL + '/api/usermanagement/add-member'
userrole_url = hostURL + '/api/usermanagement/role-list'
countrylist_url = hostURL + '/api/adminauth/country-list'
member_url = hostURL + '/api/usermanagement/member-list'
menu_list_url = hostURL + "/api/adminauth/menu-details"
rolepermissionURL = hostURL + "/api/adminauth/get-permission"
permsaveURL = hostURL + "/api/adminauth/add-permission"

def role(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        role_request = requests.get(role_url,headers=headers)
        role_response = role_request.json()
        return render(request,'org_html/user_management/role.html',{'role':role_response['data']})
    else:
        return redirect('organisation:login')
    

def member(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
    
        member_request = requests.get(member_url,headers=headers)
        member_response = member_request.json()
        return render(request,'org_html/user_management/member.html',{'member':member_response['data']})
    else:
        return redirect('organisation:login')


def add_member(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        userrole_request = requests.get(userrole_url,headers=headers)
        userrole_response = userrole_request.json()

        member_request = requests.get(member_url,headers=headers)
        member_response = member_request.json()
        
        return render(request,'org_html/user_management/add-member.html',{'userrole':userrole_response['data'],'member':member_response['data']})
    else:
        return redirect('organisation:login')



def update_member(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}

        userrole_request = requests.get(userrole_url,headers=headers)
        userrole_response = userrole_request.json()
        
        singlemember_request = requests.post(member_url,headers=headers,data={'id':id})
        singlemember_response = singlemember_request.json()
      
        return render(request,'org_html/user_management/edit-member.html',{'userrole':userrole_response['data'],'singledetails':singlemember_response['data'],'member':singlemember_response['memberdata']})
    else:
        return redirect('organisation:login')
    
    

def permission(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        if request.method == 'POST':
            data['Role_id'] = request.POST.get('role')
            data['menu_id'] = request.POST.getlist('menuItemCheck')
            permresponse =  requests.post(permsaveURL,data=data,headers=headers) 
            resp = permresponse.json()
            if resp['n'] == 1:
                messages.success(request,resp['msg'])
                return redirect('usermanagement_ui:permission')
            else:
                messages.error(request,resp['msg'])
                return redirect('usermanagement_ui:permission')
        else:
            user_type = request.session.get('user_type')
            
            role_request = requests.get(role_url,headers=headers)
            role_response = role_request.json()

            menu_list_request = requests.get(menu_list_url,params={'user_type':user_type})
            menu_list_response = menu_list_request.json()
        
            return render(request,'org_html/user_management/permission.html',{'menulist':menu_list_response['data'],'role':role_response['data']})
    else:
        return redirect('organisation:login')
    
def getpermissionbyrole(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        data['roleid'] = request.POST.get('roleID')
        permissionresp = requests.post(rolepermissionURL,data=data,headers=headers) 
        permission = permissionresp.json()
        return HttpResponse(json.dumps(permission),content_type='application/json')
    else:
        return redirect('organisation:login')