from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import *
from usermanagement.serializers import *
from adminauth.serializers import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.jwt import UserAdminJWTAuthentication
from django.contrib.auth.hashers import make_password,check_password
from adminauth.models import *
from adminauth.serializers import *

# Create your views here.

class AddRole(GenericAPIView):
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
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
        
            data['member_type'] = adminobj.user_type
            if adminobj.member_of is None :
                data['member_of'] = str(adminobj.id)
            else:
                data['member_of'] = str(adminobj.member_of)
            data['og_code'] = adminobj.og_code
            
            data['name'] = request_data.get('name')
            data['remark'] = request_data.get('remark')
            data['createdBy'] = str(request.user.id)
           
            if data['name'] is not None and data['name'] !="":
                obj = UsereRole.objects.filter(isActive=True)
                ser = UsereRoleSerializer(obj,many=True)
                for c in ser.data:
                    existingname = c['name'].lower()
                    newname = data['name'].lower()

                    existingmembertype = c['member_type']
                    newmembertype =  data['member_type']

                    existingmemberof = c['member_of']
                    newmemberof = data['member_of']

                    if existingname == newname and existingmembertype == newmembertype and existingmemberof == newmemberof:
                        response_={
                            "n": 0,
                            'msg':"Role already exits",
                            'data':{}
                        }    
                        if encryped_header == "1" :
                            data_to_serialize = convert_decimals_to_float(response_)
                            encdata = encrypt_data(json.dumps(data_to_serialize))
                            return Response(encdata,status=200)
                        else:
                            return Response(response_,status=200)
                  
                cser = UsereRoleSerializer(data=data)
                if cser.is_valid():
                    cser.save()
                    response_={
                        "n": 1,
                        'msg':'Role added successfully.',
                        'data':cser.data
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    print("error",cser.errors)
                    response_={
                        "n": 0,
                        'msg':'Role not added.',
                        'data':cser.errors
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
                    'msg':'Please Provide role name.',
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
                    "msg": 'loggedin user not found',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    

    
class RoleList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
            member_type = adminobj.user_type
            if adminobj.member_of is None :
                member_of = str(adminobj.id)
            else:
                member_of = str(adminobj.member_of)
            og_code = adminobj.og_code

            obj = UsereRole.objects.filter(isActive=True,member_type=member_type,member_of = member_of,og_code=og_code).order_by('id')
            ser = UsereRoleSerializer(obj,many=True)
            for i in ser.data:
                usedobj = UserAdmin.objects.filter(role=i['id'],isActive=True).first()
                if usedobj is not None:
                    i['isused'] = True
                else:
                    i['isused'] = False

            response_={
                "n": 1,
                'msg':'Role list found successfully.',
                'data': ser.data
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
                'msg':'Role list not found.',
                'data': {}
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
        
        id = request_data.get('id')
        if id is not None and id != "":
            catobj=UsereRole.objects.filter(id=id,isActive=True).last()
            if catobj is not None:
                serializer = UsereRoleSerializer(catobj)
                response_={
                    "n": 1,
                    'msg':'Role Details Found.',
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
                    'msg':'No Data FOund.',
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
                'msg':'id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class UpdateRole(GenericAPIView):
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
        data['id'] = request_data.get('id')
        if data['id'] is not None:
            data['name'] = request_data.get('name')
            data['remark'] = request_data.get('remark')
        
            obj = UsereRole.objects.filter(isActive=True).exclude(id=data['id'])
            ser = UsereRoleSerializer(obj,many=True)
            for p in ser.data:
                if str(p['name']).lower() == str(data['name']).lower():
                    response_={
                        "n": 0,
                        'msg':'name already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            peobj=UsereRole.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = UsereRoleSerializer(peobj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Role Updated Successfully.',
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
                        "n": 1,
                        'msg':'Role Not Updated.',
                        'data':serializer.errors
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                response_={
                    "n": 1,
                    'msg':'id not found.',
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
                "n": 1,
                'msg':'id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        


class DeleteRole(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        id = request_data.get('id')
        if id is not None and id !="":
            cat_obj=UsereRole.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                check_mapping=UserAdmin.objects.filter(role=id,isActive=True).first()
                if check_mapping is not None:
                    response_={
                        "n": 0,
                        'msg':'This role is mapped to user.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)



                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Role Deleted Successfully.',
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
                    'msg':'Role id not found.',
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
                'msg':'id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
            

class AddMember(GenericAPIView):
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
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
            data['member_type'] = adminobj.user_type
            if adminobj.member_of is None :
                data['member_of'] = str(adminobj.id)
            else:
                data['member_of'] = str(adminobj.member_of)
            data['og_code'] = adminobj.og_code
        
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['designation'] = request_data.get('designation')
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['email'] = str(request_data.get('email')).lower()
            data['password'] = make_password(request_data.get('password'))
            data['role'] = request_data.get('role')
            data['reporting_to'] = request_data.get('reporting_to')
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['city'] = request_data.get('city')
            data['country'] = request_data.get('country')
            data['state'] = request_data.get('state')
            data['pincode'] = request_data.get('pincode')
            data['joining_date'] = request_data.get('joining_date')
            data['is_member'] = True
            data['user_type'] =  data['member_type']
            # data['parent_training_center'] =  ''

            
            # data['member_type'] = 3
            # data['member_of'] = str(request.user.id)
            # data['og_code'] = str(request.user.og_code)
            data['deactivate'] = True
            
            email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).last()
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
            
            serializer = UserAdminSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                response_={
                    "n": 1,
                    "msg": 'Member added successfully',
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
                    "msg": 'Member not added',
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
                    "msg": 'logged in user not found',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

                


class MemberList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
            member_type = adminobj.user_type
            if adminobj.member_of is None :
                member_of = str(adminobj.id)
            else:
                member_of = str(adminobj.member_of)
            og_code = adminobj.og_code

            obj = UserAdmin.objects.filter(member_type = member_type,member_of=member_of,og_code=og_code,is_member=True,isActive=True)
            member_ser = UserAdminSerializer(obj,many=True)
          
            newadminobj = UserAdmin.objects.filter(id=member_of,isActive=True).first()
            userser =  UserAdminSerializer(newadminobj)


            combined_data = member_ser.data + [userser.data]
            for i in combined_data:
                if i['name'] is not None and i['name'] != '':
                    i['username'] = i['name']
                else:
                    i['username'] = i['first_name'] +" "+i['last_name']

                i['createdAt'] = i['createdAt'].split('T')[0].split('-')[2]+"-"+i['createdAt'].split('T')[0].split('-')[1]+"-"+i['createdAt'].split('T')[0].split('-')[0]
                
                obj = UsereRole.objects.filter(id=i['role']).first()
                if obj is not None:
                    i['role'] = obj.name
                else:
                    i['role'] = ""

                
            response_={
                "n": 1,
                'msg':'Members found Successfully.',
                'data':combined_data
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
                "msg": 'member list not found',
                "data":[]                     
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
        
        id = request_data.get('id')
        if id is not None and id != "":
            userobj=UserAdmin.objects.filter(id=id,isActive=True).last()
            if userobj is not None:
                serializer = UserAdminSerializer(userobj)
                member_type = serializer.data['member_type']
                member_of = serializer.data['member_of']
                og_code =  serializer.data['og_code']
                selfid =   serializer.data['id']

                obj = UserAdmin.objects.filter(member_type = member_type,member_of=member_of,og_code=og_code,is_member=True,isActive=True).exclude(id=selfid)
                member_ser = UserAdminSerializer(obj,many=True)
            
                newadminobj = UserAdmin.objects.filter(id=member_of,isActive=True).first()
                userser =  UserAdminSerializer(newadminobj)


                combined_data = member_ser.data + [userser.data]
                for i in combined_data:
                    if i['name'] is not None and i['name'] != '':
                        i['username'] = i['name']
                    else:
                        i['username'] = i['first_name'] +" "+i['last_name']

                



                response_={
                    "n": 1,
                    'msg':'User Admin Details Found.',
                    'data':serializer.data,
                    'memberdata':combined_data
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
                    'msg':'No Data FOund.',
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
                'msg':'id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        

    

class DeleteMember(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        id = request_data.get('id')
        if id is not None and id !="":
            user_obj=UserAdmin.objects.filter(id=id,isActive=True).first()
            if user_obj is not None:
                user_obj.isActive = False
                user_obj.save()
                response_={
                    "n": 1,
                    'msg':'Member Deleted Successfully.',
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
                    'msg':'Member id not found.',
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
                'msg':'id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

        
class UpdateMember(GenericAPIView):
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
        id = request_data.get('id')
        if id is not None:
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['designation'] = request_data.get('designation')
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['email'] = str(request_data.get('email')).lower()
            data['role'] = request_data.get('role')
            data['reporting_to'] = request_data.get('reporting_to')
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['city'] = request_data.get('city')
            data['country'] = request_data.get('country')
            data['state'] = request_data.get('state')
            data['pincode'] = request_data.get('pincode')
            data['joining_date'] = request_data.get('joining_date')
        
            
            obj = UserAdmin.objects.filter(isActive=True).exclude(id=id)
            ser = UserAdminSerializer(obj,many=True)
            for p in ser.data:
                if str(p['first_name']).lower() == str(data['first_name']).lower():
                    response_={
                        "n": 0,
                        'msg':'First name already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            peobj=UserAdmin.objects.filter(id=id,isActive=True).first()
            if peobj is not None:
                serializer = UserAdminSerializer(peobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Member Updated Successfully.',
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
                        "n": 1,
                        'msg':'Member Not Updated.',
                        'data':serializer.errors
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                response_={
                    "n": 1,
                    'msg':'id not found.',
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
                "n": 1,
                'msg':'id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
  

            

   
 
