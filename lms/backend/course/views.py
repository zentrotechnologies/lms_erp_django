from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from adminauth.models import *
from adminauth.serializers import *
from master.models import *
from candidate.models import *
from candidate.serializers import *
from enrollments.models import *
from enrollments.serializers import *
from .serializers import *
from master.serializers import *
from lms.settings import *
from django.contrib.auth.hashers import make_password,check_password
from adminauth.jwt import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.views import save_file,sanitize_filename
from adminauth.common import convertcreationdate
from candidate.jwt import CandidateJWTAuthentication
from schedule.models  import *
from schedule.serializers import *
# Create your views here.
from datetime import date



class AddCourse(GenericAPIView):
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
        data['course_name'] = request_data.get('coursename')
        data['course_code'] = request_data.get('coursecode')
        data['training_mode'] = request_data.get('training_mode')
        data['duration'] = request_data.get('duration')
        data['expiry'] = request_data.get('expiry') or None
        if request_data.get('followed_by') != "":
            data['followed_by'] = request_data.get('followed_by')
        else:
            data['followed_by'] = None
        data['topics_covered'] = request_data.get('topics_covered')
        data['pricing'] = request_data.get('pricing')
        data['description'] = request_data.get('description')
        data['languages'] = request_data.get('languages')

        if 'module_list' in request_data.keys():
            moduleslist = request_data.get('module_list')
        else:
            moduleslist = []
       
        data['og_code'] = str(request.user.og_code)
        data['createdBy'] = str(request.user.id)
        data['info_status'] = 1
       
        coursecode_object = Course.objects.filter(isActive=True,course_code=data['course_code']).first()
        if coursecode_object is not None:
            response_={
                        "n": 0,                    
                        "msg": 'Course Code already exists',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        serializer = CourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            courseid = serializer.data['id']
            infoid = serializer.data['info_status']

            

            if moduleslist != []:
                for m in moduleslist:
                    if m['module_name'] != '':
                        moduleexist = CourseModules.objects.filter(course_id=courseid,module_name=m['module_name'],isActive=True).first()
                        if moduleexist is None:
                            CourseModules.objects.create(course_id=courseid,module_name=m['module_name'],module_description=m['module_description'],module_hours=m['module_hours'])
            
            response_={
                        "n": 1,
                        "msg": 'Course added successfully',
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
                        "msg": 'Course not added',
                        "data":serializer.errors                    
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

class CourseList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        
        member_type = adminobj.user_type
        if adminobj.member_of is None :
            member_of = str(adminobj.id)
        else:
            member_of = str(adminobj.member_of)


        
        course_status = request_data.get('course_status')
        if course_status is not None and course_status != '':
            courselistobj = Course.objects.filter(course_status=course_status,isActive=True,).order_by('-createdAt')
        else:
            courselistobj = Course.objects.filter(isActive=True).order_by('-createdAt')



        serializer =  CourseSerializer(courselistobj,many=True)
        response_={
            "n": 1,
            "msg": 'Course list found successfully',
            "data":serializer.data                        
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

      

class CourseModulesList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
     
        
        Modulesobj = CourseModules.objects.filter(isActive=True).order_by('-createdAt')
        serializer =  CourseModuleSerializer(Modulesobj,many=True)
        response_={
            "n": 1,
            "msg": 'Course Modules list found successfully',
            "data":serializer.data                        
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)


class CourseFilterList(GenericAPIView):
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
        
        course_status = request_data.get('course_status')
        if course_status is not None and course_status != '':
            courselistobj = Course.objects.filter(course_status=course_status).order_by('-createdAt')
        else:
            courselistobj = Course.objects.all().order_by('-createdAt')

        if courselistobj.exists():
            
            page4 = self.paginate_queryset(courselistobj)
            serializer =  CourseSerializer(page4,many=True)
            for s in serializer.data:
                cretby = UserAdmin.objects.filter(id=s['createdBy']).first()
                if cretby is not None and cretby != '':
                    if cretby.user_type == 5:
                        addedby = str(cretby.first_name) + " " +str(cretby.last_name)
                    else:
                        addedby = cretby.name
                else:
                    addedby = ''

                s['addedby'] = addedby

                trobj = TrainingMode.objects.filter(id=s['training_mode']).first()
                if trobj is not None and trobj != '':
                    trmode = trobj.training_mode
                else:
                    trmode = ''

                s['training_mode'] = trmode

                if s['isActive'] == True:
                    s['status'] = 'ACTIVE'
                else:
                    s['status'] = 'INACTIVE'

            response_={
                        "n": 1,
                        "msg": 'Course list found  successfully',
                        "data":serializer.data                        
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
                        "msg": 'course not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class TrainingCenterCourseFilterList(GenericAPIView):
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
        course_status = request_data.get('course_status')
        if course_status is not None and course_status != '':
            courselistobj = Course.objects.filter(course_status=course_status).order_by('-createdAt')
        else:
            courselistobj = Course.objects.all().order_by('-createdAt')
        
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        
        member_type = adminobj.user_type
        if adminobj.member_of is None :
            member_of = str(adminobj.id)
        else:
            member_of = str(adminobj.member_of)
            
        training_center_courses_ids=list(TrainingCenterCourses.objects.filter(training_center_id=member_of,isActive=True).values_list('course_id',flat=True))
        courselistobj=courselistobj.filter(id__in=training_center_courses_ids)
        if courselistobj.exists():
            
            page4 = self.paginate_queryset(courselistobj)
            serializer =  CourseSerializer(page4,many=True)
            for s in serializer.data:
                cretby = UserAdmin.objects.filter(id=s['createdBy']).first()
                if cretby is not None and cretby != '':
                    if cretby.user_type == 5:
                        addedby = str(cretby.first_name) + " " +str(cretby.last_name)
                    else:
                        addedby = cretby.name
                else:
                    addedby = ''

                s['addedby'] = addedby

                trobj = TrainingMode.objects.filter(id=s['training_mode']).first()
                if trobj is not None and trobj != '':
                    trmode = trobj.training_mode
                else:
                    trmode = ''

                s['training_mode'] = trmode

                if s['isActive'] == True:
                    s['status'] = 'ACTIVE'
                else:
                    s['status'] = 'INACTIVE'

            response_={
                        "n": 1,
                        "msg": 'Course list found  successfully',
                        "data":serializer.data                        
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
                        "msg": 'course not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class DeactivateCourse(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
       
        course_id=request_data.get('courseid')
        if course_id is not None or course_id !='':
            course_idobj = Course.objects.filter(id=course_id).first()
            if course_idobj is not None:
                if course_idobj.isActive is True:
                    course_idobj.isActive = False
                    course_idobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Course deactivated successfully',
                            "data":''                     
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
                        "msg": 'Course already deactivated',
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
                        "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class activateCourse(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
       
        course_id=request_data.get('courseid')
        if course_id is not None or course_id !='':
            course_idobj = Course.objects.filter(id=course_id).first()
            if course_idobj is not None:
                if course_idobj.isActive is False:
                    course_idobj.isActive = True
                    course_idobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Course activated successfully',
                            "data":''                     
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
                        "msg": 'Course is already active',
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
                        "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class ApproveCourse(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
       
        course_id=request_data.get('courseid')
        if course_id is not None or course_id !='':
            course_idobj = Course.objects.filter(id=course_id,isActive=True).first()
            if course_idobj is not None:
                courseeligiobj = CourseEligibility.objects.filter(course_id=course_id,isActive=True).first()
                if courseeligiobj is not None:
                    

                    course_idobj.course_status = 'Approved'
                    course_idobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Course Approved successfully',
                            "data":''                     
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
                            "msg": 'Please add course eligibility before approving',
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
                        "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class DeclineCourse(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
       
        course_id=request_data.get('courseid')
        if course_id is not None or course_id !='':
            course_idobj = Course.objects.filter(id=course_id).first()
            if course_idobj is not None:
                if course_idobj.isActive is True:
                    course_idobj.course_status = 'Declined'
                    course_idobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Course Declined successfully',
                            "data":''                     
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
                        "msg": 'Course is deactivated',
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
                        "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class AddCourseMaterial(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        courseid = request.POST.get('courseid')
        moduleid = request.POST.get('moduleid')
        language =  request.POST.get('languageid')
        filetype = request.POST.get('filetype')
        filematerialname =request.POST.get('filematerialname')
        fileInput = request.FILES.get('fileInput')
        linkInput = request.POST.get('linkInput')
        userid = str(request.user.id)
        if courseid is not None and courseid != '':
            courseobj = Course.objects.filter(id=courseid,isActive=True).first()
            if courseobj is not None:
                coursename = courseobj.course_name
                mobj = CourseMaterial.objects.filter(material_label=filematerialname,course_id=courseid,language=language).first()
                if mobj is None:
                    course_folder_name = sanitize_filename(coursename)
                    folder_path = os.path.join(settings.MEDIA_ROOT,'media','Study Material',course_folder_name)
                    if moduleid not in [None, '', 'null']:
                        try:
                            module_id = moduleid
                        except ValueError:
                            module_id = None
                    else:
                        module_id = None

                    if filetype != 'link':
                        file_url=save_file(folder_path,fileInput,request)
                    else:
                        file_url = ''
                    CourseMaterial.objects.create(course_id=courseid,module_id=module_id,material_type=filetype,material_link=linkInput,material_file=file_url,language=language,material_label=filematerialname,createdBy = userid)

                    response_={
                            "n": 1,
                            "msg": 'Course material added  successfully',
                            "data":''                     
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
                            "msg": 'Course Material already exist!',
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
                        "msg": 'Course not found',
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
                        "msg": 'Course id not provided',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class DeleteCourseMaterial(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        materialid = request_data.get('materialid')
        userid = str(request.user.id)
        if materialid is not None and materialid != '':
            mobj = CourseMaterial.objects.filter(id=materialid,isActive=True).first()
            if mobj is not None:
                mobj.isActive = False
                mobj.save()
                response_={
                        "n": 1,
                        "msg": 'Study material deleted  successfully',
                        "data":''                     
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
                        "msg": 'Study Material not found',
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
                        "msg": 'Study Material id not provided',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class UpdateCourse(GenericAPIView):
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
        courseid = request_data.get('courseid')
        data['course_name'] = request_data.get('coursename')
        data['course_code'] = request_data.get('coursecode')
        data['training_mode'] = request_data.get('training_mode')
        data['duration'] = request_data.get('duration')
        data['expiry'] = request_data.get('expiry') or None

        if request_data.get('followed_by') != "":
            data['followed_by'] = request_data.get('followed_by')
        else:
            data['followed_by'] = None
        data['topics_covered'] = request_data.get('topics_covered')
        data['pricing'] = request_data.get('pricing')
        data['description'] = request_data.get('description')
        data['languages'] = request_data.get('languages')
        if 'module_list' in request_data.keys():
            moduleslist = request_data.get('module_list')
        else:
            moduleslist = []
        data['og_code'] = str(request.user.og_code)
        # data['createdBy'] = str(request.user.id)

        courseobj = Course.objects.filter(id=courseid).first()
        if courseobj is not None:
       
            coursecode_object = Course.objects.filter(isActive=True,course_code=data['course_code']).exclude(id=int(courseid)).order_by('id')
            if coursecode_object.exists():
                response_={
                            "n": 0,                    
                            "msg": 'Course Code already exists',
                            "data":[],                  
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            
            serializer = CourseSerializer(courseobj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                courseid = serializer.data['id']
                infoid = serializer.data['info_status']

                if infoid is None or infoid == '':
                    courseobj.info_status = '1'
                    courseobj.save()

                for m in moduleslist:
                    if m['module_name'] is not None and m['module_name'] != '':
                        moduleexist = CourseModules.objects.filter(course_id=courseid,module_name=m['module_name'],isActive=True).first()
                        if moduleexist is None:
                            CourseModules.objects.create(course_id=courseid,module_name=m['module_name'],module_description=m['module_description'],module_hours=m['module_hours'])
                
                response_={
                            "n": 1,
                            "msg": 'Course updated successfully',
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
                            "msg": 'Course not added',
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
                            "msg": 'Course not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class getCoursedetails(GenericAPIView):
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
        courseid = request_data.get('id')
        if courseid is not None and courseid != '':
            courseobj = Course.objects.filter(id=courseid).first()
            if courseobj is not None:
                serializer = CourseSerializer(courseobj)
                serializer_data = serializer.data

                moduleexist = CourseModules.objects.filter(course_id=courseid,isActive=True)
                if moduleexist.exists():
                    moduleser = CourseModuleSerializer(moduleexist,many=True)
                    serializer_data.update({
                        'modules_list':moduleser.data
                    })
                else:
                    serializer_data.update({
                        'modules_list':[]
                    })
                    
                lamguage_object = Languages.objects.filter(isActive=True,id__in=serializer.data['languages'])
                if lamguage_object.exists():
                    language_ser = LanguagesSerializer(lamguage_object,many=True)
                    # for l in language_ser.data:
                    #     materialexist = CourseMaterial.objects.filter(course_id=courseid,module_id=module_id)
                    serializer_data.update({
                        'languages_list':language_ser.data
                    })

                

                courseeligiobj = CourseEligibility.objects.filter(course_id=courseid,isActive=True).first()
                if courseeligiobj is not None:
                    courseeligser = CourseEligibilitySerializer(courseeligiobj) 
                    eligibilityid = courseeligser.data['id']
                    serializer_data.update({
                        'eligibility_data':courseeligser.data
                    })
                else:
                    eligibilityid = None
                    serializer_data.update({
                        'eligibility_data':[]
                    })

                if eligibilityid is not None:
                    rankitemobj = rankItemInfo.objects.filter(course_id=courseid,eligibilityid=eligibilityid)
                    if rankitemobj.exists():
                        rankitemser = customisedrankItemInfoSerializer(rankitemobj,many=True)
                        for r in rankitemser.data:
                            rankobj = Rank.objects.filter(id=r['rank']).first()
                            if rankobj is not None:
                                r['rankname'] = rankobj.rank
                            else:
                                r['rankname'] = ''

                            if r['mandatory'] is True :
                                r['mandatory'] = 'true'
                            else:
                                r['mandatory'] = 'false'

                            if r['isActive'] is True :
                                r['isActive'] = 'true'
                            else:
                                r['isActive'] = 'false' 


                        serializer_data.update({
                        'rankitem_data':rankitemser.data
                        })
                    else:
                        serializer_data.update({
                        'rankitem_data':[]
                        })
                else:
                    serializer_data.update({
                    'rankitem_data':[]
                    })

                    
                
                response_={
                                "n": 1,
                                "msg": 'Course data found successfully',
                                "data":serializer_data                        
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
                                "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class getCoursematerial(GenericAPIView):
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
        courseid = request_data.get('courseid')
        moduleid = request_data.get('moduleid')

        courseobj = Course.objects.filter(id=courseid,isActive=True).first()
        if courseobj is not None:
            languages = courseobj.languages
            lamguage_object = Languages.objects.filter(isActive=True,id__in=languages)
            if lamguage_object.exists():
                language_ser = LanguagesSerializer(lamguage_object,many=True)
                for l in language_ser.data:
                    if moduleid is not None and moduleid != "":
                        crmatobjects = CourseMaterial.objects.filter(course_id=courseid,module_id=moduleid,language=l['id'],isActive=True)
                    else:
                        crmatobjects = CourseMaterial.objects.filter(course_id=courseid,language=l['id'],isActive=True)

                    if crmatobjects.exists():
                        mtser = CourseMaterialSerializer(crmatobjects,many=True)
                        for m in mtser.data:
                            userobj = UserAdmin.objects.filter(id=m['createdBy']).first()
                            if userobj is not None:
                                m['createdBy'] = userobj.name
                            else:
                                m['createdBy'] = ''

                            m['createdAt'] = convertcreationdate(m['createdAt'])
                        l['material_list'] = mtser.data
                    else:
                        l['material_list'] = []
                
                response_={
                                "n": 1,
                                "msg": 'Material data found successfully',
                                "data":language_ser.data                        
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
                            "msg": 'No languages found',
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
                            "msg": 'Course not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)







class deletemodule(GenericAPIView):
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
        moduleid = request_data.get('id')
        coursemoduleobj = CourseModules.objects.filter(id=moduleid,isActive=True).first()
        if coursemoduleobj is not None:
            data={}
            data['isActive'] = False
            serializer = CourseModuleSerializer(coursemoduleobj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                materialexist = CourseMaterial.objects.filter(module_id=moduleid,isActive=True)
                if materialexist.exists():
                    matdata={}
                    matdata['isActive'] = False
                    moduleser = CourseMaterialSerializer(materialexist,partial=True,data=matdata)
                    if moduleser.is_valid():
                        moduleser.save()

                response_={
                                "n": 1,
                                "msg": 'Module deleted successfully',
                                "data":''                       
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
                            "msg": 'Module not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)




class trainingmodelist(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        
        tramodeobj = TrainingMode.objects.filter(isActive=True).order_by('id')
        trainingmodeser = TrainingModeSerializer(tramodeobj,many=True)
        response_={
                    "n": 1,
                    "msg": 'Training Mode list found successfully',
                    "data":trainingmodeser.data                       
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        

class getsubcategorylist(GenericAPIView):
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
        categoryid = request_data.get('categoryid')
        if categoryid is not None and categoryid != '':
            subcategory_object = Sub_Category.objects.filter(isActive=True,category_name__in=categoryid).order_by('id')
            subcatser = Sub_CategorySerializer(subcategory_object,many=True)
            response_={
                        "n": 1,
                        "msg": 'subcategory list found successfully',
                        "data": subcatser.data                       
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
                            "msg": 'please provide category id',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class getoptsubcategorylist(GenericAPIView):
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
        categoryid = request_data.get('categoryid')
        if categoryid is not None and categoryid != '':
            categoryobj = Category.objects.filter(id__in=categoryid,isActive=True).order_by('id')
            catser = CategorySerializer(categoryobj,many=True)
            for c in catser.data:
                subcategory_object = Sub_Category.objects.filter(isActive=True,category_name=c['id']).order_by('id')
                subcatser = Sub_CategorySerializer(subcategory_object,many=True)
                c['subcatlist'] = subcatser.data
            response_={
                        "n": 1,
                        "msg": 'subcategory list found successfully',
                        "data": catser.data                       
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
                            "msg": 'please provide category id',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class getdeptwiseranklist(GenericAPIView):
    # authentication_classes=[]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
        departmentid = request_data.get('departmentid')
        if departmentid is not None and departmentid != '':
            Rankobj = Rank.objects.filter(isActive=True,department_name__in=departmentid).order_by('id')
            rankser = RankSerializer(Rankobj,many=True)
            for r in rankser.data:
                deptobj = Department.objects.filter(id=r['department_name']).first()
                r['dept_name'] = deptobj.department_name


            response_={
                        "n": 1,
                        "msg": 'rank list found successfully',
                        "data": rankser.data                       
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
                            "msg": 'please provide rank id',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            


class getdeptranklist(GenericAPIView):
    # authentication_classes=[]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
        departmentid = request_data.get('departmentid')
        if departmentid is not None and departmentid != '':
            deptobj = Department.objects.filter(id__in = departmentid,isActive=True).order_by('id')
            deptser = DepartmentSerializer(deptobj,many=True)
            for d in deptser.data:
                Rankobj = Rank.objects.filter(isActive=True,department_name=d['id']).order_by('id')
                rankser = RankSerializer(Rankobj,many=True)
                d['ranks'] = rankser.data
        
            response_={
                        "n": 1,
                        "msg": 'rank list found successfully',
                        "data": deptser.data                       
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
                            "msg": 'please provide rank id',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            





class addcourseeligibility(GenericAPIView):
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
        courseid = request_data.get('course_id')
        data['course_id'] = courseid
        data['precategory'] = request_data.get('category')
        data['subcategory'] = request_data.get('subcatlist')
        data['predepartment'] = request_data.get('department')
        data['rank'] = request_data.get('rank')
        if 'rankitem_list' in request_data.keys():
            rankitem_list = request_data.get('rankitem_list')
        else:
            rankitem_list = []


        if courseid is not None and courseid != '':
            data['category'] = []
            subcategory_ids = list(map(int, data['subcategory']))
            for c in data['precategory']:
                subcat_ids = Sub_Category.objects.filter(category_name=int(c)).values_list('id',flat=True)
                if any(sub_id in subcategory_ids for sub_id in subcat_ids):
                    data['category'].append(c)

            data['department'] = []
            rank_ids = list(map(int, data['rank']))
            for d in data['predepartment']:
                rankobj_ids = Rank.objects.filter(department_name = int(d)).values_list('id',flat=True)
                if any(r_id in rank_ids for r_id in rankobj_ids):
                    data['department'].append(d)

            courseobj = CourseEligibility.objects.filter(isActive=True,course_id=courseid).first()
            if courseobj is None:
                courseser = CourseEligibilitySerializer(data=data)
                if courseser.is_valid():
                    courseser.save() 
                    neweligibilityid = courseser.data['id']
                    
                    if rankitem_list != []:
                        for r in rankitem_list:
                            if r['selectedValue'] == 'mandatory':
                                mandatoryval = True
                            else:
                                mandatoryval = False

                            rankItemInfo.objects.create(course_id=courseid,eligibilityid=neweligibilityid,rank=r['rank_itemvalue'],mandatory=mandatoryval)

                    coursenewobj = Course.objects.filter(id=courseid).first()
                    coursenewobj.info_status = '2'
                    coursenewobj.save()


                    response_={
                                "n": 1,
                                "msg": 'Course eligibility added successfully',
                                "data": courseser.data                       
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
                            "msg": 'Course eligibility not added',
                            "data":[]                     
                        }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                Courseupdateser = CourseEligibilitySerializer(courseobj,data=data,partial=True)
                if Courseupdateser.is_valid():
                    Courseupdateser.save() 
                    courid = courseobj.course_id
                    elid = courseobj.id

                    if rankitem_list != []:
                        rankItemInfo.objects.filter(course_id=courid,eligibilityid=elid,isActive=True).delete()

                        for r in rankitem_list:
                            if r['selectedValue'] == 'mandatory':
                                mandatoryval = True
                            else:
                                mandatoryval = False

                            rankItemInfo.objects.create(course_id=courid,eligibilityid=elid,rank=r['rank_itemvalue'],mandatory=mandatoryval)
                    coursenewobj = Course.objects.filter(id=courseid).first()
                    coursenewobj.info_status = '2'
                    coursenewobj.save()
                    
                    response_={
                                "n": 1,
                                "msg": 'Course eligibility updated successfully',
                                "data": Courseupdateser.data                       
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
                            "msg": 'Course eligibility not updated',
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
                "msg": 'Please Provide course id',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

            
class GetCourseDetailMultiple(GenericAPIView):
    
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


        course_raw = request_data.get('course_list')
        if course_raw is None or course_raw =='':
            response_={
                            "n": 0,
                            "msg": 'Course ids reuired',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            


        if course_raw.startswith ('['):
            course_list = [ int(x) for x in course_raw ]
        else:
            course_list = [int(course_raw)]

       
        topic_list = []
        module_list = []
        courseobj = Course.objects.filter(id__in=course_list,isActive=True)
        if courseobj.exists():
            serializer = CourseSerializer(courseobj,many=True)
            for i in serializer.data:
                if i['topics_covered'] != "":
                    topics_cov = json.loads(i['topics_covered'])
                    for k in topics_cov:
                        topic_list.append(k['value'])
                
                module_object = CourseModules.objects.filter(isActive=True,course_id=i['id'])
                # module_serializer = CourseModuleSerializer(module_object,many=True)
                # i['module_list'] = module_serializer.data      
                for i in module_object:
                    module_list.append({
                        "id":i.id,
                        "name":i.module_name
                    })
                                  
                
            
            response_={
                        "n": 1,
                        "msg": 'Course data found successfully',
                        "data":serializer.data,
                        "topic_list":topic_list,    
                        "module_list":module_list    
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
                            "msg": 'Course not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

class CoursesByCategory(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        category_id = request_data.get('category_id')
        if category_id is not None and category_id != '':
            courselist = CourseEligibility.objects.filter(category__contains=category_id,isActive=True).values_list('course_id', flat=True)
            if courselist != []:
                courseobjs = Course.objects.filter(id__in=courselist,isActive=True).order_by('-id')[:5]
                courser = CourseSerializer(courseobjs,many=True)
                response_={
                    "n": 1,
                    'msg':'courses found Successfully.',
                    'data':courser.data
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
                'msg':'courses not found.',
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
                'msg':'category id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class AllCoursesByCategory(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        category_id = request_data.get('category_id')
        if category_id is not None and category_id != '':
            if category_id != 'all':
                courselist = CourseEligibility.objects.filter(category__contains=category_id,isActive=True).values_list('course_id', flat=True)
            else:
                courselist = CourseEligibility.objects.filter(isActive=True).values_list('course_id', flat=True)

            if courselist != []:
                courseobjs = Course.objects.filter(id__in=courselist,course_status='Approved',isActive=True).order_by('-id')
                courser = CourseSerializer(courseobjs,many=True)
                for c in courser.data:
                    elbbobj = CourseEligibility.objects.filter(course_id=c['id'],isActive=True).first()
                    if elbbobj is not None:
                        catobj = Category.objects.filter(id__in=elbbobj.category).order_by('category_name')
                        catser = CategorySerializer(catobj,many=True)
                        c['categories'] = catser.data
                    else:
                        c['categories'] = []

                    trobj = TrainingMode.objects.filter(id=c['training_mode']).first()
                    c['training_mode'] = trobj.training_mode

                    crtby = c['createdBy']
                    crtobj = UserAdmin.objects.filter(id=str(crtby)).first()
                    if crtobj is not None:
                        trcenter = crtobj.name
                        if trcenter is not None and trcenter != []:
                            c['center_name'] = crtobj.name
                        else:
                            c['center_name'] = ''
                    else:
                        c['center_name'] = ''


                response_={
                    "n": 1,
                    'msg':'courses found Successfully.',
                    'data':courser.data
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
                'msg':'courses not found.',
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
                'msg':'category id is required.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class GetCoursedetailsbystatus(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
        courseid = request_data.get('id')
        status = request_data.get('status')
        if courseid is not None and courseid != '':
            courseobj = Course.objects.filter(id=courseid,isActive=True).first()
            if courseobj is not None:
                serializer = CourseSerializer(courseobj)
                serializer_data = serializer.data
                lamguage_object = Languages.objects.filter(isActive=True,id__in=serializer_data['languages'])
                if lamguage_object.exists():
                    language_ser = LanguagesSerializer(lamguage_object,many=True)
                    # for l in language_ser.data:
                    #     materialexist = CourseMaterial.objects.filter(course_id=courseid,module_id=module_id)
                    serializer_data.update({
                        'languages_list':language_ser.data
                    })
                else:
                    serializer_data.update({
                        'languages_list':[]
                    })

                if status == 'Overview' or status == '':
                    response_={
                                    "n": 1,
                                    "msg": 'Course overviewdata found successfully',
                                    "data":serializer_data                        
                                }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                    
                elif status == 'Modules':
                    moduleexist = CourseModules.objects.filter(course_id=courseid,isActive=True)
                    if moduleexist.exists():
                        moduleser = CourseModuleSerializer(moduleexist,many=True)
                        serializer_data.update({
                            'modules_list':moduleser.data
                        })
                    else:
                        serializer_data.update({
                            'modules_list':[]
                        })

                    response_={
                                    "n": 1,
                                    "msg": 'Course module data found successfully',
                                    "data":serializer_data                        
                                }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                   
                elif status == 'Resources':
                    moduleid = request_data.get('moduleid')
                    languageid = request_data.get('languageid')

                    if languageid is not None and languageid != '':
                        if languageid != 'All':
                            crmatobjects = CourseMaterial.objects.filter(course_id=courseid,language=languageid,isActive=True)
                        else:
                            crmatobjects = CourseMaterial.objects.filter(course_id=courseid,isActive=True)

                        if moduleid is not None and moduleid != '':
                            crmatobjects =  crmatobjects.filter(module_id=moduleid)

                        if crmatobjects.exists():
                            mtser = CourseMaterialSerializer(crmatobjects,many=True)
                            for m in mtser.data:
                                if m['module_id'] is not None and m['module_id'] != []:
                                    moduleobj = CourseModules.objects.filter(id=m['module_id']).first()
                                    if moduleobj is not None:
                                        m['modulename'] = moduleobj.module_name
                                    else:
                                        m['modulename'] = ''
                                else:
                                    m['modulename'] = ''

                                userobj = UserAdmin.objects.filter(id=m['createdBy']).first()
                                if userobj is not None:
                                    m['createdBy'] = userobj.name
                                else:
                                    m['createdBy'] = ''

                                m['createdAt'] = convertcreationdate(m['createdAt'])
                        
                            response_={
                                            "n": 1,
                                            "msg": 'Material data found successfully',
                                            "data":mtser.data                        
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
                                            "msg": 'Material data found successfully',
                                            "data":mtser.data                        
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
                                    "msg": 'No languages found',
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
                                "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class GetCoursedetailsbyId(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
        courseid = request_data.get('id')
        userid = request_data.get('user_id')

        if courseid is not None and courseid != '':
            courseobj = Course.objects.filter(id=courseid,isActive=True).first()
            if courseobj is not None:
                serializer = CourseSerializer(courseobj)
                serializer_data = serializer.data

                trobj = TrainingMode.objects.filter(id=serializer_data['training_mode']).first()
                if trobj is not None and trobj != '':
                    trmode = trobj.training_mode
                else:
                    trmode = ''

                serializer_data.update({
                        'training_mode':trmode
                })

                crtby = serializer_data['createdBy']
                crtobj = UserAdmin.objects.filter(id=str(crtby)).first()
                if crtobj is not None:
                    trcenter = crtobj.name
                    if trcenter is not None and trcenter != []:
                        center_name = crtobj.name
                    else:
                        center_name = ''
                else:
                    center_name = ''

                serializer_data.update({
                        'center_name':center_name
                })

                topics_covered = serializer_data['topics_covered']
                if topics_covered is not None and topics_covered != '':
                    if isinstance(topics_covered, str):  # Ensure it's a string before parsing
                        topics_covered = json.loads(topics_covered)

                    # Extract the 'value' field from each dictionary
                    topics_list = [item["value"] for item in topics_covered]
                else:
                    topics_list = []
                
                serializer_data.update({
                        'topics_list':topics_list
                    })
                
                moduleexist = CourseModules.objects.filter(course_id=courseid,isActive=True)
                if moduleexist.exists():
                    moduleser = CourseModuleSerializer(moduleexist,many=True)
                    serializer_data.update({
                        'modules_list':moduleser.data
                    })
                else:
                    serializer_data.update({
                        'modules_list':[]
                    })

                    
                lamguage_object = Languages.objects.filter(isActive=True,id__in=serializer_data['languages'])
                if lamguage_object.exists():
                    language_ser = LanguagesSerializer(lamguage_object,many=True)
                    # for l in language_ser.data:
                    #     materialexist = CourseMaterial.objects.filter(course_id=courseid,module_id=module_id)
                    serializer_data.update({
                        'languages_list':language_ser.data
                    })
                else:
                    serializer_data.update({
                        'languages_list':[]
                    })

                ebobj = CourseEligibility.objects.filter(course_id=courseid,isActive=True).first()


               
                if userid is not None:
                    cadobj = Candidate.objects.filter(id=str(userid)).first()
                    dept = cadobj.department 
                    rank = cadobj.rank
                    eligibobj = CourseEligibility.objects.filter(department__contains = str(dept),rank__contains = str(rank),course_id=courseid,isActive=True).first()
                    if eligibobj is not None:
                        enroll_status = 'Allowed'
                    else:
                        enroll_status = 'Not Allowed'
                else:
                    enroll_status = 'Not Allowed'

                serializer_data.update({
                        'enroll_status':enroll_status
                    })
                response_={
                                "n": 1,
                                "msg": 'Course data found successfully',
                                "data":serializer_data                        
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
                                "msg": 'Course not found',
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
                    "msg": 'Course id not provided',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class GetCourseResources(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        courseid = request_data.get('courseid')
        moduleid = request_data.get('moduleid')
        languageid = request_data.get('languageid')
        courseobj = Course.objects.filter(id=courseid,isActive=True).first()
        if courseobj is not None:
            if languageid is not None and languageid != '':
                if languageid != 'All':
                    crmatobjects = CourseMaterial.objects.filter(course_id=courseid,language=languageid,isActive=True)
                else:
                    crmatobjects = CourseMaterial.objects.filter(course_id=courseid,isActive=True)

                if moduleid is not None and moduleid != '':
                    if moduleid != 'All':
                        crmatobjects =  crmatobjects.filter(module_id=moduleid)
                    else:
                        crmatobjects = crmatobjects
                if crmatobjects.exists():
                    mtser = CourseMaterialSerializer(crmatobjects,many=True)
                    for m in mtser.data:
                        if m['module_id'] is not None and m['module_id'] != []:
                            moduleobj = CourseModules.objects.filter(id=m['module_id']).first()
                            if moduleobj is not None:
                                m['modulename'] = moduleobj.module_name
                            else:
                                m['modulename'] = ''
                        else:
                            m['modulename'] = ''

                        userobj = UserAdmin.objects.filter(id=m['createdBy']).first()
                        if userobj is not None:
                            m['createdBy'] = userobj.name
                        else:
                            m['createdBy'] = ''

                        m['createdAt'] = convertcreationdate(m['createdAt'])
                   
                    response_={
                                    "n": 1,
                                    "msg": 'Material data found successfully',
                                    "data":mtser.data                        
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
                            "msg": 'No material found',
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
                            "msg": 'No languages found',
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
                            "msg": 'Course not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class GetCourseCategoryList(GenericAPIView):
    # authentication_classes=[CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        course_ids = Course.objects.filter(isActive=True,course_status='Approved').values_list('id', flat=True)
        if course_ids != []:
            catobj = CourseEligibility.objects.filter(course_id__in=course_ids).values_list('category',flat=True)
            unique_categories = set()
            for cat in catobj:
                if cat:
                    unique_categories.update(cat)

            unique_categories = list(unique_categories)
            if unique_categories != []:

                categoryobjs = Category.objects.filter(id__in=unique_categories,isActive=True)
                categoryser = CategorySerializer(categoryobjs,many=True)

                response_={
                            "n": 1,
                            "msg": 'Category list found successfully',
                            "data":categoryser.data                       
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
                            "msg": 'Category not found',
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
                        "msg": 'Courses for category not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)





class GetCategoryList(GenericAPIView):
    # authentication_classes=[CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        course_ids = Course.objects.filter(isActive=True).values_list('id', flat=True)
        if course_ids != []:
            catobj = CourseEligibility.objects.filter(course_id__in=course_ids).values_list('category',flat=True)
            unique_categories = set()
            for cat in catobj:
                if cat:
                    unique_categories.update(cat)

            unique_categories = list(unique_categories)
            if unique_categories != []:

                categoryobjs = Category.objects.filter(id__in=unique_categories,isActive=True)
                categoryser = CategorySerializer(categoryobjs,many=True)

                response_={
                            "n": 1,
                            "msg": 'Category list found successfully',
                            "data":categoryser.data                       
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
                            "msg": 'Category not found',
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
                        "msg": 'Courses for category not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
          


class InstitutionsList(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        countryid = request_data.get('countryid')
        rrcourseid =request_data.get('courseid')
        courseid = [int(rrcourseid)]
        
       
        courseobj = Course.objects.filter(id__in=courseid,isActive=True).first()
        if courseobj is not None:
            if countryid is not None and countryid != '':
                tc_Scheduleobj = Schedule.objects.filter(course_ids__in=courseid,start_date__gt=date.today(),action_status='Approved',isActive=True).values_list('training_center_ids', flat=True).distinct()


                if tc_Scheduleobj != []:
                    if countryid == 'All':
                        Instobj = UserAdmin.objects.filter(id__in=tc_Scheduleobj,isActive=True,).order_by('name')
                    else:
                        Instobj = UserAdmin.objects.filter(id__in=tc_Scheduleobj,isActive=True,country=int(countryid)).order_by('name')
                    if Instobj.exists():
                        Instobjser = UserAdminSerializer(Instobj,many=True)
                        for i in Instobjser.data:
                            tclist = [str(i['id'])]
                            batchesobj = Schedule.objects.filter(course_ids__in=courseid,start_date__gt=date.today(),action_status='Approved',isActive=True,training_center_ids__in = tclist)
                            sch_batchser = ScheduleSerializer(batchesobj,many=True)
                            bcounter = 1
                            for b in sch_batchser.data:
                                b['start_date'] = convertdate(str(b['start_date']))
                                b['end_date'] = convertdate(str(b['end_date']))

                                b['counter'] = bcounter
                                bcounter += 1
                                candidates_enrolled = Enrollments.objects.filter(schedule=str(b['id']),course=courseid,enrollments_status='2').count()
                                b['candidates_enrolled'] = candidates_enrolled

                                if int(b['max_capacity']) == int(candidates_enrolled):
                                    b['capacity'] = 'Full'
                                elif int(b['max_capacity']) > int(candidates_enrolled):
                                    percentage = (int(candidates_enrolled) / int(b['max_capacity'])) * 100
                                    if 70 < percentage < 100:
                                        b['capacity'] = 'Filling Fast '
                                    else:
                                        b['capacity'] = 'Available'
                                else:
                                    b['capacity'] = 'Status Unknown'

                                course_payment = courseobj.pricing
                                payment_array = {
                                    'course':rrcourseid,
                                    'schedule':str(b['id']),
                                    'trainingcenter_id':i['id'],
                                    'course_payment':course_payment
                                }
                                base_data_to_serialize = convert_decimals_to_float(payment_array)
                                encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
                                
                                b['payment_link'] = candidateURL + '/panel/payment/' + encrypt_base_test_examination_link
                            
                            i['batches'] = sch_batchser.data
                            i['payment_array'] = payment_array

                        response_={
                                        "n": 1,
                                        "msg": 'Institutions found successfully',
                                        "data":Instobjser.data                       
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
                                "msg": 'No active Institutions',
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
                                "msg": 'Institutions Not found',
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
                            "msg": 'Please provide country',
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
                            "msg": 'Course not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class RecommendationList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        listtype = request_data.get('listtype')
        candidateid = str(request.user.id)
        if listtype is not None and listtype !='':
            cd_exist = Candidate.objects.filter(id=candidateid,isActive=True).first()
            if cd_exist is not None :
                cdrank = cd_exist.rank
                if cdrank is not None and cdrank != '':
                    if listtype == 'Mandatory':
                        Courses = rankItemInfo.objects.filter(rank=cdrank,isActive=True,mandatory=True).values_list('course_id', flat=True)
                    elif listtype == 'Recommended':
                        Courses = rankItemInfo.objects.filter(rank=cdrank,isActive=True,mandatory=False).values_list('course_id', flat=True)
                    else:
                        Courses = rankItemInfo.objects.filter(rank=cdrank,isActive=True).values_list('course_id', flat=True)

                    courseid = list(set(Courses))
                    if courseid != []:
                        Courseobj = Course.objects.filter(id__in=courseid,isActive=True,course_status='Approved')
                        CourseSer = CourseSerializer(Courseobj,many=True)
                        for c in CourseSer.data:
                            enrollobj = Enrollments.objects.filter(candidate=candidateid,course=str(c['id']),isActive=True).first()
                            if enrollobj is not None:
                                if enrollobj.enrollments_status == '2' :
                                    c['enroll_status'] = 'Enrolled'
                                elif enrollobj.enrollments_status == '1':
                                    c['enroll_status'] = 'Requested'
                                elif enrollobj.enrollments_status == '3':
                                    c['enroll_status'] = 'Declined'
                                else:
                                    c['enroll_status'] = 'Not Known'
                            else:
                                c['enroll_status'] = 'Not Applied'


                            trobj = TrainingMode.objects.filter(id=c['training_mode']).first()
                            c['training_mode'] = trobj.training_mode

                            getmdobj = rankItemInfo.objects.filter(rank=cdrank,course_id=c['id'],isActive=True).first()
                            if getmdobj is not None:
                                if getmdobj.mandatory == True:
                                    c['coursetype'] = 'Mandatory'
                                else:
                                    c['coursetype'] = 'Recommended'
                            else:
                                c['coursetype'] = 'Recommended'
                            
                            
                        response_={
                                "n": 1,
                                "msg": 'course data found successfully',
                                "data":CourseSer.data                        
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
                                "msg": 'courses not found',
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
                            "msg": 'candidate does not have rank',
                            "data":{}                    
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
                            "msg": 'candidate not found',
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
                            "msg": 'course list type not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            


class TrainingList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        current_date = date.today()
        statustype = request_data.get('statustype')
        candidateid = str(request.user.id)
        if statustype is not None and statustype !='':
            Courses = Enrollments.objects.filter(candidate=candidateid,isActive=True,enrollments_status='2').values_list('course', flat=True)
            schedule_list = Enrollments.objects.filter(candidate=candidateid,isActive=True,enrollments_status='2').values_list('schedule', flat=True)
            schedule_list_int = list(map(int, schedule_list))
            courseid = set(Courses)
            
            if courseid != []:
                if statustype == "All":
                    Courseobj = Course.objects.filter(id__in=courseid,isActive=True)
                elif statustype == "NS":
                    Courseobj = Course.objects.filter(isActive=True,expiry__gt = current_date,id__in=list(Schedule.objects.filter(isActive=True,id__in=schedule_list_int,course_ids__in = courseid,start_date__gt = current_date).values_list('course_ids', flat=True)))
                elif statustype == "IN":
                    Courseobj = Course.objects.filter(isActive=True,expiry__gt = current_date,id__in=list(Schedule.objects.filter(isActive=True,id__in=schedule_list_int,course_ids__in = courseid,start_date__lte = current_date,end_date__gte = current_date).values_list('course_ids', flat=True)))
                elif statustype == "CP":
                    Courseobj = Course.objects.filter(isActive=True,expiry__gt = current_date,id__in=list(Schedule.objects.filter(isActive=True,id__in=schedule_list_int,course_ids__in = courseid,end_date__lt = current_date).values_list('course_ids', flat=True)))
                else:
                    Courseobj = Course.objects.filter(id__in=courseid,isActive=True,expiry__lt = current_date)
                
                CourseSer = CourseSerializer(Courseobj,many=True)
                for c in CourseSer.data:

                    trobj = TrainingMode.objects.filter(id=c['training_mode']).first()
                    if trobj is not None and trobj != '':
                        c['trmode'] = trobj.training_mode
                    else:
                        c['trmode'] = ''

                    crtby = c['createdBy']
                    enrrobj = Enrollments.objects.filter(course=str(c['id']),isActive=True,enrollments_status='2').first()
                    if enrrobj is not None:
                        trcenterid = enrrobj.trainingcenter_id
                        crtobj = UserAdmin.objects.filter(id=str(trcenterid)).first()
                        if crtobj is not None:
                            trcenter = crtobj.name
                            if trcenter is not None and trcenter != []:
                                c['center_name'] = crtobj.name
                            else:
                                c['center_name'] = ''
                        else:
                            c['center_name'] = ''
                    else:
                        c['center_name'] = ''
                    

                response_={
                        "n": 1,
                        "msg": 'course data found successfully',
                        "data":CourseSer.data                        
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
                        "msg": 'enrolled courses not found',
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
                            "msg": 'course list type not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
