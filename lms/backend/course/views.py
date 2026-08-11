from django.shortcuts import render
import json
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
from django.db.models import Q
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
        data['course_name'] = request_data.get('course_name')
        data['course_code'] = request_data.get('course_code')
        data['duration'] = request_data.get('duration')
        data['category_id'] = request_data.get('category_id')
        data['sub_category_id'] = request_data.get('sub_category_id')

        data['pricing'] = request_data.get('pricing')
        data['description'] = request_data.get('description')
        data['languages'] = request_data.get('languages')

        if 'subject_list' in request_data.keys():
            subjectslist = request_data.get('subject_list')
        else:
            subjectslist = []
        print("request_data",request_data)
        data['og_code'] = str(request.user.og_code)
        data['createdBy'] = str(request.user.id)

        coursecode_object = Course.objects.filter(isActive=True,course_code=data['course_code']).first()
        print("coursecode_object",coursecode_object)
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
        print("subjectslist",subjectslist)
        serializer = CourseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            courseid = serializer.data['id']



            if subjectslist != []:
                for m in subjectslist:
                    if m['subject_id'] != '':
                        subjectexist = CourseSubjects.objects.filter(course_id=courseid,subject_id=m['subject_id'],isActive=True,semister_no=m['semister_no']).first()
                        if subjectexist is None:
                            CourseSubjects.objects.create(course_id=courseid,subject_id=m['subject_id'],semister_no=m['semister_no'])

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
            courselistobj = Course.objects.filter(course_status=course_status,isActive=True,og_code=str(request.user.og_code)).order_by('-createdAt')
        else:
            courselistobj = Course.objects.filter(isActive=True,og_code=str(request.user.og_code)).order_by('-createdAt')


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
                if course_idobj.course_status is True:
                    course_idobj.course_status = False
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

class ActivateCourse(GenericAPIView):
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
                if course_idobj.course_status is False:
                    course_idobj.course_status = True
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
        data['course_name'] = request_data.get('course_name')
        data['course_code'] = request_data.get('course_code')
        data['duration'] = request_data.get('duration')
        data['pricing'] = request_data.get('pricing')
        data['description'] = request_data.get('description')
        data['languages'] = request_data.get('languages')
        if 'subject_list' in request_data.keys():
            subjectslist = request_data.get('subject_list')
        else:
            subjectslist = []
        data['category_id'] = request_data.get('category_id')
        data['sub_category_id'] = request_data.get('sub_category_id')

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
                CourseSubjects.objects.filter(course_id=courseid,isActive=True).update(isActive=False)
                if subjectslist != []:
                    for m in subjectslist:
                        if m['subject_id'] != '':
                            subjectexist = CourseSubjects.objects.filter(course_id=courseid,subject_id=m['subject_id'],semister_no=m['semister_no']).first()
                            if subjectexist is None:
                                CourseSubjects.objects.create(course_id=courseid,subject_id=m['subject_id'],semister_no=m['semister_no'])
                            else:
                                subjectexist.isActive=True
                                subjectexist.save()


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
                            "msg": 'Course not deleted',
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

