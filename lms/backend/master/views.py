from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import *
from master.serializers import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.jwt import UserAdminJWTAuthentication
from candidate.jwt import CandidateJWTAuthentication
from django.db import transaction
from adminauth.models import *
from adminauth.serializers import *
from feedback.models import *
from feedback.serializers import *
from adminauth.views import save_file
import urllib.parse
from adminauth.common import convertcreationdate,convertcreationtime
# Create your views here.
import json
from django.utils import timezone
from course.models import *
def phase_one_response(request, response_data):
    encrypted_header = request.headers.get("encrypted", "")

    if encrypted_header == "1":
        data_to_serialize = convert_decimals_to_float(response_data)
        encrypted_data = encrypt_data(
            json.dumps(data_to_serialize)
)
        return Response(encrypted_data, status=200)

    return Response(response_data, status=200)



























































# CATEGORY
class AddCategory(GenericAPIView):
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
        data['category_name'] = request_data.get('category_name')
        data['tags'] = request_data.get('tags')
        
        if data['category_name'] is not None and data['category_name'] !="":
            obj = Category.objects.filter(isActive=True)
            ser = CategorySerializer(obj,many=True)
            for c in ser.data:
                if (c['category_name']).lower() == (data['category_name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Category already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        cser = CategorySerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Category added successfully.',
                'data':cser.data
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
                'msg':'Category not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class CategoryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = Category.objects.filter(isActive=True)
        ser = CategorySerializer(obj,many=True)
        for i in ser.data:
                
            if i['tags'] != "" and i['tags'] is not None:
                try:

                    i['tags'] = json.loads(i['tags'])
                except ValueError:
                    i['tags']=''


        response_={
            "n": 1,
            'msg':'Category found successfully.',
            'data': ser.data
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
            catobj=Category.objects.filter(id=id,isActive=True).first()
            if catobj is not None:
                serializer = CategorySerializer(catobj)
                response_={
                    "n": 1,
                    'msg':'Category Details Found.',
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
            

class SubcatCategoryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        subobjs = Sub_Category.objects.filter(isActive=True).order_by('category_name').values_list('category_name', flat=True).distinct()
        obj = Category.objects.filter(id__in=subobjs,isActive=True)
        ser = CategorySerializer(obj,many=True)
        for i in ser.data:
            if i['tags'] != "" and i['tags'] is not None:
                try:

                    i['tags'] = json.loads(i['tags'])
                except ValueError:
                    i['tags']=''


        response_={
            "n": 1,
            'msg':'Category found successfully.',
            'data': ser.data
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
    
       
class UpdateCategory(GenericAPIView):
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
            data['category_name'] = request_data.get('category_name')
            data['tags'] = request_data.get('tags')
        
            obj = Category.objects.filter(isActive=True).exclude(id=data['id'])
            ser = CategorySerializer(obj,many=True)
            for p in ser.data:
                if str(p['category_name']).lower() == str(data['category_name']).lower():
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
            peobj=Category.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = CategorySerializer(peobj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Category Updated Successfully.',
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
                        'msg':'Category Not Updated.',
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
        

class DeleteCategory(GenericAPIView):
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
            cat_obj=Category.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Category Deleted Successfully.',
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
                    'msg':'Category id not found.',
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


class ChangeCategoryStatus(GenericAPIView):
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
            cat_obj=Category.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                if cat_obj.status:
                    cat_obj.status = False
                else:
                    cat_obj.status=True

                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Category status changed successfully.',
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
                    'msg':'Category id not found.',
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
 

class CategoryDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        category_id = request_data.get('id')

        if (
            category_id is None
            or category_id == ""
):
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Category id is required.",
                    "data": {}
                }
    )

        category_obj = Category.objects.filter(
            id=category_id,
            isActive=True
).first()

        if category_obj is None:
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Category not found.",
                    "data": {}
                }
    )

        return phase_one_response(
            request,
            {
                "n": 1,
                "msg": "Category details found successfully.",
                "data": CategorySerializer(category_obj).data
            }
)


# Sub_Category
class AddSub_Category(GenericAPIView):
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
        data['category_id'] = request_data.get('category_id')
        data['sub_name'] = request_data.get('sub_name')
        data['tags'] = request_data.get('tags')
        
        if data['sub_name'] is not None and data['sub_name'] !="":
            obj = Sub_Category.objects.filter(isActive=True)
            ser = Sub_CategorySerializer(obj,many=True)
            for c in ser.data:
                if (c['sub_name']).lower() == (data['sub_name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Sub Category already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        cser = Sub_CategorySerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Sub Category added successfully.',
                'data':cser.data
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
                'msg':'Category not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class Sub_CategoryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = Sub_Category.objects.filter(isActive=True)
        ser = Sub_CategorySerializer(obj,many=True)
        for s in ser.data:
            objdep = Category.objects.filter(id=s['category_id']).first()
            if objdep is not None and objdep !="":
                s['category_name'] = objdep.category_name
            else:
                s['category_name'] = ""
            if s['tags'] != "" and s['tags'] is not None:
                try:
                    s['tags'] = json.loads(s['tags'])
                except ValueError:
                    s['tags']=''




            
        response_={
            "n": 1,
            'msg':'Sub Category found successfully.',
            'data': ser.data
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
            catobj=Sub_Category.objects.filter(id=id,isActive=True).first()
            if catobj is not None:
                serializer = Sub_CategorySerializer(catobj)
                response_={
                    "n": 1,
                    'msg':'Sub Category Details Found.',
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
        
        
class UpdateSub_Category(GenericAPIView):
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
            data['category_id'] = request_data.get('category_id')
            data['sub_name'] = request_data.get('sub_name')
            data['tags'] = request_data.get('tags')
            obj = Sub_Category.objects.filter(isActive=True).exclude(id=data['id'])
            ser = Sub_CategorySerializer(obj,many=True)
            for p in ser.data:
                if str(p['sub_name']).lower() == str(data['sub_name']).lower():
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
                
            peobj=Sub_Category.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = Sub_CategorySerializer(peobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_ = {
                        "n": 1,
                        'msg':'Sub Category Updated Successfully.',
                        'data':serializer.data
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    print('errorrr',serializer.errors)
                    response_ = {
                        "n": 0,
                        'msg':'Sub Category Not Updated.',
                        'data':serializer.errors
                    }
                    if encryped_header == "1":
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                response_={
                    "n": 0,
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
        

class DeleteSub_Category(GenericAPIView):
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
            cat_obj=Sub_Category.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Sub Category Deleted Successfully.',
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
                    'msg':'Sub Category id not found.',
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
        
class ChangeSubCategoryStatus(GenericAPIView):
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
            cat_obj=Sub_Category.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                if cat_obj.status:
                    cat_obj.status = False
                else:
                    cat_obj.status=True

                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Sub Category status changed successfully.',
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
                    'msg':'Sub Category id not found.',
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
 

class SubCategoryDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        sub_category_id = request_data.get('id')

        if (
            sub_category_id is None
            or sub_category_id == ""
):
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Sub category id is required.",
                    "data": {}
                }
    )

        sub_category_obj = Sub_Category.objects.filter(
            id=sub_category_id,
            isActive=True
).first()

        if sub_category_obj is None:
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Sub category not found.",
                    "data": {}
                }
    )

        return phase_one_response(
            request,
            {
                "n": 1,
                "msg": "Sub category details found successfully.",
                "data": Sub_CategorySerializer(sub_category_obj).data
            }
)


        
# Department
class AddDepartment(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        print("request.user.role_id",request.user.role)
        if request.user.role is not None and request.user.role not in [3,4] :
            response_={
                "n": 0,
                'msg':"Only College Admin Can Add Departments",
                'data':{}
            }    
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



        
        data = {
                "og_code": str(request.user.og_code),
                "college_id":str(request.user.id),
                "department_code": request_data.get(
                    "department_code"
        ),
                "department_name": request_data.get(
                    "department_name"
        ),
                "hod_faculty_id": request_data.get(
                    "hod_faculty_id"
        ),
                "tags": request_data.get("tags"),
                "status": request_data.get("status", True),
                "createdBy": str(request.user.id),
            }



        if data['department_name'] is not None and data['department_name'] !="":
            obj = Department.objects.filter(isActive=True,og_code=data['og_code'])
            ser = DepartmentSerializer(obj,many=True)
            for c in ser.data:
                if (c['department_name']).lower() == (data['department_name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Department already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        cser = DepartmentSerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Department added successfully.',
                'data':cser.data
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
                'msg':'Department not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class DepartmentList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = Department.objects.filter(isActive=True)
        ser = DepartmentSerializer(obj,many=True)
        ser_data=ser.data
        for i in ser.data:
            if i['hod_faculty_id'] != "" and i['hod_faculty_id'] is not None:
                print("i['hod_faculty_id']",i['hod_faculty_id'])
                hod_obj=UserAdmin.objects.filter(id=str(i['hod_faculty_id'])).first()
                if hod_obj is not None:
                    i['hod_name'] = str(hod_obj.first_name) +' '+ str(hod_obj.last_name)
                else:
                    i['hod_name']=''
            else:
                i['hod_name']=''
                
            if i['tags'] != "" and i['tags'] is not None:
                try:
                    i['tags'] = json.loads(i['tags'])
                except ValueError:
                    i['tags']=''
        
        response_={
            "n": 1,
            'msg':'Department found successfully.',
            'data': ser_data
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
            dep_obj=Department.objects.filter(id=id,isActive=True).first()
            if dep_obj is not None:
                serializer = DepartmentSerializer(dep_obj)
                response_={
                    "n": 1,
                    'msg':'Department Details Found.',
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
        
        
class DepartmentDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        department_id = request_data.get('id')

        if (
            department_id is None
            or department_id == ""
):
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Department id is required.",
                    "data": {}
                }
    )

        department_obj = Department.objects.filter(
            id=department_id,
            isActive=True
).first()

        if department_obj is None:
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Department not found.",
                    "data": {}
                }
    )

        return phase_one_response(
            request,
            {
                "n": 1,
                "msg": "Department details found successfully.",
                "data": DepartmentSerializer(department_obj).data
            }
)


class UpdateDepartment(GenericAPIView):
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
            data['department_name'] = request_data.get('department_name')
            data['tags'] = request_data.get('tags')
        
            obj = Department.objects.filter(isActive=True).exclude(id=data['id'])
            ser = DepartmentSerializer(obj,many=True)
            for d in ser.data:
                if str(d['department_name']).lower() == str(data['department_name']).lower():
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
            d_obj=Department.objects.filter(id=data['id'],isActive=True).first()
            if d_obj is not None:
                serializer = DepartmentSerializer(d_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Department Updated Successfully.',
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
                        'msg':'Department Not Updated.',
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
        

class DeleteDepartment(GenericAPIView):
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
            dep_obj=Department.objects.filter(id=id,isActive=True).first()
            if dep_obj is not None:
                dep_obj.isActive = False
                dep_obj.save()
                response_={
                    "n": 1,
                    'msg':'Department Deleted Successfully.',
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
                    'msg':'Department id not found.',
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
        

class ChangeDepartmentStatus(GenericAPIView):
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
            dep_obj=Department.objects.filter(id=id,isActive=True).first()
            if dep_obj is not None:
                if dep_obj.status:

                    dep_obj.status = False
                else:
                    dep_obj.status = True

                dep_obj.save()
                response_={
                    "n": 1,
                    'msg':'Department Status changed Successfully.',
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
                    'msg':'Department id not found.',
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
        
       
# Rank
class AddRank(GenericAPIView):
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
        data['department_name'] = request_data.get('department_name')
        data['rank'] = request_data.get('rank')
        data['tags'] = request_data.get('tags')
        
        if data['rank'] is not None and data['rank'] !="":
            obj = Rank.objects.filter(isActive=True)
            ser = RankSerializer(obj,many=True)
            for c in ser.data:
                if (c['rank']).lower() == (data['rank']).lower():
                    response_={
                        "n": 0,
                        'msg':"Rank already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        r_ser = RankSerializer(data=data)
        if r_ser.is_valid():
            r_ser.save()
            response_={
                "n": 1,
                'msg':'Rank added successfully.',
                'data':r_ser.data
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
                'msg':'Rank not added.',
                'data':r_ser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class RankList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        obj = Rank.objects.filter(isActive=True)
        ser = RankSerializer(obj,many=True)
        for s in ser.data:
            objdep = Department.objects.filter(id=s['department_name']).first()
            s['department_name_str'] = objdep.department_name
                
            if s['tags'] != "" and s['tags'] is not None:
                try:
                    s['tags'] = json.loads(s['tags'])
                except ValueError:
                    s['tags']=''
        response_={
            "n": 1,
            'msg':'Rank found successfully.',
            'data': ser.data
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
            r_obj=Rank.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                serializer = RankSerializer(r_obj)
                response_={
                    "n": 1,
                    'msg':'Rank Details Found.',
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

        
class UpdateRank(GenericAPIView):
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
            data['department_name'] = request_data.get('department_name')
            data['rank'] = request_data.get('rank')
            data['tags'] = request_data.get('tags')
        
            obj = Rank.objects.filter(isActive=True).exclude(id=data['id'])
            ser = RankSerializer(obj,many=True)
            for d in ser.data:
                if str(d['rank']).lower() == str(data['rank']).lower():
                    response_={
                        "n": 0,
                        'msg':'Rank already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            r_obj=Rank.objects.filter(id=data['id'],isActive=True).first()
            if r_obj is not None:
                serializer = RankSerializer(r_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Rank Updated Successfully.',
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
                        'msg':'Rank Not Updated.',
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
        

class DeleteRank(GenericAPIView):
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
            r_obj=Rank.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                r_obj.isActive = False
                r_obj.save()
                response_={
                    "n": 1,
                    'msg':'Rank Deleted Successfully.',
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
                    'msg':'Rank id not found.',
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
        
class ChangeRankStatus(GenericAPIView):
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
            r_obj=Rank.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                if r_obj.status:
                    r_obj.status = False
                else:
                    r_obj.status = True

                r_obj.save()
                response_={
                    "n": 1,
                    'msg':'Rank Status Changed Successfully.',
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
                    'msg':'Rank id not found.',
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
        
class GetDepartmentRanks(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        obj = Rank.objects.filter(isActive=True,status=True)

        department_ids=request_data.get('department_ids')
        if department_ids is not None and department_ids !='':
            obj=obj.filter(department_name__in=department_ids)
        
        ser = RankSerializer(obj,many=True)






        for s in ser.data:
            objdep = Department.objects.filter(id=s['department_name']).first()
            s['department_name_str'] = objdep.department_name
                
            if s['tags'] != "" and s['tags'] is not None:
                try:
                    s['tags'] = json.loads(s['tags'])
                except ValueError:
                    s['tags']=''
        response_={
            "n": 1,
            'msg':'Rank found successfully.',
            'data': ser.data
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
    

 
# Documents
class AddDocuments(GenericAPIView):
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
        data['role'] = request_data.get('role')
        data['document_name'] = request_data.get('document_name')
        data['description'] = request_data.get('description')
        data['isActive'] = True
        
        if data['document_name'] is not None and data['document_name'] !="":
            obj = Documents.objects.filter(isActive=True)
            ser = DocumentsSerializer(obj,many=True)
            for c in ser.data:
                if (c['document_name']).lower() == (data['document_name']).lower() and c['role'] == data['role']:
                    response_={
                        "n": 0,
                        'msg':"Documents already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        d_ser = DocumentsSerializer(data=data)
        if d_ser.is_valid():
            d_ser.save()
            response_={
                "n": 1,
                'msg':'Documents added successfully.',
                'data':d_ser.data
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
                'msg':'Documents not added.',
                'data':d_ser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class DocumentsList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = Documents.objects.filter(isActive=True)
        ser = DocumentsSerializer(obj,many=True)
        for i in ser.data:
            main_object = MainRoles.objects.filter(id=i['role']).first()
            if main_object is not None:
                i['role_name'] = main_object.name
            else:
                i['role_name'] = ""
        response_={
            "n": 1,
            'msg':'Documents found successfully.',
            'data': ser.data
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
            r_obj=Documents.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                serializer = DocumentsSerializer(r_obj)
                response_={
                    "n": 1,
                    'msg':'Documents Details Found.',
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
        
        
class UpdateDocuments(GenericAPIView):
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
            data['role'] = request_data.get('role')
            data['document_name'] = request_data.get('document_name')
            data['description'] = request_data.get('description')
        
            obj = Documents.objects.filter(isActive=True).exclude(id=data['id'])
            ser = DocumentsSerializer(obj,many=True)
            for d in ser.data:
                if str(d['document_name']).lower() == str(data['document_name']).lower() and d['role'] == data['role']:
                    response_={
                        "n": 0,
                        'msg':'Documents already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                    
            r_obj=Documents.objects.filter(id=data['id'],isActive=True).first()
            if r_obj is not None:
                serializer = DocumentsSerializer(r_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Documents Updated Successfully.',
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
                        'msg':'Documents Not Updated.',
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
        

class DeleteDocuments(GenericAPIView):
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
            d_obj=Documents.objects.filter(id=id,isActive=True).first()
            if d_obj is not None:
                d_obj.isActive = False
                d_obj.save()
                response_={
                    "n": 1,
                    'msg':'Documents Deleted Successfully.',
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
                    'msg':'Documents id not found.',
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
        
        
class ChangeDocumentStatus(GenericAPIView):
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
            d_obj=Documents.objects.filter(id=id,isActive=True).first()
            if d_obj is not None:
                if d_obj.status:

                    d_obj.status = False
                else:
                    d_obj.status = True
                    
                d_obj.save()
                response_={
                    "n": 1,
                    'msg':'Documents Status Changed Successfully.',
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
                    'msg':'Documents id not found.',
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
        
       


# Languages
class AddLanguages(GenericAPIView):
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
        data['languages_name'] = request_data.get('languages_name')
        
        if data['languages_name'] is not None and data['languages_name'] !="":
            obj = Languages.objects.filter(isActive=True)
            ser = LanguagesSerializer(obj,many=True)
            for c in ser.data:
                if (c['languages_name']).lower() == (data['languages_name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Languages already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        d_ser = LanguagesSerializer(data=data)
        if d_ser.is_valid():
            d_ser.save()
            response_={
                "n": 1,
                'msg':'Languages added successfully.',
                'data':d_ser.data
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
                'msg':'Languages not added.',
                'data':d_ser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class LanguagesList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        obj = Languages.objects.filter(isActive=True)
        ser = LanguagesSerializer(obj,many=True)
        response_={
            "n": 1,
            'msg':'Languages found successfully.',
            'data': ser.data
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
            l_obj=Languages.objects.filter(id=id,isActive=True).first()
            if l_obj is not None:
                serializer = LanguagesSerializer(l_obj)
                response_={
                    "n": 1,
                    'msg':'Languages Details Found.',
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
        
        
class UpdateLanguages(GenericAPIView):
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
            data['languages_name'] = request_data.get('languages_name')
            
            obj = Languages.objects.filter(isActive=True).exclude(id=data['id'])
            ser = LanguagesSerializer(obj,many=True)
            for d in ser.data:
                if str(d['languages_name']).lower() == str(data['languages_name']).lower():
                    response_={
                        "n": 0,
                        'msg':'Languages already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            l_obj=Languages.objects.filter(id=data['id'],isActive=True).first()
            if l_obj is not None:
                serializer = LanguagesSerializer(l_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Languages Updated Successfully.',
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
                        'msg':'Languages Not Updated.',
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
        

class DeleteLanguages(GenericAPIView):
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
            l_obj=Languages.objects.filter(id=id,isActive=True).first()
            if l_obj is not None:
                l_obj.isActive = False
                l_obj.save()
                response_={
                    "n": 1,
                    'msg':'Languages Deleted Successfully.',
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
                    'msg':'Languages id not found.',
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
        
        
# Specialization
class AddSpecialization(GenericAPIView):
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
        data['specialization_name'] = request_data.get('specialization_name')
        
        if data['specialization_name'] is not None and data['specialization_name'] !="":
            obj = Specialization.objects.filter(isActive=True)
            ser = SpecializationSerializer(obj,many=True)
            for c in ser.data:
                if (c['specialization_name']).lower() == (data['specialization_name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Specialization already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        s_ser = SpecializationSerializer(data=data)
        if s_ser.is_valid():
            s_ser.save()
            response_={
                "n": 1,
                'msg':'Specialization added successfully.',
                'data':s_ser.data
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
                'msg':'Specialization not added.',
                'data':s_ser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class SpecializationList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        obj = Specialization.objects.filter(isActive=True)
        ser = SpecializationSerializer(obj,many=True)
        response_={
            "n": 1,
            'msg':'Specialization found successfully.',
            'data': ser.data
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
            s_obj=Specialization.objects.filter(id=id,isActive=True).first()
            if s_obj is not None:
                serializer = SpecializationSerializer(s_obj)
                response_={
                    "n": 1,
                    'msg':'Specialization Details Found.',
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
        
        
class UpdateSpecialization(GenericAPIView):
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
            data['specialization_name'] = request.get('specialization_name')
            
            obj = Specialization.objects.filter(isActive=True).exclude(id=data['id'])
            ser = SpecializationSerializer(obj,many=True)
            for d in ser.data:
                if str(d['specialization_name']).lower() == str(data['specialization_name']).lower():
                    response_={
                        "n": 0,
                        'msg':'Specialization already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            s_obj=Specialization.objects.filter(id=data['id'],isActive=True).first()
            if s_obj is not None:
                serializer = SpecializationSerializer(s_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Specialization Updated Successfully.',
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
                        'msg':'Specialization Not Updated.',
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
        

class DeleteSpecialization(GenericAPIView):
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
            s_obj=Specialization.objects.filter(id=id,isActive=True).first()
            if s_obj is not None:
                s_obj.isActive = False
                s_obj.save()
                response_={
                    "n": 1,
                    'msg':'Specialization Deleted Successfully.',
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
                    'msg':'Specialization id not found.',
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
        
# Branch       
class AddBranch(GenericAPIView):
    
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
        data['college'] = request_data.get('college')
        data['mobilenumber'] = request_data.get('mobilenumber')
        data['email'] = str(request_data.get('email')).lower()      
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None
        data['landmark'] = request_data.get('landmark') 
        data['og_code'] = str(request.user.og_code)
        data['createdBy'] = str(request.user.id)
        
        coordinator_list = request_data.get('coordinator_list')
        
        email_object = Branch.objects.filter(isActive=True,email=data['email']).first()
        number_object = Branch.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
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
        
        serializer = BranchSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            if coordinator_list != []:
                for i in coordinator_list:
                    Coordinator.objects.create(
                        createdBy = str(request.user.id),
                        branch_id = serializer.data['id'],
                        coordinator_name = i['coordinator_name'],
                        coordinator_number = i['coordinator_number'],
                        coordinator_email = i['coordinator_email'],
                        coordinator_designation = i['coordinator_designation'],
            )
            response_={
                        "n": 1,
                        "msg": 'Branch added successfully',
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
                        "msg": 'Branch not registered',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class UpdateBranch(GenericAPIView):
    
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
            
        user_object = Branch.objects.filter(id=updated_of_user_id).first()
        if user_object is None:
            response_={
                        "n": 0,        
                        "msg": 'Branch not Found',
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
        data['college'] = request_data.get('college')
        data['mobilenumber'] = request_data.get('mobilenumber')   
        data['email'] = str(request_data.get('email')).lower()
        data['source'] = request_data.get('source')
        data['no_of_classroom'] = request_data.get('no_of_classroom')
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['city'] = request_data.get('city')
        data['pincode'] = request_data.get('pincode')
        data['landmark'] = request_data.get('landmark')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None   
        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()
        
        coordinator_list = request_data.get('coordinator_list')
        email_object = Branch.objects.filter(isActive=True,email=data['email']).exclude(id=updated_of_user_id).first()
        number_object = Branch.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).exclude(id=updated_of_user_id).first()
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
        
        serializer = BranchSerializer(user_object,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            if coordinator_list != []:
                Coordinator.objects.filter(branch_id=serializer.data['id']).update(isActive=False)
                for i in coordinator_list:
                    Coordinator.objects.create(
                        createdBy = str(request.user.id),
                        branch_id = serializer.data['id'],
                        coordinator_name = i['coordinator_name'],
                        coordinator_number = i['coordinator_number'],
                        coordinator_email = i['coordinator_email'],
                        coordinator_designation = i['coordinator_designation'],
            )
            response_={
                        "n": 1,
                        "msg": 'Branch updated successfully',
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
                        "msg": 'Branch not updated',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class UploadBranchDocumentFormData(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        branch_id = request.data.getlist('branch_id')
        doc_ids = request.data.getlist('doc_id')
        doc_names = request.data.getlist('doc_name')
        file_uploads = request.FILES.getlist('document_file_upload')

        # Creating the list of dictionaries
        result = [
                    {
                        'branch_id': branch_id,
                        'doc_id': doc_id,
                        'doc_name': doc_name,
                        'document_file_upload': file_upload,
                    }
                    for branch_id, doc_id, doc_name, file_upload in zip(branch_id, doc_ids, doc_names, file_uploads)
                ]
            
    
        docsUpload = request.FILES.getlist('document_file_upload')
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Documents','Branch')

        file_url_list = []
        for i in result:
     
            file_url=save_file(folder_path,i['document_file_upload'],request)
            user_doc = UserDocuments.objects.filter(isActive=True,branch_id = i['branch_id'],document_url =file_url).update(isActive=True)
            
            # if user_doc is None:
            UserDocuments.objects.create(
                document_id = i['doc_id'],
                document_name = i['doc_name'],
                branch_id = i['branch_id'],
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
            
class BranchList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')


        branchobject = Branch.objects.filter(isActive=True,college=str(request.user.id)).order_by('-createdAt')
        branch_ser = BranchSerializer(branchobject,many=True)
        for i in branch_ser.data:
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""
        
        response_={
                    "n": 1,
                    "msg": 'Branch fetched successfully',
                    "data":branch_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
class BranchDetails(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        branch_id = request_data.get('id')
        if branch_id is None or branch_id == "":
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
        user_object = Branch.objects.filter(id=branch_id).first()
        if user_object is None:
            response_={
                    "n": 0,
                    "msg": 'Branch not found',
                    "data":[]                        
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        serializer = BranchSerializer(user_object)
        serializer_data = serializer.data
        user_doc_object = UserDocuments.objects.filter(isActive=True,branch_id=branch_id)
        user_doc_ser = UserDocumentSerializer(user_doc_object,many=True)
        coordinator_object = Coordinator.objects.filter(isActive=True,branch_id=branch_id)
        coordinator_ser = CoordinatorSerializer(coordinator_object,many=True)
        documents_required_object = Documents.objects.filter(isActive=True,role=7)
        documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
        
        tc_object = UserAdmin.objects.filter(isActive=True,id=serializer.data['college']).first()
        if tc_object is not None:
            college_name = tc_object.name
        else:
            college_name = ""
        
        for d in documents_required_ser.data:
            doc_object = UserDocuments.objects.filter(isActive=True,branch_id=branch_id,document_id=d['id']).first()
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
        
        serializer_data.update({
            "document_data":user_doc_ser.data,
            "coordinator_data":coordinator_ser.data,
            "proof_data":documents_required_ser.data,
            "state_name":state_name,
            "country_name":country_name,
            "college_name":college_name,
        })
        response_={
                    "n": 1,
                    "msg": 'Branch data fetched successfully',
                    "data":serializer_data                       
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

        


 
# 

class SaveS3Uploads(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        # encryped_header = ""
        # if 'encrypted' in request.headers.keys():
        #     encryped_header = request.headers.get('encrypted')

        file_list = request.FILES.getlist('file_list')
        data = {}
        course = request.data.get('course_list')
        module = request.data.get('module_list')
        s3_tags = request.POST.get('s3tags')
        cretby = str(request.user.id)

        folder_path = os.path.join(settings.MEDIA_ROOT,'media','S3 Uploads')
        if file_list != "":
            for f in file_list:
                if f is not None and f != '':
                    file_url=save_file(folder_path,f,request)
                    S3Upload.objects.create(
                        course = course,
                        module = module,
                        s3_tags = s3_tags,
                        s3_file = file_url,
                        createdBy = cretby
            )

            response_={
                    "n": 0,
                    "msg": 'S3 files uploaded successfully',
                    "data":[]                     
                }
            return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'Please provide files',
                        "data":[]                     
                    }
            # if encryped_header == "1" :
            #     data_to_serialize = convert_decimals_to_float(response_)
            #     encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(response_,status=200)
        

# import requests

class S3UploadsList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        s3obj = S3Upload.objects.filter(isActive=True).order_by('-createdAt')
        s3_ser = S3UploadSerializer(s3obj,many=True)
        for i in s3_ser.data:
            url = i['s3_file']
            if url is not None and url != '':
                filename = urllib.parse.unquote(url.split('/')[-1])
                filename_without_ext = filename.rsplit('.', 1)[0] 
                i['filename'] = filename_without_ext
                i['fileurl'] = filename
            else:
                i['filename'] = ''
                i['fileurl'] = ''

            # response = requests.head(url)  

            # if "Content-Length" in response.headers:
            #     file_size = int(response.headers["Content-Length"])  # Size in bytes
            #     # Convert to KB or MB
            #     if file_size < 1024:
            #         size_str = f"{file_size} Bytes"
            #     elif file_size < 1024**2:
            #         size_str = f"{file_size / 1024:.2f} KB"
            #     else:
            #         size_str = f"{file_size / 1024**2:.2f} MB"

            # else:
            #     size_str= ''

            # i['size_str'] = size_str 

            crtby = i['createdBy']
            userobj = UserAdmin.objects.filter(id=crtby).first()
            if userobj is not None and userobj != '':
                if userobj.user_type == 5:
                    i['added_by'] = userobj.first_name +" "+userobj.last_name
                else:
                    i['added_by'] = userobj.name
            else:
                i['added_by'] = ''


            i['added_on']= convertcreationdate(i['createdAt'])


           
        response_={
                    "n": 1,
                    "msg": 'data fetched successfully',
                    "data":s3_ser.data                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class DeleteS3File(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        id = request_data.get('s3id')
        if id is not None and id !="":
            d_obj=S3Upload.objects.filter(id=id,isActive=True).first()
            if d_obj is not None:
                d_obj.isActive = False
                d_obj.save()
                response_={
                    "n": 1,
                    'msg':'S3 File Deleted Successfully.',
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
                    'msg':'s3 file id not found.',
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
            


# Enquiry
class AddEnquiry(GenericAPIView):
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
        data['name'] = request_data.get('name')
        data['contact'] = request_data.get('contact')
        data['email'] = request_data.get('email')
        data['message'] = request_data.get('message')
        data['status'] = 'Pending'
        data['createdBy'] = str(request.user.id)
        
        cser = EnquiriesSerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Enquiry added successfully.',
                'data':cser.data
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
                'msg':'Enquiry not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
class EnquiryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        status = request_data.get('status')
        if status is not None and status != '':
            obj = Enquiries.objects.filter(isActive=True,status = status)
            ser = EnquiriesSerializer(obj,many=True)
            response_={
                "n": 1,
                'msg':'Enquiries found successfully.',
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
                'msg':'Status not provided.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

# class AddVessel
class AddVessel(GenericAPIView):
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
        data['name'] = request_data.get('name')
        data['code'] = request_data.get('code')
        data['category'] = request_data.get('category')
        data['subcategory'] = request_data.get('subcategory')
        data['imo_number'] = request_data.get('imo_number')
        data['mmsi_number'] = request_data.get('mmsi_number')
        data['flag_state'] = request_data.get('flag_state')
        data['registry_port'] = request_data.get('registry_port')
        data['built_year'] = request_data.get('built_year')
        data['shipyard_builder'] = request_data.get('shipyard_builder')
        data['class_society'] = request_data.get('class_society')

        data['owner_name'] = request_data.get('owner_name')
        data['technical_manager'] = request_data.get('technical_manager')
        data['commercial_manager'] = request_data.get('commercial_manager')
        data['operator'] = request_data.get('operator')
        data['PI_club'] = request_data.get('PI_club')
        data['createdBy'] = str(request.user.id)
        
        cser = VesselSerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Vessel added successfully.',
                'data':cser.data
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
                'msg':'Vessel not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class AddVesselDetails(GenericAPIView):
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
        vessel_id = request_data.get('id')
        data['last_dry_dock_date'] = request_data.get('last_dry_dock_date')
        data['next_dry_dock_date'] = request_data.get('next_dry_dock_date')
        data['last_survey_date'] = request_data.get('last_survey_date')
        data['next_survey_due_date'] = request_data.get('next_survey_due_date')
        data['fuel_consumption_rates'] = request_data.get('fuel_consumption_rates')
        data['maintenance_history'] = request_data.get('maintenance_history')
        data['updatedBy'] = str(request.user.id)

        if vessel_id is not None and vessel_id != '':
            vesselobj =  Vessel.objects.filter(id=vessel_id,isActive=True).first()
            if vesselobj is not None:
                cser = VesselSerializer(vesselobj,data=data,partial=True)
                if cser.is_valid():
                    cser.save()
                    response_={
                        "n": 1,
                        'msg':'Vessel details added successfully.',
                        'data':cser.data
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
                    'msg':'vessel details not added',
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
                'msg':'vessel not found',
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
                'msg':'Please provide vessel id.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class VesselList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        serachtext = request_data.get('serachtext')
        if serachtext is not None and serachtext != '':
            obj = Vessel.objects.filter(isActive=True,name__icontains = serachtext)
        else:
            obj = Vessel.objects.filter(isActive=True)
        
        if obj.exists():
            page4 = self.paginate_queryset(obj)
            serializer =  VesselSerializer(page4,many=True)
            for i in serializer.data:
                countryobj = Country.objects.filter(id=i['flag_state']).first()
                i['flag_state'] = countryobj.name

                i['built_year'] = datefiltergetyear(i['built_year'])

                catobj = Category.objects.filter(id=i['category']).first()
                i['category'] = catobj.category_name

                subcatobj = Sub_Category.objects.filter(id=i['subcategory']).first()
                i['subcategory'] = subcatobj.sub_name

                if i['status'] is False:
                    i['status'] = 'InActive'
                else:
                    i['status'] = 'Active'

                
            response_={
                "n": 1,
                'msg':'vessel list found successfully.',
                'data': serializer.data
            }
            if encryped_header == "1" :
                paigna=self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'no vessels',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class GetVesselDetails(GenericAPIView):

    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        vessel_id = request_data.get('id')
        if vessel_id is not None and vessel_id != '':
            vesselobj =  Vessel.objects.filter(id=vessel_id,isActive=True).first()
            if vesselobj is not None:
                cser = VesselSerializer(vesselobj)
                serializer_data = cser.data
                if serializer_data['maintenance_history'] is None or  serializer_data['maintenance_history'] == '':
                    maintenance_history = ''
                else:
                    maintenance_history = serializer_data['maintenance_history']

                countryobj = Country.objects.filter(id=serializer_data['flag_state']).first()
                new_flag_state = countryobj.name

                str_built_year = datefiltergetyear(serializer_data['built_year'])

                catobj = Category.objects.filter(id=serializer_data['category']).first()
                str_category = catobj.category_name

                subcatobj = Sub_Category.objects.filter(id=serializer_data['subcategory']).first()
                str_subcategory = subcatobj.sub_name
                
                ab = serializer_data['last_dry_dock_date']
                if ab is not None and ab != '':
                    new_last_dry_dock_date = datefilterchangeformat(ab)
                else:
                    new_last_dry_dock_date = ''

                ndds = serializer_data['next_dry_dock_date']
                if ndds is not None and ndds != '':
                    new_next_dry_dock_date = datefilterchangeformat(ndds)
                else:
                    new_next_dry_dock_date = ''

                nlsd = serializer_data['last_survey_date']
                if nlsd is not None and nlsd != '':
                    new_last_survey_date = datefilterchangeformat(nlsd)
                else:
                    new_last_survey_date = ''

                nsdd = serializer_data['next_survey_due_date']
                if nsdd is not None and nsdd != '':
                    new_next_survey_due_date = datefilterchangeformat(nsdd)
                else:
                    new_next_survey_due_date = ''

                serializer_data.update({
                    "maintenance_history":maintenance_history,
                    "new_flag_state":new_flag_state,
                    "str_built_year":str_built_year,
                    "str_category":str_category,
                    "str_subcategory":str_subcategory,
                    "new_last_dry_dock_date":new_last_dry_dock_date,
                    "new_next_dry_dock_date":new_next_dry_dock_date,
                    "new_last_survey_date":new_last_survey_date,
                    "new_next_survey_due_date":new_next_survey_due_date
                })

                response_={
                    "n": 1,
                    'msg':'Vessel details found successfully.',
                    'data':serializer_data
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
                'msg':'vessel details not found',
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
                'msg':'Please provide vessel id.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            


class UpdateVessel(GenericAPIView):
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
        vessel_id = request_data.get('id')
        data['name'] = request_data.get('name')
        data['code'] = request_data.get('code')
        data['category'] = request_data.get('category')
        data['subcategory'] = request_data.get('subcategory')
        data['imo_number'] = request_data.get('imo_number')
        data['mmsi_number'] = request_data.get('mmsi_number')
        data['flag_state'] = request_data.get('flag_state')
        data['registry_port'] = request_data.get('registry_port')
        data['built_year'] = request_data.get('built_year')
        data['shipyard_builder'] = request_data.get('shipyard_builder')
        data['class_society'] = request_data.get('class_society')

        data['owner_name'] = request_data.get('owner_name')
        data['technical_manager'] = request_data.get('technical_manager')
        data['commercial_manager'] = request_data.get('commercial_manager')
        data['operator'] = request_data.get('operator')
        data['PI_club'] = request_data.get('PI_club')
        data['updatedBy'] = str(request.user.id)
        
        if vessel_id is not None and vessel_id != '':
            vesselobj =  Vessel.objects.filter(id=vessel_id,isActive=True).first()
            if vesselobj is not None:
                cser = VesselSerializer(vesselobj,data=data,partial=True)
                if cser.is_valid():
                    cser.save()
                    response_={
                        "n": 1,
                        'msg':'Vessel updated successfully.',
                        'data':cser.data
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
                    'msg':'vessel not updated',
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
                'msg':'vessel not found',
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
                'msg':'Please provide vessel id.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)






class DeleteVessel(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
       
        vessel_id = request_data.get('id')
        if vessel_id is not None and vessel_id != '':
            vesselobj =  Vessel.objects.filter(id=vessel_id,isActive=True).first()
            if vesselobj is not None:
                vesselobj.isActive = False
                vesselobj.updatedBy = str(request.user.id)
                vesselobj.save()
                response_={
                    "n": 1,
                    'msg':'Vessel deleted successfully.',
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
                'msg':'vessel not found',
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
                'msg':'Please provide vessel id.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class ChangeVesselStatus(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
       
        vessel_id = request_data.get('id')
        if vessel_id is not None and vessel_id != '':
            vesselobj =  Vessel.objects.filter(id=vessel_id,isActive=True).first()
            if vesselobj is not None:
                if vesselobj.status is True:
                    change_status = False
                else:
                    change_status = True

                vesselobj.status = change_status
                vesselobj.updatedBy = str(request.user.id)
                vesselobj.save()
                response_={
                    "n": 1,
                    'msg':'Vessel status updated successfully.',
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
                'msg':'vessel not found',
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
                'msg':'Please provide vessel id.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)




class GetDocuments(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        rolename = request_data.get('rolename')
        if rolename is not None and rolename != "":
            roleobj = MainRoles.objects.filter(name__iexact=rolename,documents_required=True).first()
            if roleobj is not None:
                roleid = roleobj.id
                r_obj = Documents.objects.filter(role=roleid,isActive=True)
                if r_obj is not None:
                    serializer = DocumentsSerializer(r_obj,many=True)
                    response_={
                        "n": 1,
                        'msg':'Documents Details Found.',
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
                'msg':'role name is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

class GetQualifications(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        all_qualifications_objs=EducationalQualifications.objects.filter(isActive=True)
        qualifications_serializer=EducationalQualificationsSerializer(all_qualifications_objs,many=True)
        response_={
            "n": 1,
            'msg':'qualifications Details Found.',
            'data':qualifications_serializer.data
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
      
        
class AddCountry(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        request_data = request.POST.copy()
        request_data['createdAt'] = timezone.now()
        request_data['created_at'] = str(timezone.now())
        request_data['isActive'] = True
        if request.FILES.get('flag_image') is not None and request.FILES.get('flag_image') !='':
            request_data['flag_image']=request.FILES.get('flag_image')
        pujaenrobj = Country.objects.filter(isActive=True)
        pserializer= CountrySerializer(pujaenrobj,many=True)
        if pserializer.data !=[]:
            for p in pserializer.data:
                if str(p['name']) == str(request_data['name']):
                    response_={
                        'status':'failed',
                        'msg':'Country already exist.',
                        'data':{}
                    }
                    return Response(response_,status=200)
           
        serializer = CountrySerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            response_={
                        'status':'success',
                        'msg':'Country added Successfully.',
                        'data':serializer.data
                    }
            return Response(response_,status=200)
        else:
            response_={
                        'status':'failed',
                        'msg':'Country Not added.',
                        'data':serializer.errors
                    }
            return Response(response_,status=200)
        
class CountryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self,request):

        catblogobj=Country.objects.filter(isActive=True).order_by('name')
        if catblogobj.exists():
            serializer = CountrySerializer(catblogobj,many=True)
 
            response_={
                    'status':'success',
                    'msg':'Country List Found.',
                    'data':serializer.data
                }
            return Response(response_,status=200)
        else:
            response_={
                'status':'failed',
                'msg':'No Data FOund.',
                'data':{}
            }
            return Response(response_,status=200)
        
    def post(self,request):
        id = request.POST.get('id')
        if id is not None and id != "":
            catblogobj=Country.objects.filter(id=id).first()
            if catblogobj is not None:
                serializer = CountrySerializer(catblogobj)
                response_={
                    'status':'success',
                    'msg':'Country Details Found.',
                    'data':serializer.data
                    }
                return Response(response_,status=200)
            else:
                response_={
                    'status':'failed',
                    'msg':'No Data FOund.',
                    'data':{}
                }
                return Response(response_,status=200)
        else:
            response_={
                'status':'failed',
                'msg':'id is required.',
                'data':{}
            }
            return Response(response_,status=200)
        
class UpdateCountry(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        request_data = request.POST.copy()
        request_data['id'] = request.POST.get('id')
        if request_data['id'] is not None and request_data['id'] !="":
            request_data['updatedAt'] = timezone.now()
            # request_data['updatedBy'] = request.session.get('user_id')
            if request.FILES.get('flag_image') is not None and request.FILES.get('flag_image') !='':
                request_data['flag_image']=request.FILES.get('flag_image')


            pujaenrobj = Country.objects.filter(isActive=True).exclude(id=request_data['id'])
            pserializer= CountrySerializer(pujaenrobj,many=True)
            if pserializer.data !=[]:
                for p in pserializer.data:
                    if str(p['name']) == str(request_data['name']):
                        response_={
                            'status':'failed',
                            'msg':'Country already exist.',
                            'data':{}
                        }
                        return Response(response_,status=200)
                   
            cobj=Country.objects.filter(id=request_data['id'],isActive=True).first()
            serializer = CountrySerializer(cobj,data=request_data,partial=True)
            if serializer.is_valid():
                serializer.save()
                response_={
                            'status':'success',
                            'msg':'Country updated Successfully.',
                            'data':serializer.data
                        }
                return Response(response_,status=200)
            else:
                print("errors",serializer.errors)
                response_={
                            'status':'failed',
                            'msg':'Country Not Updated.',
                            'data':serializer.errors
                        }
                return Response(response_,status=200)
        else:
            response_={
                        'status':'failed',
                        'msg':'id is required.',
                        'data':{}
                    }
            return Response(response_,status=200)

class DeleteCountry(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        sl_id = request.POST.get('id')
        if sl_id is not None and sl_id !="":
            storage_obj=Country.objects.filter(id=sl_id).first()

            if storage_obj is not None :
                if storage_obj.isActive == True:
                    storage_obj.isActive = False
                    storage_obj.save()
                    response_={
                        'status':'success',
                        'msg':'Country Deactivated.',
                        'data':{}
                    }
                    return Response(response_,status=200)
                else:
                    storage_obj.isActive = True
                    storage_obj.save()
                    response_={
                        'status':'success',
                        'msg':'Country Activated .',
                        'data':{}
                    }
                    return Response(response_,status=200)
            else:
                response_={
                        'status':'failed',
                        'msg':'Country id not found.',
                        'data':{}
                    }
                return Response(response_,status=200)
        else:
            response_={
                    'status':'failed',
                    'msg':'Country id is required.',
                    'data':{}
                }
            return Response(response_,status=200)
  


class GetStateCountry(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        sl_id = request_data.get('id')
        if sl_id is not None and sl_id !="":
            storage_obj=Country.objects.filter(id=sl_id).first()
            if storage_obj is not None :
                stateobj = State.objects.filter(country=sl_id).order_by('name')
                stateser = StateSerializer(stateobj,many=True)
                
                response_={
                    "n": 1,
                    'msg':'state list found successfully.',
                    'data':stateser.data
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
                    'msg':'country id not found.',
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
                    'n':0,
                    'msg':'Country id is required.',
                    'data':{}
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
  



class ChangeCountryStatus(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        sl_id = request.POST.get('id')
        if sl_id is not None and sl_id !="":
            storage_obj=Country.objects.filter(id=sl_id).first()

            if storage_obj is not None :
                if storage_obj.is_black_list == True:
                    storage_obj.is_black_list = False
                    storage_obj.save()
                    response_={
                        'status':'success',
                        'msg':'Country White Listed.',
                        'data':{}
                    }
                    return Response(response_,status=200)
                else:
                    storage_obj.is_black_list = True
                    storage_obj.save()
                    response_={
                        'status':'success',
                        'msg':'Country Black Listed .',
                        'data':{}
                    }
                    return Response(response_,status=200)
            else:
                response_={
                        'status':'failed',
                        'msg':'Country id not found.',
                        'data':{}
                    }
                return Response(response_,status=200)
        else:
            response_={
                    'status':'failed',
                    'msg':'Country id is required.',
                    'data':{}
                }
            return Response(response_,status=200)
  



class AddTicketCategory(GenericAPIView):
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
        data['name'] = request_data.get('name')
        
        if data['name'] is not None and data['name'] !="":
            obj = TicketCategory.objects.filter(isActive=True)
            ser = TicketCategorySerializer(obj,many=True)
            for c in ser.data:
                if (c['name']).lower() == (data['name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Category already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        cser = TicketCategorySerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Category added successfully.',
                'data':cser.data
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
                'msg':'Category not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class TicketCategoryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = TicketCategory.objects.filter(isActive=True)
        ser = TicketCategorySerializer(obj,many=True)
        
        response_={
            "n": 1,
            'msg':'Category found successfully.',
            'data': ser.data
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
            catobj=TicketCategory.objects.filter(id=id,isActive=True).first()
            if catobj is not None:
                serializer = TicketCategorySerializer(catobj)
                response_={
                    "n": 1,
                    'msg':'Category Details Found.',
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
        
        
class UpdateTicketCategory(GenericAPIView):
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
        
            obj = TicketCategory.objects.filter(isActive=True).exclude(id=data['id'])
            ser = TicketCategorySerializer(obj,many=True)
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
            peobj=TicketCategory.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = TicketCategorySerializer(peobj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Category Updated Successfully.',
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
                        'msg':'Category Not Updated.',
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
        

class DeleteTicketCategory(GenericAPIView):
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
            cat_obj=TicketCategory.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Category Deleted Successfully.',
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
                    'msg':'Category id not found.',
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
 
class ChangeTicketCategoryStatus(GenericAPIView):
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
            cat_obj=TicketCategory.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                if cat_obj.status:
                    cat_obj.status = False
                else:
                    cat_obj.status=True
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Category Status changed Successfully.',
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
                    'msg':'Category id not found.',
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
 




class AddFeedbackSubCategory(GenericAPIView):
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
        data['parent_feedback_category'] = request_data.get('parent_feedback_category')
        data['name'] = request_data.get('name')
        
        if data['name'] is not None and data['name'] !="":
            obj = FeedbackSubCategory.objects.filter(isActive=True)
            ser = FeedbackSubCategorySerializer(obj,many=True)
            for c in ser.data:
                if (c['name']).lower() == (data['name']).lower():
                    response_={
                        "n": 0,
                        'msg':"name already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        r_ser = FeedbackSubCategorySerializer(data=data)
        if r_ser.is_valid():
            r_ser.save()
            response_={
                "n": 1,
                'msg':'Feedback Sub Category added successfully.',
                'data':r_ser.data
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
                'msg':'Feedback Sub Category not added.',
                'data':r_ser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class FeedbackSubCategoryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        obj = FeedbackSubCategory.objects.filter(isActive=True)
        ser = FeedbackSubCategorySerializer(obj,many=True)
        for s in ser.data:
            objdep = FeedbackCategory.objects.filter(id=s['parent_feedback_category']).first()
            s['parent_feedback_category_name_str'] = objdep.name
        response_={
            "n": 1,
            'msg':'Feedback Sub Category found successfully.',
            'data': ser.data
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
            r_obj=FeedbackSubCategory.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                serializer = FeedbackSubCategorySerializer(r_obj)
                response_={
                    "n": 1,
                    'msg':'Feedback Sub Category Details Found.',
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

        
class UpdateFeedbackSubCategory(GenericAPIView):
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
            data['parent_feedback_category'] = request_data.get('parent_feedback_category')
            data['name'] = request_data.get('name')
         
            obj = FeedbackSubCategory.objects.filter(isActive=True).exclude(id=data['id'])
            ser = FeedbackSubCategorySerializer(obj,many=True)
            for d in ser.data:
                if str(d['name']).lower() == str(data['name']).lower():
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
            r_obj=FeedbackSubCategory.objects.filter(id=data['id'],isActive=True).first()
            if r_obj is not None:
                serializer = FeedbackSubCategorySerializer(r_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Feedback Sub Category Updated Successfully.',
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
                        'msg':'Feedback Sub Category Not Updated.',
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
        

class DeleteFeedbackSubCategory(GenericAPIView):
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
            r_obj=FeedbackSubCategory.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                r_obj.isActive = False
                r_obj.save()
                response_={
                    "n": 1,
                    'msg':'FeedbackSubCategory Deleted Successfully.',
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
                    'msg':'FeedbackSubCategory id not found.',
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
        
class ChangeFeedbackSubCategoryStatus(GenericAPIView):
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
            r_obj=FeedbackSubCategory.objects.filter(id=id,isActive=True).first()
            if r_obj is not None:
                if r_obj.status:

                    r_obj.status = False
                else:
                    r_obj.status=True
                r_obj.save()
                response_={
                    "n": 1,
                    'msg':'Feedback Sub Category status changed Successfully.',
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
                    'msg':'FeedbackSubCategory id not found.',
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
        
   








# Educational Qualifications
class AddEducationalQualification(GenericAPIView):
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
        data['qualification_name'] = request_data.get('qualification_name')
        
        if data['qualification_name'] is not None and data['qualification_name'] !="":
            obj = EducationalQualifications.objects.filter(isActive=True)
            ser = EducationalQualificationsSerializer(obj,many=True)
            for c in ser.data:
                if (c['qualification_name']).lower() == (data['qualification_name']).lower():
                    response_={
                        "n": 0,
                        'msg':"Qualification already exits",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                
        cser = EducationalQualificationsSerializer(data=data)
        if cser.is_valid():
            cser.save()
            response_={
                "n": 1,
                'msg':'Qualification added successfully.',
                'data':cser.data
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
                'msg':'Qualification not added.',
                'data':cser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class EducationalQualificationList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = EducationalQualifications.objects.filter(isActive=True)
        ser = EducationalQualificationsSerializer(obj,many=True)
        


        response_={
            "n": 1,
            'msg':'Qualifications found successfully.',
            'data': ser.data
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
            catobj=EducationalQualifications.objects.filter(id=id,isActive=True).first()
            if catobj is not None:
                serializer = EducationalQualificationsSerializer(catobj)
                response_={
                    "n": 1,
                    'msg':'Educational Qualifications Details Found.',
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
        
        
class UpdateEducationalQualification(GenericAPIView):
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
            data['qualification_name'] = request_data.get('qualification_name')
        
            obj = EducationalQualifications.objects.filter(isActive=True).exclude(id=data['id'])
            ser = EducationalQualificationsSerializer(obj,many=True)
            for p in ser.data:
                if str(p['qualification_name']).lower() == str(data['qualification_name']).lower():
                    response_={
                        "n": 0,
                        'msg':'Qualification already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            peobj=EducationalQualifications.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = EducationalQualificationsSerializer(peobj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Educational Qualifications Updated Successfully.',
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
                        'msg':'Educational Qualifications Not Updated.',
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
        





class DeleteEducationalQualification(GenericAPIView):
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
            cat_obj=EducationalQualifications.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Educational Qualifications Deleted Successfully.',
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
                    'msg':'Educational Qualifications id not found.',
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


class ChangeEducationalQualificationStatus(GenericAPIView):
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
            cat_obj=EducationalQualifications.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                if cat_obj.status:
                    cat_obj.status = False
                else:
                    cat_obj.status=True

                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Educational Qualifications status changed successfully.',
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
                    'msg':'Educational Qualifications id not found.',
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
 



class AddCollege(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        college_code = request_data.get("college_code")
        college_name = request_data.get("college_name")

        admin_name = request_data.get("admin_name")
        admin_email = request_data.get("admin_email")
        admin_mobile = request_data.get("admin_mobile")
        admin_password = request_data.get(
            "admin_password",
            "Default@123"
)

        if college_code is None or college_code == "":
            return phase_one_response(request, {
                "n": 0,
                "msg": "College code is required.",
                "data": {},
            })

        if college_name is None or college_name == "":
            return phase_one_response(request, {
                "n": 0,
                "msg": "College name is required.",
                "data": {},
            })

        if admin_name is None or admin_name == "":
            return phase_one_response(request, {
                "n": 0,
                "msg": "College admin name is required.",
                "data": {},
            })

        if admin_email is None or admin_email == "":
            return phase_one_response(request, {
                "n": 0,
                "msg": "College admin email is required.",
                "data": {},
            })

        duplicate_college = College.objects.filter(
            isActive=True,
            college_code__iexact=str(college_code).strip(),
).first()

        if duplicate_college is not None:
            return phase_one_response(request, {
                "n": 0,
                "msg": "College code already exists.",
                "data": {},
            })

        duplicate_admin = UserAdmin.objects.filter(
            email__iexact=str(admin_email).strip(),
            isActive=True,
).first()

        if duplicate_admin is not None:
            return phase_one_response(request, {
                "n": 0,
                "msg": "College admin email already exists.",
                "data": {},
            })

        try:
            with transaction.atomic():

                college_data = {
                    "college_code": str(
                        college_code
            ).strip().upper(),

                    "college_name": str(
                        college_name
            ).strip(),

                    "university_name": request_data.get(
                        "university_name"
            ),

                    "affiliation_number": request_data.get(
                        "affiliation_number"
            ),

                    "email": request_data.get("email"),
                    "phone": request_data.get("phone"),
                    "address": request_data.get("address"),

                    "status": request_data.get(
                        "status",
                        True
            ),

                    "createdBy": str(request.user.id),
                }

                college_serializer = CollegeSerializer(
                    data=college_data
        )

                if not college_serializer.is_valid():
                    return phase_one_response(request, {
                        "n": 0,
                        "msg": "College not added.",
                        "data": college_serializer.errors,
                    })

                college = college_serializer.save()

                admin_user = UserAdmin(
                    name=str(admin_name).strip(),
                    email=str(admin_email).strip().lower(),
                    mobilenumber=admin_mobile,

                    college_id=college.id,

                    user_type=1,
                    current_status="ACTIVE",

                    status=True,
                    deactivate=False,

                    source="COLLEGE_ADMIN",
                    og_code=college.college_code,

                    createdBy=str(request.user.id),
        )

                admin_user.set_password(admin_password)
                admin_user.save()

                response_data = {
                    "college": college_serializer.data,

                    "college_admin": {
                        "id": str(admin_user.id),
                        "name": admin_user.name,
                        "email": admin_user.email,
                        "mobilenumber": admin_user.mobilenumber,
                        "college_id": admin_user.college_id,
                    }
                }

                return phase_one_response(request, {
                    "n": 1,
                    "msg": (
                        "College and college admin "
                        "created successfully."
            ),
                    "data": response_data,
                })

        except Exception as error:
            return phase_one_response(request, {
                "n": 0,
                "msg": "College creation failed.",
                "data": {
                    "error": str(error)
                },
            })
class CollegeList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        queryset = College.objects.filter(
            isActive=True
).order_by("college_name")

        serializer = CollegeSerializer(
            queryset,
            many=True,
)

        return phase_one_response(request, {
            "n": 1,
            "msg": "College list fetched successfully.",
            "data": serializer.data,
        })

    def post(self, request):
        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        college_id = request_data.get("id")

        if college_id is None or college_id == "":
            return phase_one_response(request, {
                "n": 0,
                "msg": "College id is required.",
                "data": {},
            })

        college = College.objects.filter(
            id=college_id,
            isActive=True,
).first()

        if college is None:
            return phase_one_response(request, {
                "n": 0,
                "msg": "College not found.",
                "data": {},
            })

        return phase_one_response(request, {
            "n": 1,
            "msg": "College details fetched successfully.",
            "data": CollegeSerializer(college).data,
        })

class UpdateCollege(GenericAPIView):
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
            data['college_name'] = request_data.get('college_name')
            data['college_code'] = request_data.get('college_code')
            data['tags'] = request_data.get('tags')
        
            obj = College.objects.filter(isActive=True).exclude(id=data['id'])
            ser = CollegeSerializer(obj,many=True)
            for p in ser.data:
                if str(p['college_name']).lower() == str(data['college_name']).lower():
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
            peobj=College.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = CollegeSerializer(peobj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'College Updated Successfully.',
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
                        'msg':'College Not Updated.',
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
        

class DeleteCollege(GenericAPIView):
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
            cat_obj=College.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'College Deleted Successfully.',
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
                    'msg':'College id not found.',
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


class ChangeCollegeStatus(GenericAPIView):
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
            cat_obj=College.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                if cat_obj.status:
                    cat_obj.status = False
                else:
                    cat_obj.status=True

                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'College status changed successfully.',
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
                    'msg':'College id not found.',
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
 



class AddAcademicYear(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        name = request_data.get("academic_year_name")
        start_date = request_data.get("start_date")
        end_date = request_data.get("end_date")

        if name is None or name == "":
            return phase_one_response(request, {
                "n": 0,
                "msg": "Academic year name is required.",
                "data": {},
            })

        duplicate = AcademicYear.objects.filter(
            isActive=True,
            academic_year_name__iexact=str(name).strip(),
).first()

        if duplicate is not None:
            return phase_one_response(request, {
                "n": 0,
                "msg": "Academic year already exists.",
                "data": {},
            })

        if start_date and end_date and start_date > end_date:
            return phase_one_response(request, {
                "n": 0,
                "msg": "Start date cannot be after end date.",
                "data": {},
            })

        is_current = request_data.get("is_current", False)

        if is_current:
            AcademicYear.objects.filter(
                isActive=True,
                is_current=True,
    ).update(is_current=False)

        data = {
            "academic_year_name": str(name).strip(),
            "start_date": start_date,
            "end_date": end_date,
            "admission_start_date": request_data.get(
                "admission_start_date"
    ),
            "admission_end_date": request_data.get(
                "admission_end_date"
    ),
            "is_current": is_current,
            "status": request_data.get("status", True),
            "createdBy": str(request.user.id),
        }

        serializer = AcademicYearSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            return phase_one_response(request, {
                "n": 1,
                "msg": "Academic year added successfully.",
                "data": serializer.data,
            })

        return phase_one_response(request, {
            "n": 0,
            "msg": "Academic year not added.",
            "data": serializer.errors,
        })

class SetCurrentAcademicYear(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        academic_year = AcademicYear.objects.filter(
            id=request_data.get("id"),
            isActive=True,
            status=True,
).first()

        if academic_year is None:
            return phase_one_response(request, {
                "n": 0,
                "msg": "Active academic year not found.",
                "data": {},
            })

        AcademicYear.objects.filter(
            isActive=True,
            is_current=True,
).update(is_current=False)

        academic_year.is_current = True
        academic_year.updatedBy = str(request.user.id)
        academic_year.updatedAt = timezone.now()
        academic_year.save()

        return phase_one_response(request, {
            "n": 1,
            "msg": "Current academic year updated successfully.",
            "data": AcademicYearSerializer(
                academic_year
    ).data,
        })

class CurrentAcademicYear(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        academic_year = AcademicYear.objects.filter(
            isActive=True,
            status=True,
            is_current=True,
).first()

        if academic_year is None:
            return phase_one_response(request, {
                "n": 0,
                "msg": "Current academic year is not configured.",
                "data": {},
            })

        return phase_one_response(request, {
            "n": 1,
            "msg": "Current academic year fetched successfully.",
            "data": AcademicYearSerializer(
                academic_year
    ).data,
        })

# ============================================================
# Academic Year List and Details
# ============================================================

class AcademicYearList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        academic_year_obj = AcademicYear.objects.filter(
            isActive=True
).order_by(
            '-is_current',
            '-start_date',
            '-id'
)

        status = request.GET.get('status')
        is_current = request.GET.get('is_current')

        if status is not None and status != "":
            if str(status).lower() in [
                "true",
                "1",
                "active"
            ]:
                academic_year_obj = academic_year_obj.filter(
                    status=True
        )

            elif str(status).lower() in [
                "false",
                "0",
                "inactive"
            ]:
                academic_year_obj = academic_year_obj.filter(
                    status=False
        )

        if is_current is not None and is_current != "":
            if str(is_current).lower() in [
                "true",
                "1"
            ]:
                academic_year_obj = academic_year_obj.filter(
                    is_current=True
        )

            elif str(is_current).lower() in [
                "false",
                "0"
            ]:
                academic_year_obj = academic_year_obj.filter(
                    is_current=False
        )

        serializer = AcademicYearSerializer(
            academic_year_obj,
            many=True
)

        response_ = {
            "n": 1,
            "msg": "Academic year found successfully.",
            "data": serializer.data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )

            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )

            return Response(
                encdata,
                status=200
    )

        return Response(
            response_,
            status=200
)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        academic_year_id = request_data.get('id')

        if (
            academic_year_id is None
            or academic_year_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Academic year id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        academic_year_obj = AcademicYear.objects.filter(
            id=academic_year_id,
            isActive=True
).first()

        if academic_year_obj is None:
            response_ = {
                "n": 0,
                "msg": "Academic year not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        serializer = AcademicYearSerializer(
            academic_year_obj
)

        response_ = {
            "n": 1,
            "msg": (
                "Academic year details "
                "found successfully."
    ),
            "data": serializer.data
        }

        if encryped_header == "1":
            data_to_serialize = (
                convert_decimals_to_float(
                    response_
        )
    )

            encdata = encrypt_data(
                json.dumps(
                    data_to_serialize
        )
    )

            return Response(
                encdata,
                status=200
    )

        return Response(
            response_,
            status=200
)


class AcademicYearListByActive(GenericAPIView):
    """
    Simple academic year list filtered by isActive.

    POST /api/master/academic-year-list

    Request Body (optional):
    {
        "is_active": "active"    # "active" (default) | "inactive" | "all"
    }

    Response:
    {
        "n": 1,
        "msg": "Academic years found successfully.",
        "data": [ ...AcademicYear... ]
    }
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encrypted_header = request.headers.get("encrypted", "")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        is_active = request_data.get('is_active')

        academic_year_obj = AcademicYear.objects.all().order_by(
            '-is_current',
            '-start_date',
            '-id'
        )

        if str(is_active).lower() in ("inactive", "false", "0"):
            academic_year_obj = academic_year_obj.filter(isActive=False)
        elif str(is_active).lower() not in ("all", "none"):
            academic_year_obj = academic_year_obj.filter(isActive=True)

        serializer = AcademicYearSerializer(
            academic_year_obj,
            many=True
        )

        response_ = {
            "n": 1,
            "msg": "Academic years found successfully.",
            "data": serializer.data
        }

        if encrypted_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)

        return Response(response_, status=200)


# ============================================================
# Update Academic Year
# ============================================================

class UpdateAcademicYear(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        academic_year_id = request_data.get('id')

        if (
            academic_year_id is None
            or academic_year_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Academic year id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        academic_year_obj = AcademicYear.objects.filter(
            id=academic_year_id,
            isActive=True
).first()

        if academic_year_obj is None:
            response_ = {
                "n": 0,
                "msg": "Academic year not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        data = {}

        data['academic_year_name'] = request_data.get(
            'academic_year_name',
            academic_year_obj.academic_year_name
)

        data['start_date'] = request_data.get(
            'start_date',
            academic_year_obj.start_date
)

        data['end_date'] = request_data.get(
            'end_date',
            academic_year_obj.end_date
)

        data['admission_start_date'] = request_data.get(
            'admission_start_date',
            academic_year_obj.admission_start_date
)

        data['admission_end_date'] = request_data.get(
            'admission_end_date',
            academic_year_obj.admission_end_date
)

        data['is_current'] = request_data.get(
            'is_current',
            academic_year_obj.is_current
)

        data['status'] = request_data.get(
            'status',
            academic_year_obj.status
)

        data['updatedBy'] = str(
            request.user.id
)

        data['updatedAt'] = timezone.now()

        if (
            data['academic_year_name'] is None
            or data['academic_year_name'] == ""
):
            response_ = {
                "n": 0,
                "msg": (
                    "Academic year name is "
                    "required."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        data['academic_year_name'] = str(
            data['academic_year_name']
).strip()

        duplicate_obj = AcademicYear.objects.filter(
            academic_year_name__iexact=(
                data['academic_year_name']
    ),
            isActive=True
).exclude(
            id=academic_year_id
).first()

        if duplicate_obj is not None:
            response_ = {
                "n": 0,
                "msg": (
                    "Academic year already "
                    "exists."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        if (
            data['start_date']
            and data['end_date']
            and str(data['start_date'])
            > str(data['end_date'])
):
            response_ = {
                "n": 0,
                "msg": (
                    "Start date cannot be "
                    "after end date."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        if (
            data['admission_start_date']
            and data['admission_end_date']
            and str(data['admission_start_date'])
            > str(data['admission_end_date'])
):
            response_ = {
                "n": 0,
                "msg": (
                    "Admission start date cannot "
                    "be after admission end date."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        if data['is_current']:
            AcademicYear.objects.filter(
                isActive=True,
                is_current=True
    ).exclude(
                id=academic_year_id
    ).update(
                is_current=False
    )

        serializer = AcademicYearSerializer(
            academic_year_obj,
            data=data,
            partial=True
)

        if serializer.is_valid():
            serializer.save()

            response_ = {
                "n": 1,
                "msg": (
                    "Academic year updated "
                    "successfully."
        ),
                "data": serializer.data
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        response_ = {
            "n": 0,
            "msg": "Academic year not updated.",
            "data": serializer.errors
        }

        if encryped_header == "1":
            data_to_serialize = (
                convert_decimals_to_float(
                    response_
        )
    )

            encdata = encrypt_data(
                json.dumps(
                    data_to_serialize
        )
    )

            return Response(
                encdata,
                status=200
    )

        return Response(
            response_,
            status=200
)


# ============================================================
# Delete Academic Year
# ============================================================

class DeleteAcademicYear(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        academic_year_id = request_data.get('id')

        if (
            academic_year_id is None
            or academic_year_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Academic year id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        academic_year_obj = AcademicYear.objects.filter(
            id=academic_year_id,
            isActive=True
).first()

        if academic_year_obj is None:
            response_ = {
                "n": 0,
                "msg": "Academic year not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        if academic_year_obj.is_current:
            response_ = {
                "n": 0,
                "msg": (
                    "Current academic year "
                    "cannot be deleted."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        class_group_exists = ClassGroup.objects.filter(
            academic_year_id=academic_year_obj.id,
            isActive=True
).exists()

        if class_group_exists:
            response_ = {
                "n": 0,
                "msg": (
                    "Academic year cannot be "
                    "deleted because class groups "
                    "exist."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        academic_year_obj.isActive = False
        academic_year_obj.updatedBy = str(
            request.user.id
)
        academic_year_obj.updatedAt = timezone.now()
        academic_year_obj.save()

        response_ = {
            "n": 1,
            "msg": (
                "Academic year deleted "
                "successfully."
    ),
            "data": {}
        }

        if encryped_header == "1":
            data_to_serialize = (
                convert_decimals_to_float(
                    response_
        )
    )

            encdata = encrypt_data(
                json.dumps(
                    data_to_serialize
        )
    )

            return Response(
                encdata,
                status=200
    )

        return Response(
            response_,
            status=200
)


# ============================================================
# Change Academic Year Status
# ============================================================

class ChangeAcademicYearStatus(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        academic_year_id = request_data.get('id')

        if (
            academic_year_id is None
            or academic_year_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Academic year id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        academic_year_obj = AcademicYear.objects.filter(
            id=academic_year_id,
            isActive=True
).first()

        if academic_year_obj is None:
            response_ = {
                "n": 0,
                "msg": "Academic year not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        if (
            academic_year_obj.is_current
            and academic_year_obj.status
):
            response_ = {
                "n": 0,
                "msg": (
                    "Current academic year "
                    "cannot be deactivated."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = (
                    convert_decimals_to_float(
                        response_
            )
        )

                encdata = encrypt_data(
                    json.dumps(
                        data_to_serialize
            )
        )

                return Response(
                    encdata,
                    status=200
        )

            return Response(
                response_,
                status=200
    )

        academic_year_obj.status = (
            not academic_year_obj.status
)

        academic_year_obj.updatedBy = str(
            request.user.id
)

        academic_year_obj.updatedAt = (
            timezone.now()
)

        academic_year_obj.save()

        response_ = {
            "n": 1,
            "msg": (
                "Academic year status changed "
                "successfully."
    ),
            "data": {
                "id": academic_year_obj.id,
                "status": academic_year_obj.status,
                "is_current": (
                    academic_year_obj.is_current
        )
            }
        }

        if encryped_header == "1":
            data_to_serialize = (
                convert_decimals_to_float(
                    response_
        )
    )

            encdata = encrypt_data(
                json.dumps(
                    data_to_serialize
        )
    )

            return Response(
                encdata,
                status=200
    )

        return Response(
            response_,
            status=200
)

    



# ============================================================
# Semester Master APIs
# URL spelling retained as "semester" for existing frontend use.
# Model name remains Semester.
# ============================================================


class AddSemester(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        data = {}

        data['semester_number'] = request_data.get('semester_number')
        data['semester_name'] = request_data.get('semester_name')
        data['status'] = request_data.get('status', True)
        data['createdBy'] = str(request.user.id)

        

        # Semester number validation
        if (
            data['semester_number'] is None
            or data['semester_number'] == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester number is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        try:
            data['semester_number'] = int(
                data['semester_number']
    )

            if data['semester_number'] <= 0:
                raise ValueError

        except (TypeError, ValueError):
            response_ = {
                "n": 0,
                "msg": "Semester number must be a positive number.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)


        # Semester name validation
        if (
            data['semester_name'] is None
            or data['semester_name'] == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester name is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        data['semester_name'] = str(
            data['semester_name']
).strip()

        duplicate_number = Semester.objects.filter(
            semester_number=data['semester_number'],
            isActive=True
).first()

        if duplicate_number is not None:
            response_ = {
                "n": 0,
                "msg": (
                    "Semester number already exists "
                    "for this course."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        # Duplicate semester name for same course
        duplicate_name = Semester.objects.filter(
            semester_name__iexact=data['semester_name'],
            isActive=True
).first()

        if duplicate_name is not None:
            response_ = {
                "n": 0,
                "msg": (
                    "Semester name already exists "
                    "for this course."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        serializer = SemesterSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            response_ = {
                "n": 1,
                "msg": "Semester added successfully.",
                "data": serializer.data
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        response_ = {
            "n": 0,
            "msg": "Semester not added.",
            "data": serializer.errors
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class SemesterList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        semester_obj = Semester.objects.filter(
            isActive=True
).order_by(
            'semester_number'
)

        status = request.GET.get('status')

       
        if status is not None and status != "":
            if str(status).lower() in [
                "true",
                "1",
                "active"
            ]:
                semester_obj = semester_obj.filter(
                    status=True
        )

            elif str(status).lower() in [
                "false",
                "0",
                "inactive"
            ]:
                semester_obj = semester_obj.filter(
                    status=False
        )

        serializer = SemesterSerializer(
            semester_obj,
            many=True
)

        semester_data = serializer.data


        response_ = {
            "n": 1,
            "msg": "Semester found successfully.",
            "data": semester_data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        semester_id = request_data.get('id')

        if (
            semester_id is None
            or semester_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        semester_obj = Semester.objects.filter(
            id=semester_id,
            isActive=True
).first()

        if semester_obj is None:
            response_ = {
                "n": 0,
                "msg": "Semester not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        serializer = SemesterSerializer(
            semester_obj
)

        semester_data = serializer.data

        

        response_ = {
            "n": 1,
            "msg": "Semester details found successfully.",
            "data": semester_data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class SemesterDetails(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        semester_id = request_data.get('id')

        if (
            semester_id is None
            or semester_id == ""
):
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Semester id is required.",
                    "data": {}
                }
    )

        semester_obj = Semester.objects.filter(
            id=semester_id
).first()

        if semester_obj is None:
            return phase_one_response(
                request,
                {
                    "n": 0,
                    "msg": "Semester not found.",
                    "data": {}
                }
    )

        semester_data = {
            "id": semester_obj.id,
            "course_id": semester_obj.course_id,
            "semester_name": semester_obj.semester_name,
            "semester_number": semester_obj.semester_number,
        }

        return phase_one_response(
            request,
            {
                "n": 1,
                "msg": "Semester details found successfully.",
                "data": semester_data
            }
)


class UpdateSemester(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        semester_id = request_data.get('id')

        if (
            semester_id is None
            or semester_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        semester_obj = Semester.objects.filter(
            id=semester_id,
            isActive=True
).first()

        if semester_obj is None:
            response_ = {
                "n": 0,
                "msg": "Semester not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        data = {}

        data['course_id'] = request_data.get(
            'course_id',
            semester_obj.course_id
)
        data['semester_number'] = request_data.get(
            'semester_number',
            semester_obj.semester_number
)
        data['semester_name'] = request_data.get(
            'semester_name',
            semester_obj.semester_name
)
        data['status'] = request_data.get(
            'status',
            semester_obj.status
)
        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()

        course_obj = Course.objects.filter(
            id=data['course_id'],
            isActive=True,
            status=True
).first()

        if course_obj is None:
            response_ = {
                "n": 0,
                "msg": "Active course not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        if (
            data['semester_number'] is None
            or data['semester_number'] == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester number is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        try:
            data['semester_number'] = int(
                data['semester_number']
    )

            if data['semester_number'] <= 0:
                raise ValueError

        except (TypeError, ValueError):
            response_ = {
                "n": 0,
                "msg": "Semester number must be a positive number.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        if data['semester_number'] > course_obj.total_semesters:
            response_ = {
                "n": 0,
                "msg": (
                    "Semester number cannot be greater than "
                    f"{course_obj.total_semesters} for this course."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        if (
            data['semester_name'] is None
            or data['semester_name'] == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester name is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        data['semester_name'] = str(
            data['semester_name']
).strip()

        duplicate_number = Semester.objects.filter(
            semester_number=data['semester_number'],
            isActive=True
).exclude(
            id=semester_id
).first()

        if duplicate_number is not None:
            response_ = {
                "n": 0,
                "msg": (
                    "Semester number already exists "
                    "for this course."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        duplicate_name = Semester.objects.filter(
            semester_name__iexact=data['semester_name'],
            isActive=True
).exclude(
            id=semester_id
).first()

        if duplicate_name is not None:
            response_ = {
                "n": 0,
                "msg": (
                    "Semester name already exists "
                    "for this course."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        serializer = SemesterSerializer(
            semester_obj,
            data=data,
            partial=True
)

        if serializer.is_valid():
            serializer.save()

            response_ = {
                "n": 1,
                "msg": "Semester updated successfully.",
                "data": serializer.data
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        response_ = {
            "n": 0,
            "msg": "Semester not updated.",
            "data": serializer.errors
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class DeleteSemester(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        semester_id = request_data.get('id')

        if (
            semester_id is None
            or semester_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        semester_obj = Semester.objects.filter(
            id=semester_id,
            isActive=True
).first()

        if semester_obj is None:
            response_ = {
                "n": 0,
                "msg": "Semester id not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        class_group_exists = ClassGroup.objects.filter(
            semester_id=semester_obj.id,
            isActive=True
).exists()

        if class_group_exists:
            response_ = {
                "n": 0,
                "msg": (
                    "Semester cannot be deleted because "
                    "class groups exist."
        ),
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        semester_obj.isActive = False
        semester_obj.updatedBy = str(request.user.id)
        semester_obj.updatedAt = timezone.now()
        semester_obj.save()

        response_ = {
            "n": 1,
            "msg": "Semester deleted successfully.",
            "data": {}
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class ChangeSemesterStatus(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        semester_id = request_data.get('id')

        if (
            semester_id is None
            or semester_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Semester id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        semester_obj = Semester.objects.filter(
            id=semester_id,
            isActive=True
).first()

        if semester_obj is None:
            response_ = {
                "n": 0,
                "msg": "Semester id not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
                    response_
        )
                encdata = encrypt_data(
                    json.dumps(data_to_serialize)
        )
                return Response(encdata, status=200)

            return Response(response_, status=200)

        semester_obj.status = not semester_obj.status
        semester_obj.updatedBy = str(request.user.id)
        semester_obj.updatedAt = timezone.now()
        semester_obj.save()

        response_ = {
            "n": 1,
            "msg": "Semester status changed successfully.",
            "data": {
                "id": semester_obj.id,
                "status": semester_obj.status
            }
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)





# ============================================================
# Class Group Master APIs
# ============================================================


class AddClassGroup(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}
        data['course_id'] = request_data.get('course_id')
        data['semester_ids'] = request_data.get('semester_ids')
        data['class_name'] = request_data.get('class_name')
        data['division'] = request_data.get('division')
        data['batch_name'] = request_data.get('batch_name')
        data['capacity'] = request_data.get('capacity',0)
        data['status'] = request_data.get('status',True)
        data['createdBy'] = str(request.user.id)



        # course validation
        if (data['course_id'] is None or data['course_id'] == ""):
            response_ = {
                "n": 0,
                "msg": "course id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)

            return Response(response_, status=200)

        course_obj = Course.objects.filter(id=data['course_id'],isActive=True,og_code=str(request.user.og_code)).first()

        if course_obj is None:
            response_ = {
                "n": 0,
                "msg": "Active course not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)

            return Response(response_, status=200)



        # Class name validation
        if (data['class_name'] is None  or data['class_name'] == ""):
            response_ = {
                "n": 0,
                "msg": "Class name is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        data['class_name'] = str(data['class_name']).strip()
        if (data['division'] is not None and data['division'] != ""):
            data['division'] = str(data['division']).strip().upper()
        else:
            data['division'] = None

        if (data['batch_name'] is not None   and data['batch_name'] != ""):
            data['batch_name'] = str(data['batch_name']).strip()
        else:
            data['batch_name'] = None
        data['og_code'] = str(request.user.og_code)

        # Capacity validation
        try:
            data['capacity'] = int(data['capacity'])
            if data['capacity'] < 0:
                raise ValueError
        except (TypeError, ValueError):
            response_ = {
                "n": 0,
                "msg": "Capacity must be zero or a positive number.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        duplicate_query = ClassGroup.objects.filter(
            course_id=data['course_id'],
            class_name=data['class_name'],
            og_code=str(request.user.og_code),
            isActive=True
        )


        duplicate_obj = duplicate_query.first()
        if duplicate_obj is not None:
            response_ = {
                "n": 0,
                "msg": "Class group already exists.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)
        serializer = ClassGroupSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            response_ = {
                "n": 1,
                "msg": "Class group added successfully.",
                "data": serializer.data
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        response_ = {
            "n": 0,
            "msg": "Class group not added.",
            "data": serializer.errors
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


class ClassGroupList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        class_group_obj = ClassGroup.objects.filter(isActive=True,og_code=str(request.user.og_code))
        course_id = request.GET.get('course_id')
        status = request.GET.get('status')


        if (course_id is not None and course_id != ""):
            class_group_obj = class_group_obj.filter(course_id=course_id)



        if status is not None and status != "":
            if str(status).lower() in ["true""1""active"]:
                class_group_obj = class_group_obj.filter(status=True)
            elif str(status).lower() in ["false""0""inactive"]:
                class_group_obj = class_group_obj.filter(status=False)

        serializer = ClassGroupSerializer(class_group_obj,many=True)

        class_group_data = serializer.data

        for item in class_group_data:

            course_obj = Course.objects.filter(id=item['course_id'],isActive=True).first()

            if course_obj is not None:
                item['course_name'] = (course_obj.course_name)                
                item['course_code'] = (course_obj.course_code)
            else:
                item['course_name'] = ""
                item['course_code'] = ""


        response_ = {
            "n": 1,
            "msg": "Class group found successfully.",
            "data": class_group_data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)

        return Response(response_, status=200)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        class_group_id = request_data.get('id')
        if (class_group_id is None or class_group_id == ""):
            response_ = {
                "n": 0,
                "msg": "Class group id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)

            return Response(response_, status=200)

        class_group_obj = ClassGroup.objects.filter(id=class_group_id,isActive=True).first()
        if class_group_obj is None:
            response_ = {
                "n": 0,
                "msg": "Class group not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)
        serializer = ClassGroupSerializer(class_group_obj)
        class_group_data = serializer.data
        response_ = {
            "n": 1,
            "msg": "Class group details found successfully.",
            "data": class_group_data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)

        return Response(response_, status=200)


class UpdateClassGroup(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        class_group_id = request_data.get('id')
        if (class_group_id is None or class_group_id == ""):
            response_ = {
                "n": 0,
                "msg": "Class group id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        class_group_obj = ClassGroup.objects.filter(id=class_group_id,isActive=True).first()
        if class_group_obj is None:
            response_ = {
                "n": 0,
                "msg": "Class group not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)
        data = {}
        data['semester_ids'] = request_data.get('semester_ids',class_group_obj.semester_ids)
        data['course_id'] = request_data.get('course_id',class_group_obj.course_id)
        data['class_name'] = request_data.get('class_name',class_group_obj.class_name)
        data['division'] = request_data.get('division',class_group_obj.division)
        data['capacity'] = request_data.get('capacity',class_group_obj.capacity)
        data['status'] = request_data.get('status',class_group_obj.status)
        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()


        if (data['class_name'] is None  or data['class_name'] == ""):
            response_ = {
                "n": 0,
                "msg": "Class name is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        data['class_name'] = str(data['class_name']).strip()

        if (data['division'] is not None and data['division'] != ""):
            data['division'] = str(data['division']).strip().upper()
        else:
            data['division'] = None



        try:
            data['capacity'] = int(data['capacity'])
            if data['capacity'] < 0:
                raise ValueError

        except (TypeError, ValueError):
            response_ = {
                "n": 0,
                "msg": "Capacity must be zero or a positive number.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        duplicate_query = ClassGroup.objects.filter(
            course_id=data['course_id'],
            class_name__iexact=data['class_name'],
            og_code=str(request.user.og_code),
            isActive=True).exclude(id=class_group_id)

        if data['division'] is None:
            duplicate_query = duplicate_query.filter(division__isnull=True)
        else:
            duplicate_query = duplicate_query.filter(division__iexact=data['division'])

        if duplicate_query.exists():
            response_ = {
                "n": 0,
                "msg": "Class group already exists.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        serializer = ClassGroupSerializer(class_group_obj,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()

            response_ = {
                "n": 1,
                "msg": "Class group updated successfully.",
                "data": serializer.data
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)

            return Response(response_, status=200)

        response_ = {
            "n": 0,
            "msg": "Class group not updated.",
            "data": serializer.errors
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(                response_    )
            encdata = encrypt_data(                json.dumps(data_to_serialize)    )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class DeleteClassGroup(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        class_group_id = request_data.get('id')

        if (            class_group_id is None            or class_group_id == ""):
            response_ = {                "n": 0,
                "msg": "Class group id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)

            return Response(response_, status=200)

        class_group_obj = ClassGroup.objects.filter(            id=class_group_id,            isActive=True).first()

        if class_group_obj is None:
            response_ = {
                "n": 0,
                "msg": "Class group id not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        class_group_obj.isActive = False
        class_group_obj.updatedBy = str(request.user.id)
        class_group_obj.updatedAt = timezone.now()
        class_group_obj.save()

        response_ = {
            "n": 1,
            "msg": "Class group deleted successfully.",
            "data": {}
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(                response_    )
            encdata = encrypt_data(                json.dumps(data_to_serialize)    )
            return Response(encdata, status=200)
        return Response(response_, status=200)


class ChangeClassGroupStatus(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(
            request
)

        if error_response:
            return error_response

        class_group_id = request_data.get('id')

        if (
            class_group_id is None
            or class_group_id == ""
):
            response_ = {
                "n": 0,
                "msg": "Class group id is required.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
response_
)
                encdata = encrypt_data(
json.dumps(data_to_serialize)
)
                return Response(encdata, status=200)

            return Response(response_, status=200)

        class_group_obj = ClassGroup.objects.filter(
            id=class_group_id,
            isActive=True
).first()

        if class_group_obj is None:
            response_ = {
                "n": 0,
                "msg": "Class group id not found.",
                "data": {}
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(
response_
)
                encdata = encrypt_data(
json.dumps(data_to_serialize)
)
                return Response(encdata, status=200)

            return Response(response_, status=200)

        class_group_obj.status = not class_group_obj.status
        class_group_obj.updatedBy = str(request.user.id)
        class_group_obj.updatedAt = timezone.now()
        class_group_obj.save()

        response_ = {
            "n": 1,
            "msg": "Class group status changed successfully.",
            "data": {
                "id": class_group_obj.id,
                "status": class_group_obj.status
            }
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
    )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
    )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class ClassGroupDetails(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)

        if error_response:
            return error_response

        class_group_id = request_data.get('id')

        if (class_group_id is None  or class_group_id == ""):
            return phase_one_response(                
                request,                
                {
                    "n": 0,
                    "msg": "Class group id is required.",
                    "data": {}
                }
            )

        class_group_obj = ClassGroup.objects.filter(id=class_group_id,isActive=True).first()
        if class_group_obj is None:
            return phase_one_response(
                request,{
                    "n": 0,
                    "msg": "Class group not found.",
                    "data": {}
                }
            )

        serializer = ClassGroupSerializer(class_group_obj)
        class_group_data = serializer.data

        return phase_one_response(
            request,
            {
                "n": 1,
                "msg": "Class group details found successfully.",
                "data": class_group_data
            }
)












