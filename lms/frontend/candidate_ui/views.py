from django.shortcuts import render
# Create your views here.
from django.shortcuts import render,redirect
from django.contrib import messages
import requests
from helpers.validations import *
# Create your views here.

candi_details_urls = hostURL + '/api/candidate/candidate-list'
add_candidate_url = hostURL + '/api/candidate/add-candidate'
update_candidate_url = hostURL + '/api/candidate/update-candidate'
update_details_candidate_page_url = hostURL + '/api/candidate/update-details-candidate-page'
department_url = hostURL + '/api/master/department-list'
rank_url = hostURL + '/api/master/rank-list'
get_qualification_url = hostURL + '/api/master/get-qualifications'


def candidateList(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        # candi_details_request = requests.get(candi_details_urls,headers=headers)
        # candi_details_response = candi_details_request.json()
        
        # return render(request,'org_html/candidate/candidate.html',{'get_details':candi_details_response['data']})
        return render(request,'org_html/candidate/candidate.html')
    else:
        return redirect('organisation:login')
    
    
def addCandidate(request):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        data={}
        qual_request = requests.get(get_qualification_url,headers=headers)
        qual_response = qual_request.json()
        return render(request,'org_html/candidate/add-candidate.html',{'og_token':og_token,'quallist':qual_response['data']})
    else:
        return redirect('organisation:login')
    
    

    
    
def updateCandidate(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        candi_details_request = requests.get(candi_details_urls,headers=headers,params={'id':id})       
        candi_details_response = candi_details_request.json()

        department_request = requests.get(department_url,headers=headers)
        department_response = department_request.json()
        
        rank_request = requests.get(rank_url,headers=headers)
        rank_response = rank_request.json()

        qual_request = requests.get(get_qualification_url,headers=headers)
        qual_response = qual_request.json()
        
        return render(request,'org_html/candidate/update-candidate.html',{'rank':rank_response['data'],'department':department_response['data'],'canddata':candi_details_response['data'],'quallist':qual_response['data']})
    else:
        return redirect('organisation:login')
 

def ViewCandidateProfile(request,id):
    og_token = request.session.get('og_token')
    if og_token:
        token = 'Bearer {}'.format(og_token)
        headers = {'Authorization':token}
        
        candi_details_request = requests.get(candi_details_urls,headers=headers,params={'id':id})       
        candi_details_response = candi_details_request.json()

        department_request = requests.get(department_url,headers=headers)
        department_response = department_request.json()
        
        rank_request = requests.get(rank_url,headers=headers)
        rank_response = rank_request.json()

        qual_request = requests.get(get_qualification_url,headers=headers)
        qual_response = qual_request.json()
        
        return render(request,'org_html/candidate/view-candidate-profile.html',{'rank':rank_response['data'],'department':department_response['data'],'canddata':candi_details_response['data'],'quallist':qual_response['data']})
    else:
        return redirect('organisation:login')
    
def CandidatesResults(request):



    
    return render(request,'org_html/reports/candidates-results.html',{})



