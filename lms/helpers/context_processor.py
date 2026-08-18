from django.shortcuts import redirect, render
import requests
from helpers.validations import *


def getMenu(request):
    menuItems = None
    name = None
    
    og_token = request.session.get('og_token')
    if og_token is not None:  
        is_parent_college = request.session.get('is_parent_college')
        user_type = request.session.get('user_type')
        parent_college = request.session.get('parent_college')
        user_id = request.session.get('user_id')
        menuItems=request.session.get('menuItems')
        name = request.session.get('name')
        email = request.session.get('email')
        role = request.session.get('role')
      
        return {
            'og_token':og_token,
            'base_encryption_key':base_encryption_key,
            'backendurl':hostURL,
            'frontendurl':frontURL,
            'is_parent_college':is_parent_college,
            'user_type':user_type,      
            'parent_college':parent_college,
            'user_id':user_id,
            'menuItems':menuItems,
            'name':name,
            'email':email,
            'role':role,
        }
    return {'og_token':og_token,'base_encryption_key':base_encryption_key,'backendurl':hostURL,'frontendurl':frontURL,'menuItems':menuItems,'name':name}