class DeleteCourse(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):

        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        data = {
            "isActive":False
        }
        courseid = request_data.get('courseid')

        courseobj = Course.objects.filter(id=courseid).first()
        if courseobj is not None:



            serializer = CourseSerializer(courseobj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                courseid = serializer.data['id']
                CourseSubjects.objects.filter(course_id=courseid,isActive=True).update(isActive=False)



                response_={
                            "n": 1,
                            "msg": 'Course deleted successfully',
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
                            "msg": 'Course not deleted',
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
        courseid = request_data.get('courseid')
        if courseid is not None and courseid != '':
            courseobj = Course.objects.filter(id=courseid).first()
            if courseobj is not None:
                serializer = CourseSerializer(courseobj)
                serializer_data = serializer.data

                subject_ids = list(CourseSubjects.objects.filter(course_id=courseid,isActive=True).values_list('subject_id',flat=True))
                subject_obj=Subject.objects.filter(id__in=subject_ids)
                if subject_obj.exists():
                    subjectser = SubjectSerializer(subject_obj,many=True)
                    serializer_data.update({
                        'subjects_list':subjectser.data
                    })
                else:
                    serializer_data.update({
                        'subjects_list':[]
                    })

                lamguage_object = Languages.objects.filter(isActive=True,id__in=serializer.data['languages'])
                if lamguage_object.exists():
                    language_ser = LanguagesSerializer(lamguage_object,many=True)
                    serializer_data.update({
                        'languages_list':language_ser.data
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


def _subject_response(encryped_header, response_):
    if encryped_header == "1":
        data_to_serialize = convert_decimals_to_float(response_)
        encdata = encrypt_data(json.dumps(data_to_serialize))
        return Response(encdata, status=200)
    return Response(response_, status=200)


def _subject_value(request_data, *keys):
    for key in keys:
        value = request_data.get(key)
        if value is not None:
            if value == "":
                return None
            return value
    return None


def _build_subject_data(request_data, user, include_created=False):
    data = {
        "subject_code": _subject_value(request_data, "subject_code", "subjectcode"),
        "subject_name": _subject_value(request_data, "subject_name", "subjectname"),
        "short_name": _subject_value(request_data, "short_name", "shortname"),
        "department_id": _subject_value(request_data, "department_id"),
        "subject_type": _subject_value(request_data, "subject_type") or "THEORY",
        "theory_credits": _subject_value(request_data, "theory_credits") or 0,
        "practical_credits": _subject_value(request_data, "practical_credits") or 0,
        "total_credits": _subject_value(request_data, "total_credits") or 0,
        "theory_marks": _subject_value(request_data, "theory_marks") or 0,
        "practical_marks": _subject_value(request_data, "practical_marks") or 0,
        "internal_marks": _subject_value(request_data, "internal_marks") or 0,
        "total_marks": _subject_value(request_data, "total_marks") or 0,
        "description": _subject_value(request_data, "description"),
        "status": request_data.get("status", True),
    }

    if include_created:
        data["createdBy"] = str(user.id)
    else:
        data["updatedBy"] = str(user.id)

    return data


def _build_subject_update_data(request_data, user):
    field_keys = {
        "subject_code": ("subject_code", "subjectcode"),
        "subject_name": ("subject_name", "subjectname"),
        "short_name": ("short_name", "shortname"),
        "department_id": ("department_id",),
        "subject_type": ("subject_type",),
        "theory_credits": ("theory_credits",),
        "practical_credits": ("practical_credits",),
        "total_credits": ("total_credits",),
        "theory_marks": ("theory_marks",),
        "practical_marks": ("practical_marks",),
        "internal_marks": ("internal_marks",),
        "total_marks": ("total_marks",),
        "description": ("description",),
        "status": ("status",),
    }
    data = {}
    for field, keys in field_keys.items():
        if any(key in request_data for key in keys):
            data[field] = _subject_value(request_data, *keys)
    data["updatedBy"] = str(user.id)
    return data


class AddSubject(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        data = _build_subject_data(request_data, request.user, True)

        if data["subject_code"] in (None, ""):
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject code is required",
                "data": [],
            })

        if data["subject_name"] in (None, ""):
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject name is required",
                "data": [],
            })

        subject_object = Subject.objects.filter(
            isActive=True,
            department_id=data["department_id"],
            subject_code=data["subject_code"],
        ).first()
        if subject_object is not None:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject Code already exists",
                "data": [],
            })

        serializer = SubjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return _subject_response(encryped_header, {
                "n": 1,
                "msg": "Subject added successfully",
                "data": serializer.data,
            })

        return _subject_response(encryped_header, {
            "n": 0,
            "msg": "Subject not added",
            "data": serializer.errors,
        })


class CollegeSubjectFilterList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectlistobj = Subject.objects.filter(isActive=True).order_by("-createdAt")
        department_id = request_data.get("department_id")
        subject_type = request_data.get("subject_type")
        status = request_data.get("status")
        search = request_data.get("search")

        if department_id not in (None, ""):
            subjectlistobj = subjectlistobj.filter(department_id=department_id)
        if subject_type not in (None, ""):
            subjectlistobj = subjectlistobj.filter(subject_type=subject_type)
        if status not in (None, ""):
            subjectlistobj = subjectlistobj.filter(status=status)
        if search not in (None, ""):
            subjectlistobj = subjectlistobj.filter(
                Q(subject_code__icontains=search)
                | Q(subject_name__icontains=search)
                | Q(short_name__icontains=search)
            )

        if subjectlistobj.exists():
            page4 = self.paginate_queryset(subjectlistobj)
            serializer = SubjectSerializer(page4, many=True)
            for subject in serializer.data:
                cretby = UserAdmin.objects.filter(id=subject["createdBy"]).first()
                if cretby is not None and cretby != "":
                    if cretby.user_type == 5:
                        addedby = str(cretby.first_name) + " " + str(cretby.last_name)
                    else:
                        addedby = cretby.name
                else:
                    addedby = ""
                subject["addedby"] = addedby

            response_ = {
                "n": 1,
                "msg": "Subject list found successfully",
                "data": serializer.data,
            }
            if encryped_header == "1":
                paigna = self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        return _subject_response(encryped_header, {
            "n": 0,
            "msg": "subject not found",
            "data": [],
        })


