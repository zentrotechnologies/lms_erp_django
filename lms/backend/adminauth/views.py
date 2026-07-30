from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from .serializers import *
from lms.settings import *
from django.contrib.auth.hashers import make_password,check_password
from .jwt import *
from helpers.validations import *
from rest_framework import permissions
from urllib.parse import unquote
from master.models import *
from master.serializers import *
from django.core.files.storage import default_storage
from django.http import QueryDict
import re
from course.models import TrainingMode
from usermanagement.models import *
from usermanagement.serializers import *
from course.models import *
from django.db.models import Q

from course.serializers import *
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def save_file(folder_path,uploaded_file,request):              
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, uploaded_file.name)
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
    file_url=request.build_absolute_uri(settings.MEDIA_URL + relative_file_path.replace("\\", "/"))
    return file_url

#super admin

class AddAdmin(GenericAPIView):
    def post(self,request): 
        data = {}
        data['name'] = request.POST.get('name')
        data['mobilenumber'] = request.POST.get('mobilenumber')
        data['password'] = make_password(request.POST.get('password'))
        data['email'] = str(request.POST.get('email')).lower()
        data['status'] = True
        data['source'] = 'admin'
        data['user_type'] = 1
        data['og_code'] = 'SUPER'
        
        email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).first()
        number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
        if email_object is not None:
            response_={
                "n": 0,                    
                "msg": 'Email already exists',
                "data":[],                  
            }
            return Response(response_,status=200)
        
        if number_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Mobile number already exists',
                        "data":[],                  
                    }
            return Response(response_,status=200)
        
        serializer = UserAdminSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_={
                "n": 1,
                "msg": 'Admin registered successfully',
                "data":serializer.data                        
            }
            return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Admin not registered',
                        "data":[]                     
                    }
            return Response(response_,status=200)
            

