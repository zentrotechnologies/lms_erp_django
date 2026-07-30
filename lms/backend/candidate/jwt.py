from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)

import jwt
from .models import *
from rest_framework.serializers import ValidationError
from rest_framework import status


class CustomAPIException(ValidationError):
    """
    raises API exceptions with custom messages and custom status codes
    """    
    status_code = 401
    default_code = 'error'    
    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class CandidateJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth_header = get_authorization_header(request)

        auth_data = auth_header.decode('utf-8')
        auth_token = auth_data.split(" ")

        if len(auth_token) != 2:
            error_msg = {
                "response": {
                    "n": 0,
                    "data":[],
                    "msg": 'Token not valid',
                }
            }
            raise CustomAPIException(error_msg)        
        token = auth_token[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
       
            user_id = payload['id']
            useradmin = Candidate.objects.get(id=user_id)
            # if source == "web":
            #     useradminTok = UserAdminToken.objects.filter(
            #         authToken=token, user_id=useradmin.id, isActive=True).first()
            # else:
            useradminTok = CandidateToken.objects.filter(
                authToken=token, user_id=useradmin.id, isActive=True).first()
            if useradminTok is None:
                error_msg = {
                   
                        "n": 0,
                        "data":[],
                        "msg": 'Token is expired, login again',
                   
                }
                raise CustomAPIException(error_msg)              
            return (useradmin, token)

        except jwt.ExpiredSignatureError as ex:
            error_msg = {
               
                    "n": 0,
                    "data":[],
                    "msg": 'Token is expired, login again',
              
            }
            raise CustomAPIException(error_msg)        

        except jwt.DecodeError as ex:
            error_msg = {
                "response": {
                    "n": 0,
                    "data":[],
                    "msg": "Token is invalid",
                }
            }
            raise CustomAPIException(error_msg)        

        except ObjectDoesNotExist as no_user:
            return None

        return super().authenticate(request)