class CollegeSubjectList(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectlistobj = Subject.objects.filter(
            isActive=True,
            status=True,
        ).order_by("subject_name")

        department_id = request_data.get("department_id")
        subject_type = request_data.get("subject_type")

        if department_id not in (None, ""):
            subjectlistobj = subjectlistobj.filter(department_id=department_id)
        if subject_type not in (None, ""):
            subjectlistobj = subjectlistobj.filter(subject_type=subject_type)

        serializer = SubjectSerializer(subjectlistobj, many=True)
        return _subject_response(encryped_header, {
            "n": 1,
            "msg": "Subject list found successfully",
            "data": serializer.data,
        })


class UpdateSubject(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectid = request_data.get("subjectid") or request_data.get("subject_id")
        if subjectid in (None, ""):
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject id not provided",
                "data": [],
            })

        subjectobj = Subject.objects.filter(id=subjectid).first()
        if subjectobj is None:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject not found",
                "data": [],
            })

        data = _build_subject_update_data(request_data, request.user)
        subject_code = data.get("subject_code", subjectobj.subject_code)
        department_id = data.get("department_id", subjectobj.department_id)
        if subject_code not in (None, ""):
            subject_object = Subject.objects.filter(
                isActive=True,
                department_id=department_id,
                subject_code=subject_code,
            ).exclude(id=subjectid)
            if subject_object.exists():
                return _subject_response(encryped_header, {
                    "n": 0,
                    "msg": "Subject Code already exists",
                    "data": [],
                })

        serializer = SubjectSerializer(subjectobj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return _subject_response(encryped_header, {
                "n": 1,
                "msg": "Subject updated successfully",
                "data": serializer.data,
            })

        return _subject_response(encryped_header, {
            "n": 0,
            "msg": "Subject not updated",
            "data": serializer.errors,
        })


class DeleteSubject(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectid = request_data.get("subjectid") or request_data.get("subject_id")
        subjectobj = Subject.objects.filter(id=subjectid).first()
        if subjectobj is None:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject not found",
                "data": [],
            })

        serializer = SubjectSerializer(
            subjectobj,
            data={"isActive": False, "updatedBy": str(request.user.id)},
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return _subject_response(encryped_header, {
                "n": 1,
                "msg": "Subject deleted successfully",
                "data": serializer.data,
            })

        return _subject_response(encryped_header, {
            "n": 0,
            "msg": "Subject not deleted",
            "data": serializer.errors,
        })


class GetSubjectdetails(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectid = request_data.get("subjectid") or request_data.get("subject_id")
        if subjectid in (None, ""):
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject id not provided",
                "data": [],
            })

        subjectobj = Subject.objects.filter(id=subjectid).first()
        if subjectobj is None:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject not found",
                "data": [],
            })

        serializer = SubjectSerializer(subjectobj)
        return _subject_response(encryped_header, {
            "n": 1,
            "msg": "Subject data found successfully",
            "data": serializer.data,
        })


class DeactivateSubject(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectid = request_data.get("subjectid") or request_data.get("subject_id")
        subjectobj = Subject.objects.filter(id=subjectid).first()
        if subjectobj is None:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject not found",
                "data": [],
            })

        if subjectobj.status is False:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject already deactivated",
                "data": [],
            })

        subjectobj.status = False
        subjectobj.updatedBy = str(request.user.id)
        subjectobj.save()
        return _subject_response(encryped_header, {
            "n": 1,
            "msg": "Subject deactivated successfully",
            "data": "",
        })


class ActivateSubject(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if "encrypted" in request.headers.keys():
            encryped_header = request.headers.get("encrypted")

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        subjectid = request_data.get("subjectid") or request_data.get("subject_id")
        subjectobj = Subject.objects.filter(id=subjectid).first()
        if subjectobj is None:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject not found",
                "data": [],
            })

        if subjectobj.status is True:
            return _subject_response(encryped_header, {
                "n": 0,
                "msg": "Subject is already active",
                "data": [],
            })

        subjectobj.status = True
        subjectobj.updatedBy = str(request.user.id)
        subjectobj.save()
        return _subject_response(encryped_header, {
            "n": 1,
            "msg": "Subject activated successfully",
            "data": "",
        })


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