class UserLogin(GenericAPIView):
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request_data.get('email')
        password = request_data.get('password')
        
        if email is None or email == "":
            response_={
                "n": 0,                    
                "msg": 'Email is required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        if password is None or password == "":
            response_={
                "n": 0,                    
                "msg": 'Password is required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

        user_object = UserAdmin.objects.filter(isActive=True,email=email).first()
        if user_object is None:

            response_={
                "n": 0,                    
                "msg": 'User not found',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:

            user_ser = UserAdminSerializer(user_object)
            check_user_password = check_password(password,user_object.password)
            if check_user_password == True:
                role = user_object.role
                deactive_user_token = UserAdminToken.objects.filter(user_id=user_object.id).update(isActive=False)           
                user_token= UserAdminToken.objects.create(user_id=user_object.id,authToken=user_object.token)
                # if user_object.user_type == 3:
                #     usertype_filter = 3
                menuobj = MenuDetails.objects.filter(isActive=True,user_type__icontains = str(user_object.user_type)).order_by('sort_order')
                menu_serializer = MenuDetailsSerializer(menuobj, many=True)
                
               
                response_={
                        "n": 1,                    
                        "msg": 'User logged in successfully',
                        "token":user_token.authToken,
                        'menuItems':menu_serializer.data,
                        "data":user_ser.data,   
                        
                                 
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:

                response_={
                        "n": 0,                    
                        "msg": 'Incorrect password',
                        "data":[],                  
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                 

class UserLogout(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        token = request_data.get('token')
        if token is not None and token !="":
            admintokenobj = UserAdminToken.objects.filter(authToken=token,isActive=True).first()
            if admintokenobj is not None:
                admintokenobj.isActive = False
                admintokenobj.save()
                response_={
                    "n": 1,
                    "msg": 'Logout Successful!',
                    "data":[]                      
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                response_={
                    "n": 0,                    
                    "msg": 'token not found',
                    "data":[],                  
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        else:
            response_={
                "n": 0,                    
                "msg": 'token required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

#Organisation

def OrganisationUniqueCode(ogname):
    og = [s[0].upper() for s in ogname.split()]
    ogJoin = "".join(og)
    firstog = ogJoin + "001"
    ogobject = UserAdmin.objects.filter(isActive=True,is_organisation=True).order_by('-createdAt').first()
    if ogobject is None:
        ogcode = firstog
        return ogcode
    else:
        stripog = ogobject.og_code
        increementog = int(stripog[3:]) + 1
        placeog = "%03d" % (increementog)
        newogcode = ogJoin + str(placeog)
        return newogcode

class AddOrganisation(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
        data['name'] = request_data.get('name')
        data['mobilenumber'] = request_data.get('mobilenumber')
        data['password'] = make_password(request_data.get('password'))
        data['email'] = str(request_data.get('email')).lower()
        data['status'] = True
        data['source'] = 'admin'
        data['user_type'] = 2
        data['og_code'] = OrganisationUniqueCode(data['name'])
        data['createdBy'] = str(request.user.id)

        
        email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).first()
        number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
        if email_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Email already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        if number_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Mobile number already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        serializer = UserAdminSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            role_obj=UsereRole.objects.create(name='Admin',member_type=2,og_code=data['og_code'],member_of=serializer.data['id'])
            data['role_id']=role_obj.id
            user_bj=UserAdmin.objects.filter(id=serializer.data['id']).update(role=role_obj.id)

            serobj = MenuDetails.objects.filter(isActive=True,user_type__icontains = [2]).order_by('sort_order')
            serializer2 = MenuDetailsSerializer(serobj,many=True)
            for i in serializer2.data:
                Permissions.objects.create(
                        role_id =  data['role_id'],
                        menu_id = i['id']
                    )






            response_={
                        "n": 1,
                        "msg": 'Organisation registered successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Organisation not registered',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class AddTrainingCenter(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}

        userid = request.user.id
        
        adminobj = UserAdmin.objects.filter(id=userid).first()
        if adminobj is not None:
            if adminobj.member_of is None :
                data['og_id'] = str(adminobj.id)
            else:
                data['og_id'] = str(adminobj.member_of)

        data['name'] = request_data.get('name')
        data['mobilenumber'] = request_data.get('mobilenumber')
        data['password'] = make_password(request_data.get('password'))
        data['email'] = str(request_data.get('email')).lower()
        data['source'] = request_data.get('source')
        data['user_type'] = 3
        data['accreditation_number'] = request_data.get('accreditation_number')
        data['is_parent_training_center']=True
        if request_data.get('no_of_classroom') is not None and request_data.get('no_of_classroom') !='':
            data['no_of_classroom'] = request_data.get('no_of_classroom')




        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None
        data['createdBy'] = str(request.user.id)

        
        # data['parent_training_center'] = ''
        data['og_code'] = str(request.user.og_code)

        
        
        email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).first()
        number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
        if email_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Email already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        if number_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Mobile number already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        serializer = UserAdminSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            courses=request_data.get('courses')
            if courses is not None and courses != '':
                for course in courses:
                    already_exist_obj=TrainingCenterCourses.objects.filter(course_id=course,training_center_id=serializer.data['id'],isActive=True).first()
                    if already_exist_obj is None:
                        TrainingCenterCourses.objects.create(course_id=course,training_center_id=serializer.data['id'],isActive=True)

            menu_user_type = "3"
            role_obj=UsereRole.objects.create(name='Admin',member_type=3,og_code=data['og_code'],member_of=serializer.data['id'])
            data['role_id']=role_obj.id
            user_bj=UserAdmin.objects.filter(id=serializer.data['id']).update(role=role_obj.id)
            serobj = MenuDetails.objects.filter(isActive=True,user_type__icontains = menu_user_type).order_by('sort_order')
            serializer2 = MenuDetailsSerializer(serobj,many=True)
            for i in serializer2.data:
                Permissions.objects.create(
                        role_id =  data['role_id'],
                        menu_id = i['id']
                    )
                


            authority_list = request_data.get('authority_list')
            if authority_list != []:
                for i in authority_list:
                    Authority.objects.create(
                        createdBy = str(request.user.id),
                        user_id =  serializer.data['id'],
                        authority_name = i['authority_name'],
                        authority_number = i['authority_number'],
                        authority_email = i['authority_email'],
                        authority_designation = i['authority_designation'],
                    )


            response_={
                        "n": 1,
                        "msg": 'Training center added successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Training center not registered',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class UpdateTrainingCenter(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        updated_of_user_id =request_data.get('id')
        if updated_of_user_id is None or updated_of_user_id == "":
            response_={
                        "n": 0,                    
                        "msg": 'User id is required',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        user_object = UserAdmin.objects.filter(id=updated_of_user_id).first()
        if user_object is None:
            response_={
                        "n": 0,                    
                        "msg": 'Training center not Found',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        data = {}

 
        data['name'] = request_data.get('name')
        data['mobilenumber'] = request_data.get('mobilenumber')   
        data['email'] = str(request_data.get('email')).lower()
        data['source'] = request_data.get('source')
        data['accreditation_number'] = request_data.get('accreditation_number')      
        if request_data.get('no_of_classroom') is not None and request_data.get('no_of_classroom') !='':
            data['no_of_classroom'] = request_data.get('no_of_classroom')


        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None
        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()
        
        authority_list = request_data.get('authority_list')
        email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).exclude(id=updated_of_user_id).first()
        number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).exclude(id=updated_of_user_id).first()
        if email_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Email already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        if number_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Mobile number already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        serializer = UserAdminSerializer(user_object,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            courses=request_data.get('courses')
            if courses is not None:
                TrainingCenterCourses.objects.filter(training_center_id=serializer.data['id'],).update(isActive=False)
                for course in courses:
                    already_exist_obj=TrainingCenterCourses.objects.filter(course_id=course,training_center_id=serializer.data['id'],).first()
                    if already_exist_obj is None:
                        TrainingCenterCourses.objects.create(course_id=course,training_center_id=serializer.data['id'],isActive=True)
                    else:
                        TrainingCenterCourses.objects.filter(course_id=course,training_center_id=serializer.data['id'],).update(isActive=True)




            if authority_list != [] and authority_list is not None:
                Authority.objects.filter(user_id=serializer.data['id']).update(isActive=False)
                for i in authority_list:
                    Authority.objects.create(
                        createdBy = str(request.user.id),
                        user_id =  serializer.data['id'],
                        authority_name = i['authority_name'],
                        authority_number = i['authority_number'],
                        authority_email = i['authority_email'],
                        authority_designation = i['authority_designation'],
                    )
            response_={
                        "n": 1,
                        "msg": 'Training center updated successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Training center not updated',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class DeleteTrainingCenter(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        updated_of_user_id =request_data.get('id')
        if updated_of_user_id is None or updated_of_user_id == "":
            response_={
                        "n": 0,                    
                        "msg": 'User id is required',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        user_object = UserAdmin.objects.filter(id=updated_of_user_id,isActive=True).first()
        if user_object is None:
            response_={
                        "n": 0,                    
                        "msg": 'Training center not Found',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        data = {}

 

        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()
        data['isActive'] = False
        
        
        serializer = UserAdminSerializer(user_object,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            response_={
                        "n": 1,
                        "msg": 'Training center deleted successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Training center not deleted',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
     

class DeleteDocument(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        updated_of_user_id =request_data.get('document_id')
        if updated_of_user_id is None or updated_of_user_id == "":
            response_={
                        "n": 0,                    
                        "msg": 'Document id is required',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        user_object = UserDocuments.objects.filter(id=updated_of_user_id,isActive=True).first()
        if user_object is None:
            response_={
                        "n": 0,                    
                        "msg": 'Document center not Found',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        data = {}

 

        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()
        data['isActive'] = False
        
        
        serializer = UserDocumentSerializer(user_object,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            response_={
                        "n": 1,
                        "msg": 'Document deleted successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Document center not deleted',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
     

class AddSubTrainingCenter(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}

        userid = request.user.id
        parent_training_center = request_data.get('parent_training_center')
        if parent_training_center is None or parent_training_center =='':
            adminobj = UserAdmin.objects.filter(id=userid).first()
            if adminobj is not None:
                if adminobj.member_of is not None and adminobj.member_of !='':
                    data['parent_training_center'] = str(adminobj.member_of)
                else:
                    data['parent_training_center'] = str(adminobj.id)
        else:
            data['parent_training_center'] = parent_training_center
            

        data['og_code'] = str(request.user.og_code)
        data['name'] = request_data.get('name')
        data['mobilenumber'] = request_data.get('mobilenumber')

        if request_data.get('password') is not None and request_data.get('password') != "":
            data['password'] = make_password(request_data.get('password'))
        else:
            data['password'] =  make_password('Default@123')



        data['email'] = str(request_data.get('email')).lower()

        data['source'] = request_data.get('source')
        data['user_type'] = 4
        
        data['accreditation_number'] = request_data.get('accreditation_number')
        data['no_of_classroom'] = request_data.get('no_of_classroom') or 0
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None
 
        data['og_code'] = str(request.user.og_code)

        data['createdBy'] = str(request.user.id)

        email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).first()
        number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
        if email_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Email already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        if number_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Mobile number already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        serializer = UserAdminSerializer(data=data)
        menu_user_type = "4"
        if serializer.is_valid():
            serializer.save()
            courses=request_data.get('courses')
            if courses is not None and courses != '':
                for course in courses:
                    already_exist_obj=TrainingCenterCourses.objects.filter(course_id=course,training_center_id=serializer.data['id'],isActive=True).first()
                    if already_exist_obj is None:
                        TrainingCenterCourses.objects.create(course_id=course,training_center_id=serializer.data['id'],isActive=True)

            role_obj=UsereRole.objects.create(name='Admin',member_type=4,og_code=data['og_code'],member_of=serializer.data['id'])
            data['role_id']=role_obj.id

            user_bj=UserAdmin.objects.filter(id=serializer.data['id']).update(role=role_obj.id)
            serobj = MenuDetails.objects.filter(isActive=True,user_type__icontains = menu_user_type).order_by('sort_order')
          
            serializer2 = MenuDetailsSerializer(serobj,many=True)
            for i in serializer2.data:
                Permissions.objects.create(
                        role_id =  data['role_id'],
                        menu_id = i['id']
                    )










            authority_list = request_data.get('authority_list')

            if authority_list != []:
                for i in authority_list:
                    Authority.objects.create(
                        createdBy = str(request.user.id),
                        user_id =  serializer.data['id'],
                        authority_name = i['authority_name'],
                        authority_number = i['authority_number'],
                        authority_email = i['authority_email'],
                        authority_designation = i['authority_designation'],
                    )
            response_={
                        "n": 1,
                        "msg": 'Sub Training center added successfully',
                        "data":serializer.data                        
                    }
           
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Sub Training center not registered',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class UpdateSubTrainingCenter(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        updated_of_user_id =request_data.get('id')
        if updated_of_user_id is None or updated_of_user_id == "":
            response_={
                        "n": 0,                    
                        "msg": 'User id is required',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        user_object = UserAdmin.objects.filter(id=updated_of_user_id).first()
        if user_object is None:
            response_={
                        "n": 0,                    
                        "msg": 'Training center not Found',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        data = {}
        parent_training_center=request_data.get('parent_training_center')
        if parent_training_center is not None and parent_training_center !='':
            data['parent_training_center'] = parent_training_center

        data['name'] = request_data.get('name')
        data['mobilenumber'] = request_data.get('mobilenumber')   
        data['email'] = str(request_data.get('email')).lower()
        data['source'] = request_data.get('source')
        data['accreditation_number'] = request_data.get('accreditation_number')      
        data['no_of_classroom'] = request_data.get('no_of_classroom')
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None
        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()
        
        authority_list = request_data.get('authority_list')
        email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).exclude(id=updated_of_user_id).first()
        number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).exclude(id=updated_of_user_id).first()
        if email_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Email already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        if number_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Mobile number already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        serializer = UserAdminSerializer(user_object,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            courses=request_data.get('courses')
            TrainingCenterCourses.objects.filter(training_center_id=serializer.data['id'],).update(isActive=False)
            if courses is not None and courses !='':
                for course in courses:
                    already_exist_obj=TrainingCenterCourses.objects.filter(course_id=course,training_center_id=serializer.data['id'],isActive=True).first()
                    if already_exist_obj is None:
                        TrainingCenterCourses.objects.create(course_id=course,training_center_id=serializer.data['id'],isActive=True)
                    else:
                        TrainingCenterCourses.objects.filter(course_id=course,training_center_id=serializer.data['id'],).update(isActive=True)






            if authority_list != []:
                Authority.objects.filter(user_id=serializer.data['id']).update(isActive=False)
                for i in authority_list:
                    Authority.objects.create(
                        createdBy = str(request.user.id),
                        user_id =  serializer.data['id'],
                        authority_name = i['authority_name'],
                        authority_number = i['authority_number'],
                        authority_email = i['authority_email'],
                        authority_designation = i['authority_designation'],
                    )
            response_={
                        "n": 1,
                        "msg": 'Sub Training center added successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Sub Training center not registered',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
class SubTrainingCenterList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

            
        useradminobject = UserAdmin.objects.filter(isActive=True,user_type=4,is_member=False).order_by('-createdAt')
        if request.user.user_type==3:
            if request.user.member_of is not None and request.user.member_of !='':
                useradminobject=useradminobject.filter(parent_training_center=str(request.user.member_of),is_member=False)

            else:
                useradminobject=useradminobject.filter(parent_training_center=str(request.user.id),is_member=False)

        user_admin_ser = UserAdminSerializer(useradminobject,many=True)
        for i in user_admin_ser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""

            ptc_obj=UserAdmin.objects.filter(id=i['parent_training_center']).first()
            if ptc_obj is not None:
                i['parent_training_center_name']=ptc_obj.name
            else:
                i['parent_training_center_name']=''
        
        response_={
                    "n": 1,
                    "msg": 'Sub Training center fetched successfully',
                    "data":user_admin_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)



class TrainingCenterList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        og_code=str(request.user.og_code)    
        useradminobject = UserAdmin.objects.filter(isActive=True,user_type=3,og_code=og_code,is_member=False).order_by('-createdAt')
        user_admin_ser = UserAdminSerializer(useradminobject,many=True)
        for i in user_admin_ser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
        
        response_={
                    "n": 1,
                    "msg": 'Training center fetched successfully',
                    "data":user_admin_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)


class AllTrainingCenterList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        og_code = str(request.user.og_code)
            
        useradminobject = UserAdmin.objects.filter(isActive=True,user_type__in=[3,4],og_code=og_code).order_by('-createdAt')
        user_admin_ser = UserAdminSerializer(useradminobject,many=True)
        for i in user_admin_ser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
        
        response_={
                    "n": 1,
                    "msg": 'Training center fetched successfully',
                    "data":user_admin_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class OrgAllTrainingCenterList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        og_code = str(request.user.og_code)
            
        training_center_objs=UserAdmin.objects.filter(isActive=True,og_code=og_code,)
        training_center_objs=training_center_objs.filter(Q(user_type=3,is_parent_training_center=True,is_member=False,)|Q(user_type=4,is_member=False,))
        
        user_admin_ser = UserAdminSerializer(training_center_objs,many=True)
        for i in user_admin_ser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
        
        response_={
                    "n": 1,
                    "msg": 'Training center fetched successfully',
                    "data":user_admin_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)


class ParentAndSubTrainingCenterList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        og_code = str(request.user.og_code)
        parent_training_center_id=request_data.get('parent_training_center_id')

        useradminobject = UserAdmin.objects.filter(Q(id=parent_training_center_id,isActive=True,user_type__in=[3],is_parent_training_center=True,og_code=og_code)|Q(parent_training_center=parent_training_center_id,isActive=True,user_type__in=[4],is_parent_training_center=False,og_code=og_code,is_member=False)).order_by('-createdAt')


        course_ids=request_data.get('course_ids')
        if course_ids is not None and course_ids !='':
            traning_center_ids=list(TrainingCenterCourses.objects.filter(course_id__in=course_ids,isActive=True).values_list('training_center_id',flat=True))
            useradminobject=useradminobject.filter(id__in=traning_center_ids)
        useradminobject=useradminobject.order_by('id').distinct('id')

        user_admin_ser = UserAdminSerializer(useradminobject,many=True)
        for i in user_admin_ser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
        
        response_={
                    "n": 1,
                    "msg": 'Training center fetched successfully',
                    "data":user_admin_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)




class UserDetails(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        user_id = request_data.get('id')
        if user_id is None or user_id == "":
            response_={
                    "n": 0,
                    "msg": 'User not found',
                    "data":[]                        
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        user_object = UserAdmin.objects.filter(id=user_id).first()
        if user_object is None:
            response_={
                    "n": 0,
                    "msg": 'User not found',
                    "data":[]                        
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        serializer = UserAdminSerializer(user_object)
        serializer_data = serializer.data
        user_doc_object = UserDocuments.objects.filter(isActive=True,user_id=user_id)
   
        user_doc_ser = UserDocumentSerializer(user_doc_object,many=True)
        authority_object = Authority.objects.filter(isActive=True,user_id=user_id)
        authority_ser = AuthoritySerializer(authority_object,many=True)
       
        documents_required_object = Documents.objects.filter(isActive=True,role=serializer.data['user_type'])
        documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
        
        for d in documents_required_ser.data:
            doc_object = UserDocuments.objects.filter(isActive=True,user_id=user_id,document_id=d['id']).first()
            if doc_object is not None:
                d['uploaded_proof'] = doc_object.document_url
            else:
                d['uploaded_proof'] = ""
            
        country_name = ""
        state_name = ""
        if serializer.data['country'] is not None and serializer.data['country'] != "":
            country_object = Country.objects.filter(id=serializer.data['country']).first()
            if country_object is not None:
                country_name = country_object.name
            else:
                country_name = ""
        else:
            country_name = ""
        if serializer.data['state'] is not None and serializer.data['state'] != "":
            state_object = State.objects.filter(id=serializer.data['state']).first()
            if state_object is not None:
                state_name = state_object.name
            else:
                state_name = ""
        else:
            state_name = ""

        course_ids = list(TrainingCenterCourses.objects.filter(isActive=True,training_center_id=user_id).values_list('course_id',flat=True))

        
        serializer_data.update({
            "document_data":user_doc_ser.data,
            "authority_data":authority_ser.data,
            "proof_data":documents_required_ser.data,
            "state_name":state_name,
            "country_name":country_name,
            "course_ids":course_ids,
        })
        response_={
                    "n": 1,
                    "msg": 'User data fetched successfully',
                    "data":serializer_data                       
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class TrainingCenterDetails(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        user_id = request_data.get('id')
        if user_id is None or user_id == "":
            response_={
                    "n": 0,
                    "msg": 'User id not found',
                    "data":[]                        
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        user_object = UserAdmin.objects.filter(id=user_id).first()
        if user_object is None:
            response_={
                    "n": 0,
                    "msg": 'User not found',
                    "data":[]                        
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        serializer = UserAdminSerializer(user_object)
        serializer_data = serializer.data

        user_doc_object = UserDocuments.objects.filter(isActive=True,user_id=user_id)
        user_doc_ser = UserDocumentSerializer(user_doc_object,many=True)
        
        authority_object = Authority.objects.filter(isActive=True,user_id=user_id)
        authority_ser = AuthoritySerializer(authority_object,many=True)

        documents_required_object = Documents.objects.filter(isActive=True,role=serializer.data['user_type'])
        documents_required_ser = DocumentsSerializer(documents_required_object,many=True)

        branch_required_object = Branch.objects.filter(isActive=True,training_center=serializer.data['id'])
        branch_required_ser = CustomBranchSerializer(branch_required_object,many=True)


        for d in documents_required_ser.data:
            doc_object = UserDocuments.objects.filter(isActive=True,user_id=user_id,document_id=d['id']).first()
            if doc_object is not None:
                d['uploaded_proof'] = doc_object.document_url
            else:
                d['uploaded_proof'] = ""
            
        country_name = ""
        state_name = ""
        if serializer.data['country'] is not None and serializer.data['country'] != "":
            country_object = Country.objects.filter(id=serializer.data['country']).first()
            if country_object is not None:
                country_name = country_object.name
            else:
                country_name = ""
        else:
            country_name = ""
        if serializer.data['state'] is not None and serializer.data['state'] != "":
            state_object = State.objects.filter(id=serializer.data['state']).first()
            if state_object is not None:
                state_name = state_object.name
            else:
                state_name = ""
        else:
            state_name = ""

        course_ids = list(TrainingCenterCourses.objects.filter(isActive=True,training_center_id=user_id).values_list('course_id',flat=True))
        
        
        serializer_data.update({
            "document_data":user_doc_ser.data,
            "authority_data":authority_ser.data,
            "proof_data":documents_required_ser.data,
            "state_name":state_name,
            "country_name":country_name,
            "course_ids":course_ids,
            "branches":branch_required_ser.data
        })
        response_={
                    "n": 1,
                    "msg": 'User data fetched successfully',
                    "data":serializer_data                       
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)


class UploadUserDocument(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        combined_array = []
        user_id = request_data.get('user_id')
        doc_ids = request_data.getlist('doc_id')
        doc_names = request_data.getlist('doc_name')
        
        docsUpload = request.FILES.getlist('docsUpload')
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Documents','SubTrainingCenter')

        file_url_list = []
        if docsUpload != []:
            for i in docsUpload:
                file_url=save_file(folder_path,i,request)
                file_url_list.append(file_url)
                
            for i in range(len(doc_ids)):
                file_url = file_url_list[i] if i < len(file_url_list) else None
                combined_array.append({
                    'document_id': doc_ids[i],
                    'document_name': doc_names[i],
                    'user_id': user_id,
                    'uploaded_file': file_url
                })
                data = {}
                user_doc = UserDocuments.objects.filter(isActive=True,user_id = user_id,document_url =file_url).update(isActive=True)
                
                # if user_doc is None:
                UserDocuments.objects.create(
                    document_id = doc_ids[i],
                    document_name = doc_names[i],
                    user_id = user_id,
                    document_url =file_url
                )
       
        
        response_={
                    "n": 1,
                    "msg": 'Files uploaded successfully',
                    "data":[]               
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
class UploadUserDocumentFormData(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        user_ids = request.data.getlist('user_id')
        doc_ids = request.data.getlist('doc_id')
        doc_names = request.data.getlist('doc_name')
        file_uploads = request.FILES.getlist('document_file_upload')

        # Creating the list of dictionaries
        result = [
            {
                'user_id': user_id,
                'doc_id': doc_id,
                'doc_name': doc_name,
                'document_file_upload': file_upload,
            }
            for user_id, doc_id, doc_name, file_upload in zip(user_ids, doc_ids, doc_names, file_uploads)
        ]
            
    
        docsUpload = request.FILES.getlist('document_file_upload')
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Documents','Faculty')

        file_url_list = []
        for i in result:
     
            file_url=save_file(folder_path,i['document_file_upload'],request)
            user_doc = UserDocuments.objects.filter(isActive=True,user_id = i['user_id'],document_url =file_url).update(isActive=True)
            
            # if user_doc is None:
            UserDocuments.objects.create(
                document_id = i['doc_id'],
                document_name = i['doc_name'],
                user_id = i['user_id'],
                document_url =file_url
            )

        
        
        response_={
                    "n": 1,
                    "msg": 'Files uploaded successfully',
                    "data":[]               
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class SearchCities(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        cityname = request_data.get("city")
        if cityname != "":
            cityobj = Cities.objects.filter(name__icontains=cityname)[:10]
            cityser = CitiesSerializer(cityobj,many=True)   

        else:
            cityobj = Cities.objects.filter(country=101)
            cityser = CitiesSerializer(cityobj,many=True) 


        for i in cityser.data:
            statename_obj=State.objects.filter(id=i['state']).first()
            countryname_obj=Country.objects.filter(id=i['country']).first()
            if statename_obj is not None:
                i['statename']=statename_obj.name
            else:
                i['statename']=''

            if countryname_obj is not None:
                i['countryname']=countryname_obj.name
            else:
                i['countryname']=''

        response_={
                    "n": 1,
                    "msg": 'Data fetched successfully',
                    "data":cityser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
            
class AddCountryEligibility(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        countryname_obj=Country.objects.filter(id=request_data['country']).first()

        if countryname_obj is not None:
            data={}
            data['is_eligibile']=True
            serializer=CountrySerializer(countryname_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
            
                response_={
                            "n": 1,
                            "msg": 'Country marked as eligibile',
                            "data": serializer.data                        
                        }
            else:
                response_={
                            "n":0,
                            "msg": 'Country not marked as eligibile',
                            "data": serializer.errors                        
                        }
        else:
            response_={
                            "n":0,
                            "msg": 'Country not found',
                            "data": {}                        
                        }
            

        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
            



class AddFaculty(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data={}
        data['first_name'] = request_data.get("first_name")
        data['middle_name'] = request_data.get("middle_name")
        data['last_name'] = request_data.get("last_name")
        data['dob'] = request_data.get("dob")
        data['gender'] = request_data.get("gender")
        data['years_of_experience'] = request_data.get("years_of_experience")
        data['previous_institute'] = request_data.get("previous_institute")
        data['teaching_experience'] = request_data.get("teaching_experience")
        data['preferred_teaching_mode'] = request_data.get("preferred_teaching_mode")
        data['specialization'] = request_data.get("specialization") #json.loads
        data['languages'] = request_data.get("languages")
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None 
        data['email'] = request_data.get('email')    
        data['mobilenumber'] = request_data.get('mobilenumber')    
        data['user_type'] = 5
        data['og_code'] = str(request.user.og_code)
        data['createdBy'] = str(request.user.id)
        data['password'] =make_password('Default@123')
        userid = request.user.id
        
        adminobj = UserAdmin.objects.filter(id=userid).first()
        if adminobj is not None:
            if adminobj.member_of is None :
                data['parent_training_center'] = str(adminobj.id)
            else:
                data['parent_training_center'] = str(adminobj.member_of)
                


        serializer = UserAdminSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # role_obj=UsereRole.objects.create(name='Faculty',member_type=5,og_code=data['og_code'],member_of=serializer.data['id'])
            # data['role_id']=role_obj.id
            # user_bj=UserAdmin.objects.filter(id=serializer.data['id']).update(role=role_obj.id)
            # serobj = MenuDetails.objects.filter(isActive=True,user_type__icontains = [4]).order_by('sort_order')
            # serializer2 = MenuDetailsSerializer(serobj,many=True)
            # for i in serializer2.data:
            #     Permissions.objects.create(
            #             role_id =  data['role_id'],
            #             menu_id = i['id']
            #         )













            response_={
                        "n": 1,
                        "msg": 'Faculty added successfully',
                        "data":serializer.data                        
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            print("error",serializer.errors)
            response_={
                        "n": 0,
                        "msg": 'Faculty not registered',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class FacultyList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        og_code = str(request.user.og_code)

        if request.user.member_of is not None and request.user.member_of !='':
            facultyobj = UserAdmin.objects.filter(isActive=True,og_code=og_code,user_type=5,parent_training_center=str(request.user.member_of)).order_by('-id')
        else:
            facultyobj = UserAdmin.objects.filter(isActive=True,og_code=og_code,user_type=5,parent_training_center=str(request.user.id)).order_by('-id')
        

        
        facultyser = UserAdminSerializer(facultyobj,many=True)
        for i in facultyser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
                
                
            if i['specialization'] != "" and i['specialization'] is not None:
                i['specialization'] = json.loads(i['specialization'])
                # for k in topics_cov:
                #     topic_list.append(k['value'])
            
            trmode = i['preferred_teaching_mode']
            if trmode is not None and trmode != '':
                trobj = TrainingMode.objects.filter(id=i['preferred_teaching_mode']).first()
                i['preferred_teaching_mode'] = trobj.training_mode
            else:
                i['preferred_teaching_mode'] = ''

            if i['name'] == '' or i['name'] is None:
                i['name']=i['first_name']+' '+i['last_name']
        response_={
                    "n": 1,
                    "msg": 'Faculty list found successfully',
                    "data":facultyser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        facultyid = request_data.get('facultyid')
        if facultyid is not None and facultyid != "":
            facultyobj = UserAdmin.objects.filter(isActive=True,id=facultyid).first()
            if facultyobj is not None: 
                serializer = UserAdminSerializer(facultyobj)
                response_={
                    "n": 1,
                    'msg':'Faculty Details Found.',
                    'data':serializer.data
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                response_={
                    "n": 0,
                    'msg':'Faculty not FOund.',
                    'data':{}
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        else:
            response_={
                "n": 0,
                'msg':'Faculty id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class userList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        og_code = str(request.user.og_code)
        userobj = UserAdmin.objects.filter(isActive=True,og_code=og_code,).order_by('-id')
        userser = UserAdminSerializer(userobj,many=True)
        for i in userser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
            
        response_={
                    "n": 1,
                    "msg": 'user list found successfully',
                    "data":userser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        


class UpdateFaculty(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data={}
        og_code = str(request.user.og_code)
        facultyid =  request_data.get("facultyid")
        
        if facultyid is not None and facultyid !="":
            data['first_name'] = request_data.get("first_name")
            data['middle_name'] = request_data.get("middle_name")
            data['last_name'] = request_data.get("last_name")
            data['dob'] = request_data.get("dob")
            data['gender'] = request_data.get("gender")
            data['years_of_experience'] = request_data.get("years_of_experience")
            data['previous_institute'] = request_data.get("previous_institute")
            data['teaching_experience'] = request_data.get("teaching_experience")
            data['preferred_teaching_mode'] = request_data.get("preferred_teaching_mode")
            data['specialization'] = request_data.get("specialization") #json.loads
            data['languages'] = request_data.get("languages")
            data['address_line_one'] = request_data.get('address_line_one')
            data['address_line_two'] = request_data.get('address_line_two')
            data['country'] = request_data.get('country')
            data['state'] = request_data.get('state')
            data['city'] = request_data.get('city')
            data['pincode'] = request_data.get('pincode')
            data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None 
            data['email'] = request_data.get('email')    
            data['mobilenumber'] = request_data.get('mobilenumber')
   
            data['updatedBy'] = str(request.user.id)
            data['updatedAt'] = timezone.now()

            
            email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).exclude(id=facultyid).first()
            number_object = UserAdmin.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).exclude(id=facultyid).first()
            if email_object is not None:
                response_={
                            "n": 0,                    
                            "msg": 'Email already exists',
                            "data":[],                  
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            if number_object is not None:
                response_={
                            "n": 0,                    
                            "msg": 'Mobile number already exists',
                            "data":[],                  
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)

            facultyobj = UserAdmin.objects.filter(isActive=True,og_code=og_code,user_type=5,id=facultyid).first()
            if facultyobj is not None: 
                serializer = UserAdminSerializer(facultyobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                                "n": 1,
                                "msg": 'Faculty updated successfully',
                                "data":serializer.data                        
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    print("error",serializer.errors)
                    response_={
                                "n": 0,
                                "msg": 'Faculty not updated',
                                "data":[]                     
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                response_={
                                "n": 0,
                                "msg": 'Faculty not found',
                                "data":[]                     
                            }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        else:
            response_={
                            "n": 0,
                            "msg": 'Faculty id required',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class DeleteFaculty(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        facultyid =  request_data.get("facultyid")
        if facultyid is not None and facultyid !="":
            facultyobj = UserAdmin.objects.filter(isActive=True,id=facultyid).first()
            if facultyobj is not None:
                facultyobj.isActive = False
                facultyobj.save()
                response_={
                    "n": 1,
                    'msg':'Faculty Deteled Successfully.',
                    'data':{}
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                response_={
                    "n": 0,
                    'msg':'Faculty not found.',
                    'data':{}
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        else:
            response_={
                "n": 0,
                'msg':'Faculty id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        




        
        
class CheckAndDecyptData(GenericAPIView):

    def post(self,request):

        data = request.data.get('data')
        
        if data is not None and data != "":
            decrypt_to_data = json.loads(decrypt_data(data))
            return Response(decrypt_to_data,status=200)
        else:
            response_={
                    'status':'failed',
                    'msg':'Please provid data to decrypt',
                    'data':[]
                                
                }
            return Response(response_,status=200)
        
class GetPublicKey(GenericAPIView):
    
    def get(self,request):
        with open('public_key.pem', 'rb') as pub_file:
            public_key = pub_file.read().decode()
        response_={
                'n':1,
                'msg':'Public key fetched',
                'data':public_key                            
            }
        return Response(response_,status=200)
    
class MainRoleList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        main_role_object = MainRoles.objects.all()
        ser = MainRolesSerializer(main_role_object,many=True) 


        response_={
                    "n": 1,
                    "msg": 'Data fetched successfully',
                    "data":ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        

class MainRoleDocumentList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        main_role_object = MainRoles.objects.filter(documents_required=True)
        ser = MainRolesSerializer(main_role_object,many=True) 

        response_={
                    "n": 1,
                    "msg": 'Data fetched successfully',
                    "data":ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
        
            
class MenuDetailList(GenericAPIView):
    def get(self,request):
        user_type = request.GET.get('user_type')
        serobj = MenuDetails.objects.filter(isActive=True,user_type__icontains = str(user_type)).order_by('sort_order')
        serializer = MenuDetailsSerializer(serobj,many=True)
        response_={
            "n": 1,
            'msg':'Menu data found successfully',
            'data':serializer.data
        }
        return Response(response_,status=200)

# 

class AddPermission(GenericAPIView):
    def post(self,request):
        data={}
        data['role_id'] = request.data.get('Role_id')
        data['menu_id'] = list(map(int, request.data.getlist('menu_id')))
        if data['role_id'] is not None and data['role_id'] != '':
            roleobj = Permissions.objects.filter(role_id= data['role_id'],isActive=True).first()
            if roleobj is None:
                for i in data['menu_id']:
                    Permissions.objects.create(
                        role_id =  data['role_id'],
                        menu_id = i
                    )
                response_={
                    "n": 1,
                    'msg':'Permissions Added Successfully.',
                    'data':{}
                }
                return Response(response_,status=200)
            else:
                Permissions.objects.filter(role_id= data['role_id']).delete()
                for i in data['menu_id']:
                    Permissions.objects.create(
                        role_id =  data['role_id'],
                        menu_id = i
                    )
                response_={
                    "n": 1,
                    'msg':'Permissions Added Successfully.',
                    'data':{}
                }
                return Response(response_,status=200)
        else:
            response_={
                "n": 0,
                'msg':'Please select role.',
                'data':{}
            }
            return Response(response_,status=200)
                
            
class GetPermission(GenericAPIView):
    def post(self,request):
        data = {}
        data['role_id'] = request.data.get('roleid')
        roleobj = Permissions.objects.filter(role_id=data['role_id'], isActive=True).order_by('menu_id')
        if roleobj is not None:
            serializer = PermissionsSerializer(roleobj,many=True)
            for i in serializer.data:
                menuobj=MenuDetails.objects.filter(id=int(i['menu_id'])).first()
                i['menu_path'] = menuobj.menu_path
                i['menu_name'] = menuobj.menu_name
                i['parent_id'] = menuobj.parent_id
                i['menu_icon'] = menuobj.menu_icon
            response_= {
                    "n": 1,
                    'msg':'Permission found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                "n": 0,
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)
        
class GetUserTypePermission(GenericAPIView):
    def post(self,request):
        data = {}
        data['user_type'] = request.data.get('user_type')
        menuobj=MenuDetails.objects.filter(user_type__icontains=str(data['user_type'])).order_by('id')
        if menuobj.exists():
            serializer=MenuDetailsSerializer(menuobj,many=True)
            for i in serializer.data:
                i['menu_id']=i['id']
            response_= {
                    "n": 1,
                    'msg':'Permission found Successfully.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                "n": 0,
                'msg':'Data not found.',
                'data':{}
            }
            return Response(response_,status=200)
        

class DeleteUserDocuments(GenericAPIView):
    
    def post(self,request):
        
        user_doc_id = request.data.get('user_doc_id')
        if user_doc_id is not None and user_doc_id != "":
            user_doc_object = UserDocuments.objects.filter(id=user_doc_id).first()
            if user_doc_object is not None:
                user_doc_object.isActive = False
                user_doc_object.updatedAt = timezone.now()
                user_doc_object.save()
                response_={
                    "n": 1,
                    'msg':'Document Deleted Successfully.',
                    'data':[]
                }
                return Response(response_,status=200)
            else:
                response_={
                    "n": 0,
                    'msg':'Document not Deleted.',
                    'data':{}
                }
                return Response(response_,status=200)
        else:
            response_={
                    "n": 0,
                    'msg':'Document id not provided.',
                    'data':{}
                }
            return Response(response_,status=200)
                

class GetTrainingCenterCourses(GenericAPIView):
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        training_center_id = request_data.get('training_center_id')
        if training_center_id is None or training_center_id == "" or training_center_id == "None":
            training_center_id = str(request.user.id)

        if training_center_id is not None and training_center_id != "" and training_center_id != "None":


            course_ids = list(TrainingCenterCourses.objects.filter(training_center_id=training_center_id,isActive=True).values_list('course_id',flat=True))
            course_objs=Course.objects.filter(id__in=course_ids,isActive=True,course_status='Approved')
            if course_objs.exists():
                serializer=CourseSerializer(course_objs,many=True)
                response_={
                    "n": 1,
                    'msg':'Courses found Successfully.',
                    'data':serializer.data
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                response_={
                    "n": 0,
                    'msg':'coueses  not found.',
                    'data':{}
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        else:
            response_={
                    "n": 0,
                    'msg':'Training center id not provided.',
                    'data':{}
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
                

