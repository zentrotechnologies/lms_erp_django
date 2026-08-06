from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import *
from feedback.serializers import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.jwt import UserAdminJWTAuthentication
from adminauth.models import *
# Create your views here.
from adminauth.views import save_file
from feedback.validation import *


# CATEGORY
class AddFeedbackCategory(GenericAPIView):
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
            obj = FeedbackCategory.objects.filter(isActive=True)
            ser = FeedbackCategorySerializer(obj,many=True)
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
                
        fser = FeedbackCategorySerializer(data=data)
        if fser.is_valid():
            fser.save()
            response_={
                "n": 1,
                'msg':'Category added successfully.',
                'data':fser.data
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
                'data':fser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class FeedbackCategoryList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = FeedbackCategory.objects.filter(isActive=True)
        ser = FeedbackCategorySerializer(obj,many=True)
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
            catobj=FeedbackCategory.objects.filter(id=id,isActive=True).first()
            if catobj is not None:
                serializer = FeedbackCategorySerializer(catobj)
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
        
        
class UpdateFeedbackCategory(GenericAPIView):
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
        
            obj = FeedbackCategory.objects.filter(isActive=True).exclude(id=data['id'])
            ser = FeedbackCategorySerializer(obj,many=True)
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
            peobj=FeedbackCategory.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = FeedbackCategorySerializer(peobj,data=data)
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
        

class FeedbackDeleteCategory(GenericAPIView):
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
            cat_obj=FeedbackCategory.objects.filter(id=id,isActive=True).first()
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
 

class ChangeFeedbackCategoryStatus(GenericAPIView):
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
            cat_obj=FeedbackCategory.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                if cat_obj.status:
                    cat_obj.status = False
                else:
                    cat_obj.status=True
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Category status changed Successfully.',
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
 

# FeedbackForm
class AddFeedbackForm(GenericAPIView):
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
        data['add_note'] = request_data.get('add_note')
        data['category_name'] = request_data.get('category_name')
        data['rating_type'] = request_data.get('rating_type')
        
        if data['name'] is not None and data['name'] !="":
            obj = FeedbackForm.objects.filter(isActive=True)
            ser = FeedbackFormSerializer(obj,many=True)
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
                
        f_Ser = FeedbackFormSerializer(data=data)
        if f_Ser.is_valid():
            f_Ser.save()
            for s in range(1,int(request_data.get("questioncount"))):
                question = request_data.get('question' + str(s))
                file_url = ''
                upload_img = request.FILES.get('upload_img' + str(s))
                if upload_img is not None:
                    folder_path = os.path.join(settings.MEDIA_ROOT,'media','Feedback Images')
                    file_url=save_file(folder_path,upload_img,request)
                    
                obj = FeedbackQuestion.objects.create(feedback_form_id=f_Ser.data['id'],question=question,upload_img = file_url)
            
            response_={
                "n": 1,
                'msg':'Form added successfully.',
                'data':f_Ser.data
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
                'msg':'Form not added.',
                'data':f_Ser.errors
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
class FeedbackFormList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        obj = FeedbackForm.objects.filter(isActive=True)
        ser = FeedbackFormSerializer(obj,many=True)
        
        for fb in ser.data:
            createdTime = fb['createdAt'].split('T')[1].split('.')[0]
            fb['createdAt'] = fb['createdAt'].split('T')[0]
            fb['createdAt'] = datefilterchangeformat(fb['createdAt'])
            fb['createdTime'] = timefilterchangeformat(createdTime)
            # iso_timestamp = fb['createdAt']
            # formatted_time = format_timestamp(iso_timestamp)
        response_={
            "n": 1,
            'msg':'Form found successfully.',
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
            f_object=FeedbackForm.objects.filter(id=id,isActive=True).first()
            if f_object is not None:
                serializer = FeedbackFormSerializer(f_object)
                response_={
                    "n": 1,
                    'msg':'Form Details Found.',
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
        
        
class UpdateFeedbackForm(GenericAPIView):
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
            data['add_note'] = request_data.get('add_note')
            data['category_name'] = request_data.get('category_name')
            data['rating_type'] = request_data.get('rating_type')
            data['question'] = request_data.get('question')
            data['upload_img'] = request_data.get('upload_img')
            data['email'] = request_data.get('email')
            
            obj = FeedbackForm.objects.filter(isActive=True).exclude(id=data['id'])
            ser = FeedbackFormSerializer(obj,many=True)
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
            f_obj=FeedbackForm.objects.filter(id=data['id'],isActive=True).first()
            if f_obj is not None:
                serializer = FeedbackFormSerializer(f_obj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Form Updated Successfully.',
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
                        'msg':'Form Not Updated.',
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
        

class FeedbackDeleteForm(GenericAPIView):
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
            f_obj=FeedbackForm.objects.filter(id=id,isActive=True).first()
            if f_obj is not None:
                f_obj.isActive = False
                f_obj.save()
                response_={
                    "n": 1,
                    'msg':'Form Deleted Successfully.',
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
                    'msg':'Form id not found.',
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
            
            
class FeedbackActivation(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
            
            

# @api_view(['POST'])
# def feedback_training_batch_dependent(request):
#     fid= request.POST.get('fid')
#     if fid is not None and fid !="":
#         obj = .objects.filter(id=fid,isActive=True)
#         ser = Serializer(siteobj,many=True)
#         if ser.data !=[]:
            
#             response_={
#                 'status':'success',
#                 'msg':'Site details found',
#                 'data':ser.data
#             }
#             return Response(response_,status=200)
#         else:
#             response_={
#                 'status':'failed',
#                 'msg':'Details not found',
#                 'data':{}
#             }
#             return Response(response_,status=400)
#     else:
#         response_={
#             'status':'failed',
#             'msg':'Client id not found',
#             'data':{}
#         }
#         return Response(response_,status=200)
   

            
            
        
 
