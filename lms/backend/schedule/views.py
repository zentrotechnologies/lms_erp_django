import uuid

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from .serializers import *
from lms.settings import *
from django.contrib.auth.hashers import make_password,check_password
from adminauth.jwt import *
from helpers.validations import *
from rest_framework import permissions
from course.models import *
from course.serializers import SubjectSerializer
from master.models import ClassGroup, AcademicYear, Department, Semester
from master.serializers import ClassGroupSerializer
# Create your views here.
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from candidate.models import *
from candidate.serializers import *

from enrollments.models import *
from enrollments.serializers import *

from attendance.models import *
from attendance.serializers import *
from datetime import date, timedelta
from django.utils import timezone

def resolve_faculty_name(faculty_id):
    if faculty_id in (None, ''):
        return ""

    faculty_value = str(faculty_id).strip()
    if not faculty_value:
        return ""

    try:
        uuid.UUID(faculty_value)
    except (AttributeError, TypeError, ValueError):
        return ""

    faculty_obj = UserAdmin.objects.filter(id=faculty_value, isActive=True).first()
    if faculty_obj is None:
        return ""

    if getattr(faculty_obj, 'user_type', None) == 5:
        return f"{faculty_obj.first_name or ''} {faculty_obj.last_name or ''}".strip()
    return faculty_obj.name or ""


def calculate_days_difference(start_date_str, end_date_str):
    # Convert string dates to date objects
    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)
    # Calculate the difference in days
    delta_days = (end_date - start_date).days
    # Ensure at least one day is counted
    return max(delta_days, 0) + 1

def get_dates_from_range(start_date, end_date):
    """
    Generate a list of dates between start_date and end_date (inclusive) in yyyy-mm-dd format.
    
    Args:
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    
    Returns:
        list: List of dates in yyyy-mm-dd format
    """
    date_list = []
    
    # Convert string dates to datetime objects
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Handle case where start date is after end date
    if start > end:
        raise ValueError("Start date cannot be after end date")
    
    # Generate dates
    current_date = start
    while current_date <= end:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    return date_list
def process_time_ranges(start_date, end_date, start_time, end_time):
    """
    Process time ranges where if start_time > end_time, end date becomes next day
    
    Args:
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
        start_time (str): Start time in HH:MM format
        end_time (str): End time in HH:MM format
    
    Returns:
        list: List of dictionaries with start and end datetime strings
    """
    result = []
    dates_range = get_dates_from_range(start_date, end_date)
    
    for date_str in dates_range:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Parse times
        start_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date_str} {end_time}", "%Y-%m-%d %H:%M")
        
        if start_time > end_time:
            # If start time is later than end time, end is next day
            end_dt += timedelta(days=1)
        
        result.append({
            "start": start_dt.strftime("%Y-%m-%d %H:%M"),
            "end": end_dt.strftime("%Y-%m-%d %H:%M"),
            "date": date_str
        })
    
    return result

class AddSchedule(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):

        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        
        course_ids=json.loads(request_data.get('course_ids'))
        if course_ids is None or course_ids =='':
            msg="Please provide course ids"
            validation_status=False 

        request_data['course_ids']=course_ids
        
        college_ids=json.loads(request_data.get('college_ids'))
        if college_ids is None or college_ids =='':
            msg="Please provide college ids"
            validation_status=False 
            
        request_data['college_ids']=college_ids
            

        
        start_date=request_data.get('start_date')#yyyy-mm-dd
        if start_date is None or start_date =='':
            msg="Please provide schedule start date "
            validation_status=False 
        else:
            try:
                start_date_d = datetime.strptime(start_date, '%Y-%m-%d').date()
                today = datetime.now().date()
                if start_date_d <= today:
                    msg = "Start date must be in the future"
                    validation_status = False
            except ValueError:
                msg = "Invalid start date format. Please use YYYY-MM-DD format"
                validation_status = False
            
            
        end_date=request_data.get('end_date') #yyyy-mm-dd
        if end_date is None or end_date =='':
            msg="Please provide schedule end date "
            validation_status=False 
        else:
            try:
                end_date_d = datetime.strptime(end_date, '%Y-%m-%d').date()
                today = datetime.now().date()
                if end_date_d <= today:
                    msg = "End date must be in the future"
                    validation_status = False
                
                # Additional check if start_date is valid and end_date is before start_date
                if validation_status and 'start_date' in locals() and end_date_d < start_date_d:
                    msg = "End date cannot be before start date"
                    validation_status = False
            except ValueError:
                msg = "Invalid end date format. Please use YYYY-MM-DD format"
                validation_status = False    
            
        start_time=request_data.get('start_time')
        if start_time is None or start_time =='':
            msg="Please provide schedule start time "
            validation_status=False 
            
        end_time=request_data.get('end_time')
        if end_time is None or end_time =='':
            msg="Please provide schedule end time "
            validation_status=False 
            
        max_capacity=request_data.get('max_capacity')
        if max_capacity is None or max_capacity =='':
            msg="Please provide schedule max capacity "
            validation_status=False 
            
        branch_id=request_data.get('branch_id')
        # if branch_id is None or branch_id =='':
        #     msg="Please provide branch id"
        #     validation_status=False 
            
        mode=request_data.get('mode')
        if mode is None or mode =='':
            msg="Please provide mode"
            validation_status=False 
            
        schedulename=request_data.get('schedulename')
        if schedulename is None or schedulename =='':
            msg="Please provide schedule name"
            validation_status=False 

        already_exists_schedule=Schedule.objects.filter(start_date=start_date,end_date=end_date,course_ids__in=course_ids,mode=mode,isActive=True).first()
        if already_exists_schedule is not None:
            msg="Schedule for this date range  is already exists"
            validation_status=False 


        if validation_status:
            # already_exists=


            serializer=ScheduleSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()
                response_={
                        "n": 1,
                        "msg": 'New Schedule added successfully',
                        "data":''                     
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                first_key, first_value = next(iter(serializer.errors.items()))
                response_={
                            "n": 0,
                            "msg": first_key+' : '+ first_value[0],
                            "data":serializer.errors                    
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)



class LectureTypeDropdown(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        if template_id in (None, ''):
            response_ = {"n": 0, "msg": "template_id not provided", "data": []}
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        lecture_types = list(
            TimetableSlot.objects.filter(timetable_template_id=template_id, is_active=True)
            .values_list('lecture_type', flat=True).distinct()
        )

        data = [{"id": i + 1, "name": lt} for i, lt in enumerate(lecture_types)]
        response_ = {"n": 1, "msg": "Lecture type list found successfully", "data": data}
        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


class SubjectDropdown(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        if template_id in (None, ''):
            response_ = {"n": 0, "msg": "template_id not provided", "data": []}
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        course_ids = list(
            TimetableSlot.objects.filter(timetable_template_id=template_id, is_active=True)
            .values_list('course_id', flat=True).distinct()
        )
        if not course_ids:
            response_ = {"n": 0, "msg": "No courses found for this template", "data": []}
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        subject_ids = list(
            CourseSubjects.objects.filter(course_id__in=course_ids, isActive=True)
            .values_list('subject_id', flat=True).distinct()
        )
        subjectlistobj = Subject.objects.filter(isActive=True, status=True, id__in=subject_ids).order_by('subject_name')
        if subjectlistobj.exists():
            serializer = SubjectSerializer(subjectlistobj, many=True)
            response_ = {"n": 1, "msg": "Subject list found successfully", "data": serializer.data}
        else:
            response_ = {"n": 0, "msg": "Subject not found", "data": []}

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


class FacultyDropdown(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        if template_id in (None, ''):
            response_ = {"n": 0, "msg": "template_id not provided", "data": []}
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        raw_faculty_ids = list(
            TimetableSlot.objects.filter(timetable_template_id=template_id, is_active=True)
            .exclude(faculty_id__isnull=True).exclude(faculty_id='')
            .values_list('faculty_id', flat=True).distinct()
        )
        faculty_ids = []
        for fid in raw_faculty_ids:
            try:
                faculty_ids.append(uuid.UUID(str(fid)))
            except (AttributeError, TypeError, ValueError):
                pass
        faculty_objs = UserAdmin.objects.filter(id__in=faculty_ids, isActive=True).order_by('first_name', 'last_name')

        data = []
        for f in faculty_objs:
            full_name = f"{f.first_name or ''} {f.last_name or ''}".strip()
            data.append({
                "id": str(f.id),
                "name": full_name,
                "email": f.email or "",
                "employee_code": f.employee_code or "",
                "department_id": f.department_id,
            })

        response_ = {"n": 1, "msg": "Faculty list found successfully", "data": data}
        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


class LocationDropdown(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        if template_id in (None, ''):
            response_ = {"n": 0, "msg": "template_id not provided", "data": []}
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        room_numbers = list(
            TimetableSlot.objects.filter(timetable_template_id=template_id, is_active=True)
            .exclude(room_number__isnull=True).exclude(room_number='')
            .values_list('room_number', flat=True).distinct()
        )

        data = [{"id": i + 1, "name": rn} for i, rn in enumerate(room_numbers)]
        response_ = {"n": 1, "msg": "Location list found successfully", "data": data}
        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


class UpdateSchedule(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 
        
        
        course_ids=list(json.loads(request_data.get('course_ids')))
        if course_ids is None or course_ids =='':
            msg="Please provide course ids"
            validation_status=False 

        request_data['course_ids']=course_ids
        college_ids=json.loads(request_data.get('college_ids'))
        if college_ids is None or college_ids =='':
            msg="Please provide college ids"
            validation_status=False 
            
        request_data['college_ids']=college_ids


        start_date=request_data.get('start_date')
        if start_date is None or start_date =='':
            msg="Please provide schedule start date "
            validation_status=False 
            
            
            
        end_date=request_data.get('end_date')
        if end_date is None or end_date =='':
            msg="Please provide schedule end date "
            validation_status=False 
            
            
        start_time=request_data.get('start_time')
        if start_time is None or start_time =='':
            msg="Please provide schedule start time "
            validation_status=False 
            
        end_time=request_data.get('end_time')
        if end_time is None or end_time =='':
            msg="Please provide schedule end time "
            validation_status=False 
            
        max_capacity=request_data.get('max_capacity')
        if max_capacity is None or max_capacity =='':
            msg="Please provide schedule max capacity "
            validation_status=False 
            
        # branch_id=request_data.get('branch_id')
        # if branch_id is None or branch_id =='':
        #     msg="Please provide branch id"
        #     validation_status=False 
            
        mode=request_data.get('mode')
        if mode is None or mode =='':
            msg="Please provide mode"
            validation_status=False 
        
        
        schedulename=request_data.get('schedulename')
        if schedulename is None or schedulename =='':
            msg="Please provide schedule name"
            validation_status=False 
        already_exists_schedule=Schedule.objects.filter(start_date=start_date,end_date=end_date,course_ids__in=course_ids,mode=mode,isActive=True).exclude(id=schedule_id).first()
        if already_exists_schedule is not None:
            msg="Schedule for this date range  is already exists"
            validation_status=False 



        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True).first()
            if schedule_obj is not None:
                
                
                serializer=ScheduleSerializer(schedule_obj,data=request_data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                
                    
                    response_={
                            "n": 1,
                            "msg": 'Schedule updated successfully',
                            "data":''                     
                        }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    response_={
                                "n": 0,
                                "msg": first_key+' : '+ first_value[0],
                                "data":serializer.errors                    
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class DeleteSchedule(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 
        

            
               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True).first()
            if schedule_obj is not None:
                
                data['isActive']=False
                serializer=ScheduleSerializer(schedule_obj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                
                    
                    response_={
                            "n": 1,
                            "msg": 'Schedule deleted successfully',
                            "data":''                     
                        }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    response_={
                                "n": 0,
                                "msg": first_key+' : '+ first_value[0],
                                "data":serializer.errors                    
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class GetScheduleById(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 

               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True).first()
            if schedule_obj is not None:
                
                serializer=ScheduleSerializer(schedule_obj)
  
                response_={
                        "n": 1,
                        "msg": 'Schedule found successfully',
                        "data":serializer.data                     
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class ScheduleFilterApi(GenericAPIView):
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
        
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        
        member_type = adminobj.user_type
        if adminobj.member_of is None :
            member_of = str(adminobj.id)
        else:
            member_of = str(adminobj.member_of)
        
        schedule_objs=Schedule.objects.filter(college_ids=member_of,isActive=True).exclude(action_status='Decline')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        
        branch_id=request_data.get('branch_id')
        if branch_id is not None and branch_id !='':
            schedule_objs=schedule_objs.filter(branch_id=branch_id) 
        
        faculty_id=request_data.get('faculty_id')
        if faculty_id is not None and faculty_id !='':
            schedule_objs=schedule_objs.filter(faculty_id=faculty_id) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 

        status=request_data.get('status')
        if status is not None and status !='':
            now = datetime.now().time()  # Get the current time

            for schedule in schedule_objs:
                # Parse the start and end times from the schedule
                start_time = datetime.strptime(schedule.start_time, "%H:%M").time() if schedule.start_time else None
                end_time = datetime.strptime(schedule.end_time, "%H:%M").time() if schedule.end_time else None

                if status == "Upcoming":
                    # Check if the current time is before the start time
                    if start_time and now < start_time:
                        schedule_objs = schedule_objs.filter(id=schedule.id)

                elif status == "Ongoing":
                    # Check if the current time is between start and end times
                    if start_time and end_time and start_time <= now <= end_time:
                        schedule_objs = schedule_objs.filter(id=schedule.id)

                elif status == "Completed":
                    # Check if the current time is after the end time
                    if end_time and now > end_time:
                        schedule_objs = schedule_objs.filter(id=schedule.id)


        if schedule_objs.exists():
            page4 = self.paginate_queryset(schedule_objs)

            serializer=CustomScheduleSerializer(page4,many=True)

            response_={
                    "n": 1,
                    "msg": 'Schedule found successfully',
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
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    



class ScheduleCalenderEvents(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = request.headers.get("encrypted", "")
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        schedule_objs = Schedule.objects.filter(isActive=True,college_ids__in=[str(request.user.id)])

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            # schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 








        if schedule_objs.exists():
            # Serialize schedules and format for calendar
            events = []
            for schedule in schedule_objs:
                serializer=CustomScheduleSerializer(schedule)

                dates_range = get_dates_from_range(serializer.data['start_date'], serializer.data['end_date'])
                for date_str in dates_range:
                    start_dt = datetime.strptime(f"{date_str}", "%Y-%m-%d")
                    end_dt = datetime.strptime(f"{date_str}", "%Y-%m-%d")
                    
                    # Corrected time comparison - add day only when start_time > end_time
                    if schedule.start_time > schedule.end_time:
                        end_dt += timedelta(days=1)
                    
                    event = {
                        "id": schedule.id,
                        "title": f"{serializer.data['schedulename']}  - {', '.join(serializer.data['college_names'])} - {', '.join(serializer.data['course_names'])} - {serializer.data['faculty_name']}",
                        "start": str(start_dt).split(' ')[0],  # Using isoformat for standard datetime string
                        "end": str(end_dt).split(' ')[0],
                        "allDay": not (schedule.start_time and schedule.end_time),  # Simplified allDay logic
                        "startTime": schedule.start_time,
                        "endTime": schedule.end_time,
                        "status": self.get_schedule_status(schedule),
                        "maxCapacity": schedule.max_capacity,
                        "date": date_str  # Adding original date for reference
                    }
                    events.append(event)

            response_ = {
                "n": len(events),
                "msg": "Schedule events fetched successfully",
                "data": events,
            }

            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)
        else:
            response_ = {
                "n": 0,
                "msg": "No schedule events found",
                "data": [],
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

    def get_schedule_status(self, schedule):
        now = datetime.now()
        if schedule.start_date and schedule.end_date:
            if schedule.start_date > now.date():
                return "Upcoming"
            elif schedule.end_date < now.date():
                return "Completed"
            elif schedule.start_date <= now.date() <= schedule.end_date:
                if schedule.start_time and schedule.end_time:
                    try:
                        start_time = datetime.strptime(schedule.start_time, "%H:%M").time()
                        end_time = datetime.strptime(schedule.end_time, "%H:%M").time()
                        if start_time <= now.time() <= end_time:
                            return "Ongoing"
                        elif now.time() < start_time:
                            return "Upcoming"
                        else:
                            return "Completed"
                    except ValueError:
                        return "Invalid Time Format"
                return "Ongoing"
        return "No Schedule"


class FilterFacultySchedulePendingRequestsListApi(GenericAPIView):
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
        
        
        schedule_objs=Schedule.objects.filter(isActive=True,faculty_id=str(request.user.id),action_status='Pending')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            # 'branch_id': request_data.get('branch_id'),
            # 'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 




        # status=request_data.get('status')
        # if status is not None and status !='':
        #     now = datetime.now().time()  # Get the current time

        #     for schedule in schedule_objs:
        #         # Parse the start and end times from the schedule
        #         start_time = datetime.strptime(schedule.start_time, "%H:%M").time() if schedule.start_time else None
        #         end_time = datetime.strptime(schedule.end_time, "%H:%M").time() if schedule.end_time else None

        #         if status == "Upcoming":
        #             # Check if the current time is before the start time
        #             if start_time and now < start_time:
        #                 schedule_objs = schedule_objs.filter(id=schedule.id)

        #         elif status == "Ongoing":
        #             # Check if the current time is between start and end times
        #             if start_time and end_time and start_time <= now <= end_time:
        #                 schedule_objs = schedule_objs.filter(id=schedule.id)

        #         elif status == "Completed":
        #             # Check if the current time is after the end time
        #             if end_time and now > end_time:
        #                 schedule_objs = schedule_objs.filter(id=schedule.id)


        if schedule_objs.exists():
            page4 = self.paginate_queryset(schedule_objs)

            serializer=CustomScheduleSerializer(page4,many=True)
            
            response_={
                    "n": 1,
                    "msg": 'Schedule found successfully',
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
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    

class FilterFacultyScheduleApprovedRequestsListApi(GenericAPIView):
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
        
        
        schedule_objs=Schedule.objects.filter(isActive=True,faculty_id=str(request.user.id),action_status='Approved')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            # 'branch_id': request_data.get('branch_id'),
            # 'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 




        # status=request_data.get('status')
        # if status is not None and status !='':
        #     now = datetime.now().time()  # Get the current time

        #     for schedule in schedule_objs:
        #         # Parse the start and end times from the schedule
        #         start_time = datetime.strptime(schedule.start_time, "%H:%M").time() if schedule.start_time else None
        #         end_time = datetime.strptime(schedule.end_time, "%H:%M").time() if schedule.end_time else None

        #         if status == "Upcoming":
        #             # Check if the current time is before the start time
        #             if start_time and now < start_time:
        #                 schedule_objs = schedule_objs.filter(id=schedule.id)

        #         elif status == "Ongoing":
        #             # Check if the current time is between start and end times
        #             if start_time and end_time and start_time <= now <= end_time:
        #                 schedule_objs = schedule_objs.filter(id=schedule.id)

        #         elif status == "Completed":
        #             # Check if the current time is after the end time
        #             if end_time and now > end_time:
        #                 schedule_objs = schedule_objs.filter(id=schedule.id)


        if schedule_objs.exists():
            page4 = self.paginate_queryset(schedule_objs)

            serializer=CustomScheduleSerializer(page4,many=True)

            response_={
                    "n": 1,
                    "msg": 'Schedule found successfully',
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
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    

class FilterFacultyScheduleDeclineRequestsListApi(GenericAPIView):
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
        
        
        schedule_objs=Schedule.objects.filter(isActive=True,faculty_id=str(request.user.id),action_status='Decline')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters


        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            # 'branch_id': request_data.get('branch_id'),
            # 'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        

        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 





        if schedule_objs.exists():
            page4 = self.paginate_queryset(schedule_objs)

            serializer=CustomScheduleSerializer(page4,many=True)

            response_={
                    "n": 1,
                    "msg": 'Schedule found successfully',
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
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    

class ApproveScheduleRequest(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 
        

            
               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True).first()
            if schedule_obj is not None:
                
                data['action_status']='Approved'
                serializer=ScheduleSerializer(schedule_obj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                
                    
                    response_={
                            "n": 1,
                            "msg": 'Schedule approved successfully',
                            "data":''                     
                        }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    response_={
                                "n": 0,
                                "msg": first_key+' : '+ first_value[0],
                                "data":serializer.errors                    
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class DeclineScheduleRequest(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 
        decline_reason=request_data.get('decline_reason')
        if decline_reason is None or decline_reason =='':
            msg="Please provide schedule decline reason"
            validation_status=False 

               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True).first()
            if schedule_obj is not None:
                data['action_status']='Decline'
                data['decline_reason']=data['decline_reason']
                serializer=ScheduleSerializer(schedule_obj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                
                    
                    response_={
                            "n": 1,
                            "msg": 'Schedule decline successfully',
                            "data":''                     
                        }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    response_={
                                "n": 0,
                                "msg": first_key+' : '+ first_value[0],
                                "data":serializer.errors                    
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class RescheduleRequest(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 

        new_start_date=request_data.get('new_start_date')
        if new_start_date is None or new_start_date =='':
            msg="Please provide schedule new start date"
            validation_status=False 

        new_end_date=request_data.get('new_end_date')
        if new_end_date is None or new_end_date =='':
            msg="Please provide schedule new end date"
            validation_status=False 

        reschedule_reason=request_data.get('reschedule_reason')
        if reschedule_reason is None or reschedule_reason =='':
            msg="Please provide reschedule reason"
            validation_status=False 



               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True).first()
            old_start_date=schedule_obj.start_date
            old_end_date=schedule_obj.end_date
            if schedule_obj is not None:
                data['action_status']='Approved'
                data['start_date']=new_start_date
                data['end_date']=new_end_date
                serializer=ScheduleSerializer(schedule_obj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    RescheduleLog.objects.create(
                        schedule_id=serializer.data['id'],
                        old_start_date=old_start_date,
                        old_end_date=old_end_date,
                        old_start_time=serializer.data['start_time'],
                        old_end_time=serializer.data['end_time'],
                        new_start_date=new_start_date,
                        new_end_date=new_end_date,
                        new_start_time=serializer.data['start_time'],
                        new_end_time=serializer.data['end_time'],
                        reschedule_reason=reschedule_reason,
                        )
                    
                    response_={
                            "n": 1,
                            "msg": 'Schedule reschedule successfully',
                            "data":''                     
                        }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    first_key, first_value = next(iter(serializer.errors.items()))
                    response_={
                                "n": 0,
                                "msg": first_key+' : '+ first_value[0],
                                "data":serializer.errors                    
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class FacultyCurrentScheduleFilterApi(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def expand_schedule_objects(self, schedule_objs):
        """Expand schedule objects to unique college_id and course_id combinations"""
        expanded_schedules = []

        for schedule in schedule_objs:
            branch = Branch.objects.filter(id=schedule.branch_id, isActive=True).values('name').first()
            branch_name = branch['name'] if branch else None  # Extract name safely

            for college in schedule.college_ids.all():
                for course in schedule.course_ids.all():
                    start_time = (
                        datetime.strptime(schedule.start_time, "%H:%M").strftime("%I:%M %p")
                        if schedule.start_time else "N/A"
                    )
                    end_time = (
                        datetime.strptime(schedule.end_time, "%H:%M").strftime("%I:%M %p")
                        if schedule.end_time else "N/A"
                    )

                    expanded_schedules.append({
                        "id": schedule.id,
                        "schedulename": schedule.schedulename,
                        "college_id": college.id,
                        "college_name": college.name,
                        "course_id": course.id,
                        "course_name": course.course_name,
                        "mode": schedule.mode,
                        "formatted_start_date": schedule.start_date.strftime("%d %B, %Y") if schedule.start_date else None,
                        "formatted_end_date": schedule.end_date.strftime("%d %B, %Y") if schedule.end_date else None,
                        "formatted_time": f"{start_time} - {end_time}",
                        "branch_name": branch_name,  # Fixed branch name retrieval
                    })

        return expanded_schedules


    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        schedule_objs=Schedule.objects.filter(isActive=True).exclude(action_status='Decline')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        
        branch_id=request_data.get('branch_id')
        if branch_id is not None and branch_id !='':
            schedule_objs=schedule_objs.filter(branch_id=branch_id) 
        
        faculty_id=str(request.user.id)
        if faculty_id is not None and faculty_id !='':
            schedule_objs=schedule_objs.filter(faculty_id=faculty_id) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 

        status='Ongoing'
        if status is not None and status !='':
            now = datetime.now().time()  # Get the current time
            schedule_objs = schedule_objs.filter(start_time__lte=now, end_time__gte=now)



        if schedule_objs.exists():
            expanded_schedule_objs = self.expand_schedule_objects(schedule_objs)
            page4 = self.paginate_queryset(expanded_schedule_objs)
            serializer=UniqueScheduleSerializer(page4,many=True)
            response_={
                    "n": 1,
                    "msg": 'Schedule found successfully',
                    "data":serializer.data                     
                }



            if encryped_header == "1" :
                paigna=self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                paigna=self.get_paginated_response(serializer.data)

                return Response(paigna,status=200)
        else:
            response_={
                        "count":0,
                        "next":None,
                        "previous":None,
                        "n": 0,
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
   


class FacultyUpcomingScheduleFilterApi(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def expand_schedule_objects(self, schedule_objs):
        """Expand schedule objects to unique college_id and course_id combinations"""
        expanded_schedules = []

        for schedule in schedule_objs:
            branch = Branch.objects.filter(id=schedule.branch_id, isActive=True).values('name').first()
            branch_name = branch['name'] if branch else None  # Extract name safely

            for college in schedule.college_ids.all():
                for course in schedule.course_ids.all():
                    start_time = (
                        datetime.strptime(schedule.start_time, "%H:%M").strftime("%I:%M %p")
                        if schedule.start_time else "N/A"
                    )
                    end_time = (
                        datetime.strptime(schedule.end_time, "%H:%M").strftime("%I:%M %p")
                        if schedule.end_time else "N/A"
                    )

                    expanded_schedules.append({
                        "id": schedule.id,
                        "schedulename": schedule.schedulename,
                        "college_id": college.id,
                        "college_name": college.name,
                        "course_id": course.id,
                        "course_name": course.course_name,
                        "mode": schedule.mode,
                        "formatted_start_date": schedule.start_date.strftime("%d %B, %Y") if schedule.start_date else None,
                        "formatted_end_date": schedule.end_date.strftime("%d %B, %Y") if schedule.end_date else None,
                        "formatted_time": f"{start_time} - {end_time}",
                        "branch_name": branch_name,  # Fixed branch name retrieval
                    })

        return expanded_schedules


    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        
        if error_response:
            return error_response
        
        
        schedule_objs=Schedule.objects.filter(isActive=True).exclude(action_status='Decline')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        
        branch_id=request_data.get('branch_id')
        if branch_id is not None and branch_id !='':
            schedule_objs=schedule_objs.filter(branch_id=branch_id) 
        
        faculty_id=request.user.id
        if faculty_id is not None and faculty_id !='':
            schedule_objs=schedule_objs.filter(faculty_id=faculty_id) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 

        status='Upcoming'
        if status is not None and status !='':
            now = datetime.now().time()  # Get the current time
            schedule_objs = schedule_objs.filter(start_time__gte=now, end_time__gte=now)



        if schedule_objs.exists():
            expanded_schedule_objs = self.expand_schedule_objects(schedule_objs)
            page4 = self.paginate_queryset(expanded_schedule_objs)
            serializer=UniqueScheduleSerializer(page4,many=True)
            response_={
                    "count":0,
                    "next":None,
                    "previous":None,
                    "n": 1,
                    "msg": 'Schedule found successfully',
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
                        "count":0,
                        "next":None,
                        "previous":None,
                        "n": 0,
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
   


class FacultyPreviousScheduleFilterApi(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def expand_schedule_objects(self, schedule_objs):
        """Expand schedule objects to unique college_id and course_id combinations"""
        expanded_schedules = []

        for schedule in schedule_objs:
            branch = Branch.objects.filter(id=schedule.branch_id, isActive=True).values('name').first()
            branch_name = branch['name'] if branch else None  # Extract name safely

            for college in schedule.college_ids.all():
                for course in schedule.course_ids.all():
                    start_time = (
                        datetime.strptime(schedule.start_time, "%H:%M").strftime("%I:%M %p")
                        if schedule.start_time else "N/A"
                    )
                    end_time = (
                        datetime.strptime(schedule.end_time, "%H:%M").strftime("%I:%M %p")
                        if schedule.end_time else "N/A"
                    )

                    expanded_schedules.append({
                        "id": schedule.id,
                        "schedulename": schedule.schedulename,
                        "college_id": college.id,
                        "college_name": college.name,
                        "course_id": course.id,
                        "course_name": course.course_name,
                        "mode": schedule.mode,
                        "formatted_start_date": schedule.start_date.strftime("%d %B, %Y") if schedule.start_date else None,
                        "formatted_end_date": schedule.end_date.strftime("%d %B, %Y") if schedule.end_date else None,
                        "formatted_time": f"{start_time} - {end_time}",
                        "branch_name": branch_name,  # Fixed branch name retrieval
                    })

        return expanded_schedules


    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        
        if error_response:
            return error_response
        
        
        schedule_objs=Schedule.objects.filter(isActive=True).exclude(action_status='Decline')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'college_ids__in': [request_data.get('colleges')] if request_data.get('colleges') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        college_id=request_data.get('colleges')
        if college_id is not None and college_id !='':
            schedule_objs=schedule_objs.filter(college_ids__in=[college_id]) 
        
        
        branch_id=request_data.get('branch_id')
        if branch_id is not None and branch_id !='':
            schedule_objs=schedule_objs.filter(branch_id=branch_id) 
        
        faculty_id=request.user.id
        if faculty_id is not None and faculty_id !='':
            schedule_objs=schedule_objs.filter(faculty_id=faculty_id) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            schedule_objs=schedule_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
        
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            schedule_objs=schedule_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 

        status='Completed'
        if status is not None and status !='':
            now = datetime.now().time()  # Get the current time
            schedule_objs = schedule_objs.filter(start_time__lte=now, end_time__lte=now)



        if schedule_objs.exists():
            expanded_schedule_objs = self.expand_schedule_objects(schedule_objs)
            page4 = self.paginate_queryset(expanded_schedule_objs)
            serializer=UniqueScheduleSerializer(page4,many=True)
            response_={
                    "count":0,
                    "next":None,
                    "previous":None,
                    "n": 1,
                    "msg": 'Schedule found successfully',
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
                        "count":0,
                        "next":None,
                        "previous":None,
                        "n": 0,
                        "msg": 'schedule not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
   

def format_time(time_str):
    try:
        # Try parsing as HH:MM:SS
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        try:
            # Try parsing as HH:MM
            time_obj = datetime.strptime(time_str, "%H:%M")
        except ValueError:
            try:
                # Try parsing as H:M:S (handling single-digit hours)
                time_obj = datetime.strptime(time_str, "%I:%M:%S")
            except ValueError:
                return "Invalid Time Format"
    
    return time_obj.strftime("%H:%M:%S")  #

class GetScheduleAttendance(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 

        schedule_date=request_data.get('schedule_date')
        if schedule_date is None or schedule_date =='':
            msg="Please provide schedule date"
            validation_status=False 

        course_id=request_data.get('course_id')
        # if course_id is None or course_id =='':
        #     msg="Please provide course id"
        #     validation_status=False 

        college_id=request_data.get('college_id')
        # if college_id is None or college_id =='':
            # msg="Please provide college id"
            # validation_status=False 
        faculty_id=str(request.user.id)


               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True,)
            if course_id is not None and course_id !='':
                schedule_obj=schedule_obj.filter(course_ids=course_id,).first()
            else:
                schedule_obj=schedule_obj.first()

                

            if schedule_obj is not None:
                serializer=CustomScheduleSerializer(schedule_obj)
                new_serializer=serializer.data

                if course_id is None or course_id =='':
                    course_id=new_serializer['course_ids'][0]

                if college_id is None or college_id =='':
                    college_id=new_serializer['college_ids'][0]

                schedule_list_obj=Schedule.objects.filter(faculty_id=faculty_id,start_date__lte=schedule_date,end_date__gte=schedule_date,isActive=True).exclude(action_status="Decline")
                schedule_list_serializer=CustomScheduleSerializer(schedule_list_obj,many=True)
                

                candidate_ids=list(Enrollments.objects.filter(course=course_id,schedule=serializer.data['id'],isActive=True).order_by('candidate').distinct("candidate").values_list('candidate',flat=True))

                candidate_objs=Candidate.objects.filter(id__in=candidate_ids,isActive=True)
                candidate_serializer=CandidateSerializer(candidate_objs,many=True)
                schedule_attendance=[]
                for candidate in candidate_serializer.data:
                    candidate['candidate_name']=candidate['first_name']+' '+candidate['middle_name']+' '+candidate['last_name']

                    attendance_obj=CandidateAttendance.objects.filter(candidate_id=candidate['id'],schedule_id=serializer.data['id'],course_id=course_id,college_id=college_id,faculty_id=faculty_id,attendance_date=schedule_date).first()
                    candidate['checkin_time']=''
                    candidate['checkout_time']=''
                    candidate['absent']=False

                    if attendance_obj is not None:
                        candidate['checkin_time']=attendance_obj.checkin_time
                        candidate['checkout_time']=attendance_obj.checkout_time
                        candidate['absent']=attendance_obj.absent
                    

                    candidate['course_id']=course_id
                    candidate['college_id']=college_id

                    schedule_attendance.append(candidate)

                response_={
                        "n": 1,
                        "msg": 'Schedule attendance found successfully',
                        "data":{
                            "schedule":new_serializer,
                            "schedule_list":schedule_list_serializer.data,
                            "schedule_attendance":schedule_attendance
                        }                     
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":{}                    
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class GetScheduleCandidatesAttendance(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        validation_status=True
        data=request_data.copy()

        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id"
            validation_status=False 



        course_id=request_data.get('course_id')
        if course_id is None or course_id =='':
            msg="Please provide course id"
            validation_status=False 

        college_id=request_data.get('college_id')
        if college_id is None or college_id =='':
            msg="Please provide college id"
            validation_status=False 
        faculty_id=str(request.user.id)

               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True,
                    # college_ids__in=[str(college_id)],course_ids__in=[course_id]
                                                 ).first()

            if schedule_obj is not None:
                serializer=CustomScheduleSerializer(schedule_obj)
                new_serializer=serializer.data
                new_serializer['total_days']=calculate_days_difference(new_serializer['start_date'],new_serializer['end_date'])
                candidate_ids=list(Enrollments.objects.filter(course=course_id,schedule=serializer.data['id'],isActive=True).order_by('candidate').distinct("candidate").values_list('candidate',flat=True))

                new_serializer['college_name']=''
                # college_obj = UserAdmin.objects.filter(id=str(college_id), isActive=True).values('name').first()
                # new_serializer['college_name'] = college_obj['name'] if college_obj else None  # Extract name safely

                course_obj = Course.objects.filter(id=course_id, isActive=True).values('course_name').first()
                new_serializer['course_name'] = course_obj['course_name'] if course_obj else None  # Extract name safely

                candidate_objs=Candidate.objects.filter(id__in=candidate_ids,isActive=True)
                candidate_serializer=CandidateSerializer(candidate_objs,many=True)
                schedule_attendance=[]

                sum_of_attendance=0

                for candidate in candidate_serializer.data:
                    candidate['candidate_name']=candidate['first_name']+' '+candidate['middle_name']+' '+candidate['last_name']
                    candidate['course_id']=course_id
                    candidate['college_id']=college_id
                    candidate['total_days']=new_serializer['total_days']
                    


                    candidate['country_name'] = ""
                    if candidate['country'] is not None and candidate['country'] != "":
                        country_object = Country.objects.filter(id=candidate['country']).first()
                        if country_object is not None:
                            candidate['country_name'] = country_object.name
  

                    candidate['state_name'] = ""

                    if candidate['state'] is not None and candidate['state'] != "":
                        state_object = State.objects.filter(id=candidate['state']).first()
                        if state_object is not None:
                            candidate['state_name'] = state_object.name
           






                    
                    candidate['present_count']=CandidateAttendance.objects.filter(candidate_id=candidate['id'],schedule_id=serializer.data['id'],course_id=course_id,college_id=college_id,faculty_id=faculty_id,attendance_date__gte=new_serializer['start_date'],attendance_date__lte=new_serializer['end_date']).exclude(absent=True).count()
                    sum_of_attendance+=int(candidate['present_count'])

                    schedule_attendance.append(candidate)
                new_serializer['Average_Class_Attendance']=round(int(sum_of_attendance)/int(new_serializer['total_days']))

                response_={
                        "n": 1,
                        "msg": 'Schedule attendance found successfully',
                        "data":{
                            "schedule":new_serializer,
                            "schedule_attendance":schedule_attendance
                        }                     
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
                            "msg": 'schedule not found',
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
                        "msg": msg,
                        "data":{}                    
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class ClassListByCourse(GenericAPIView):
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        return self._list_classes(request, request_data)

    def _list_classes(self, request, request_data):
        encryped_header = ""

        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        course_id = request_data.get('course_id')

        if course_id is None or course_id == "":
            response_ = {
                "n": 0,
                "msg": "Course id is required.",
                "data": {}
            }
            return self._respond(response_, encryped_header)

        course_obj = Course.objects.filter(
            id=course_id,
            isActive=True
        ).first()

        if course_obj is None:
            response_ = {
                "n": 0,
                "msg": "Course not found.",
                "data": {}
            }
            return self._respond(response_, encryped_header)

        mapped_class_ids = CourseClass.objects.filter(
            course_id=course_id,
            isActive=True
        ).values_list('class_id', flat=True)

        if not mapped_class_ids:
            response_ = {
                "n": 1,
                "msg": "No classes found for the course.",
                "data": []
            }
            return self._respond(response_, encryped_header)

        class_group_obj = ClassGroup.objects.filter(
            id__in=mapped_class_ids,
            isActive=True
        )

        semester_id = request_data.get(
            'semester_id'
        )

        if semester_id is not None and semester_id != "":
            class_group_obj = class_group_obj.filter(
                semester_ids__contains=[int(semester_id)]
            )

        class_group_obj = class_group_obj.order_by(
            'class_name',
            'division'
        )

        serializer = ClassGroupSerializer(
            class_group_obj,
            many=True
        )

        class_group_data = serializer.data
        semester_ids_all = set()
        for item in class_group_data:
            raw_ids = item.get('semester_ids') or []
            for sid in raw_ids:
                semester_ids_all.add(int(sid))

        semester_map = {
            obj.id: obj for obj in Semester.objects.filter(
                id__in=semester_ids_all, isActive=True
            )
        }

        for item in class_group_data:
            item['course_id'] = course_obj.id
            item['course_name'] = course_obj.course_name
            item['course_code'] = course_obj.course_code

            item['academic_year_id'] = None
            item['academic_year_name'] = ""

            item['department_id'] = None
            item['department_name'] = ""
            item['department_code'] = ""

            raw_ids = item.get('semester_ids') or []
            semester_items = []
            for sid in raw_ids:
                semester_obj = semester_map.get(int(sid))
                if semester_obj is not None:
                    semester_items.append({
                        'semester_id': semester_obj.id,
                        'semester_name': semester_obj.semester_name,
                        'semester_number': semester_obj.semester_number,
                    })
            item['semester_list'] = semester_items

        response_ = {
            "n": 1,
            "msg": "Classes found successfully.",
            "data": class_group_data
        }

        return self._respond(response_, encryped_header)

    def _respond(self, response_, encryped_header):
        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(
                response_
            )
            encdata = encrypt_data(
                json.dumps(data_to_serialize)
            )
            return Response(encdata, status=200)

        return Response(response_, status=200)


class TimetableTemplateListByYearSemester(GenericAPIView):
    """
    API endpoint to list timetable templates filtered by academic year and semester.
    
    POST /api/schedule/timetable-template-list/
    
    Request Body:
    {
        "academic_year_id": 1,  # Required
        "semester_id": 1        # Required
    }
    
    Response:
    {
        "n": 1,
        "msg": "Templates retrieved successfully",
        "data": [
            {
                "id": 1,
                "template_name": "Template 1",
                "class_name": "F.Y.B.Sc.",
                "total_lectures": 7,
                "created_by_name": "Mr. Satyavan M. Kunjir",
                "created_date": "09/08/2026"
            }
        ]
    }
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        academic_year_id = request_data.get('academic_year_id')
        semester_id = request_data.get('semester_id') or request_data.get('semister_id')
        course_id = request_data.get('course_id')

        # Validate required fields
        if not academic_year_id:
            response_ = {
                "n": 0,
                "msg": "academic_year_id is required",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        if not semester_id:
            response_ = {
                "n": 0,
                "msg": "semester_id is required",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        # Filter timetable templates by year and semester (class group -> semester)
        class_qs = ClassGroup.objects.filter(
            semester_ids__contains=[int(semester_id)],
            isActive=True
        )
        if not class_qs.exists():
            # Fallback: interpret the value as semester_number (e.g. 1 -> first semester)
            try:
                resolved_sem = Semester.objects.filter(semester_number=int(semester_id), isActive=True).first()
                if resolved_sem is not None and int(semester_id) != resolved_sem.id:
                    class_qs = ClassGroup.objects.filter(
                        semester_ids__contains=[resolved_sem.id],
                        isActive=True
                    )
            except (TypeError, ValueError):
                pass

        class_ids = class_qs.values_list('id', flat=True)

        templates_queryset = TimetableTemplate.objects.filter(
            academic_year_id=academic_year_id,
            class_group_id__in=class_ids,
            is_active=True
        ).order_by('-createdAt')

        # Optional course filter: only templates that have at least one slot for this course
        if course_id not in (None, ''):
            slot_template_ids = TimetableSlot.objects.filter(
                course_id=course_id,
                is_active=True
            ).values_list('timetable_template_id', flat=True)
            templates_queryset = templates_queryset.filter(id__in=slot_template_ids)

        if templates_queryset.exists():
            page = self.paginate_queryset(templates_queryset)

            class_group_map = {
                cg.id: cg
                for cg in ClassGroup.objects.filter(
                    id__in={t.class_group_id for t in page},
                    isActive=True
                )
            }
            semester_ids_all = set()
            for cg in class_group_map.values():
                for sid in (cg.semester_ids or []):
                    semester_ids_all.add(int(sid))
            semester_map = {
                s.id: s
                for s in Semester.objects.filter(
                    id__in=semester_ids_all,
                    isActive=True
                )
            }
            creator_ids = {
                t.created_by or t.createdBy for t in page
                if (t.created_by or t.createdBy)
            }
            valid_creator_ids = set()
            for creator_id in creator_ids:
                try:
                    uuid.UUID(str(creator_id))
                except (AttributeError, TypeError, ValueError):
                    continue
                valid_creator_ids.add(str(creator_id))
            user_map = {
                str(u.id): u
                for u in UserAdmin.objects.filter(id__in=valid_creator_ids, isActive=True)
            }
            slot_count_map = {
                row['timetable_template_id']: row['total']
                for row in TimetableSlot.objects.filter(
                    timetable_template_id__in=[t.id for t in page],
                    is_active=True
                ).values('timetable_template_id').annotate(total=Count('id'))
            }

            serializer = TimetableTemplateListSerializer(
                page,
                many=True,
                context={
                    'class_group_map': class_group_map,
                    'semester_map': semester_map,
                    'user_map': user_map,
                    'slot_count_map': slot_count_map,
                }
            )

            response_ = {
                "n": 1,
                "msg": "Templates retrieved successfully",
                "data": serializer.data
            }

            if encryped_header == "1":
                paginated_response = self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paginated_response)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(self.get_paginated_response(serializer.data), status=200)
        else:
            response_ = {
                "n": 1,
                "msg": "No templates found",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)


class TemplateSlotEdit(GenericAPIView):
    """
    API to edit a single lecture slot of a timetable template by template id, lecture day and lecture no.

    POST /api/schedule/template-edit/

    Request Body:
    {
        "template_id": 1,       # Required
        "lecture_day": 0,       # Required (0 = Monday)
        "lecture_no": 1,        # Required (period number)
        "start_time": "09:00 AM",
        "end_time": "10:00 AM",
        "course_id": 9,
        "faculty_id": "1",
        "room_number": "101",
        "entry_for": "lecture",
        "lecture_type": "THEORY"
    }

    Response:
    {
        "n": 1,
        "msg": "Template lecture updated successfully",
        "data": { ...updated slot... }
    }
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        lecture_day = request_data.get('lecture_day')
        lecture_no = request_data.get('lecture_no')

        msg = ''
        validation_status = True

        if template_id in (None, ''):
            msg = 'template_id is required'
            validation_status = False
        if lecture_day in (None, ''):
            msg = 'lecture_day is required'
            validation_status = False
        if lecture_no in (None, ''):
            msg = 'lecture_no is required'
            validation_status = False

        try:
            lecture_day = int(lecture_day)
            lecture_no = int(lecture_no)
        except (TypeError, ValueError):
            msg = 'lecture_day and lecture_no must be integers'
            validation_status = False

        if validation_status and not (0 <= lecture_day <= 6):
            msg = 'lecture_day must be between 0 and 6'
            validation_status = False

        if validation_status and lecture_no < 1:
            msg = 'lecture_no must be a positive integer'
            validation_status = False

        if not validation_status:
            response_ = {
                "n": 0,
                "msg": msg,
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        if not TimetableTemplate.objects.filter(id=template_id, isActive=True).exists():
            response_ = {
                "n": 0,
                "msg": "Template not found",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        slot_obj = TimetableSlot.objects.filter(
            timetable_template_id=template_id,
            day_of_week=lecture_day,
            period_number=lecture_no
        ).first()

        if slot_obj is None:
            response_ = {
                "n": 0,
                "msg": "Lecture not found for this template",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        editable_fields = ['start_time', 'end_time', 'course_id', 'faculty_id', 'room_number', 'entry_for', 'lecture_type']
        for field in editable_fields:
            if field in request_data and request_data[field] not in (None, ''):
                setattr(slot_obj, field, request_data[field])

        slot_obj.updatedAt = timezone.now()
        if request.user:
            slot_obj.updatedBy = str(request.user.id)
        slot_obj.save()

        response_ = {
            "n": 1,
            "msg": "Template lecture updated successfully",
            "data": {
                "id": slot_obj.id,
                "template_id": slot_obj.timetable_template_id,
                "lecture_day": slot_obj.day_of_week,
                "lecture_no": slot_obj.period_number,
                "start_time": slot_obj.start_time,
                "end_time": slot_obj.end_time,
                "course_id": slot_obj.course_id,
                "faculty_id": slot_obj.faculty_id,
                "room_number": slot_obj.room_number,
                "entry_for": slot_obj.entry_for,
                "lecture_type": slot_obj.lecture_type
            }
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        else:
            return Response(response_, status=200)


class SemesterListByCourse(GenericAPIView):
    """
    API to list semesters of a course with timetable template counts.

    POST /api/schedule/semester-list-by-course

    Request Body:
    {
        "course_id": 2,        # Required
        "academic_year_id": 1   # Optional (template count for a specific year)
    }

    Response:
    {
        "n": 1,
        "msg": "Semester list found successfully",
        "data": [
            {
                "id": 1,
                "semester_name": "Semester I",
                "semester_number": 1,
                "course_id": 2,
                "template_count": 2
            }
        ]
    }
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        course_id = request_data.get('course_id')
        academic_year_id = request_data.get('academic_year_id')

        if course_id in (None, ''):
            response_ = {
                "n": 0,
                "msg": "course_id is required",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        semester_obj = Semester.objects.filter(
            course_id=course_id,
            isActive=True
        ).order_by('semester_number')

        semester_data = []
        for sem in semester_obj:
            class_ids = ClassGroup.objects.filter(
                semester_id=sem.id,
                isActive=True
            ).values_list('id', flat=True)

            template_qs = TimetableTemplate.objects.filter(
                class_group_id__in=class_ids,
                is_active=True
            )
            if academic_year_id not in (None, ''):
                template_qs = template_qs.filter(
                    academic_year_id=academic_year_id
                )

            semester_data.append({
                "id": sem.id,
                "semester_name": sem.semester_name,
                "semester_number": sem.semester_number,
                "course_id": sem.course_id,
                "template_count": template_qs.count()
            })

        response_ = {
            "n": 1,
            "msg": "Semester list found successfully",
            "data": semester_data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        else:
            return Response(response_, status=200)


class SemesterListByCourse(GenericAPIView):
    """
    API to list semesters of a course based on the course's semester_count
    with timetable template counts.

    Only the first `semester_count` semesters are returned. Example:
    semester_count = 3 -> Semester I, II, III. If semester_count is
    None/0/absent, all semesters of the course's course(s) are returned.

    POST /api/schedule/semester-list-by-course

    Request Body:
    {
        "course_id": 9,         # Required
        "academic_year_id": 1   # Optional (template count for a specific year)
    }

    Response:
    {
        "n": 1,
        "msg": "Semester list found successfully",
        "data": [
            {
                "id": 1,
                "semester_name": "Semester I",
                "semester_number": 1,
                "course_id": 2,
                "template_count": 2
            }
        ]
    }
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        course_id = request_data.get('course_id')
        academic_year_id = request_data.get('academic_year_id')

        if course_id in (None, ''):
            response_ = {
                "n": 0,
                "msg": "course_id is required",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        course_obj = Course.objects.filter(
            id=course_id,
            isActive=True
        ).first()

        if course_obj is None:
            response_ = {
                "n": 0,
                "msg": "Course not found.",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        semester_count = course_obj.semester_count

        class_groups = ClassGroup.objects.filter(
            id__in=CourseClass.objects.filter(
                course_id=course_id,
                isActive=True
            ).values_list('class_id', flat=True),
            isActive=True
        )

        semester_ids = []
        for cg in class_groups:
            for sem_id in (cg.semester_ids or []):
                semester_ids.append(sem_id)
        semester_ids = list(set(semester_ids))

        if not semester_ids:
            response_ = {
                "n": 1,
                "msg": "No semesters found for the course.",
                "data": []
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            else:
                return Response(response_, status=200)

        semester_obj = Semester.objects.filter(
            id__in=semester_ids,
            isActive=True
        ).order_by('semester_number')

        if semester_count:
            semester_obj = semester_obj[:int(semester_count)]

        class_ids_by_semester = {}
        for cg in class_groups:
            for sem_id in (cg.semester_ids or []):
                class_ids_by_semester.setdefault(sem_id, []).append(cg.id)

        semester_data = []
        for sem in semester_obj:
            class_ids = class_ids_by_semester.get(sem.id, [])

            template_qs = TimetableTemplate.objects.filter(
                class_group_id__in=class_ids,
                is_active=True
            )
            if academic_year_id not in (None, ''):
                template_qs = template_qs.filter(
                    academic_year_id=academic_year_id
                )

            semester_data.append({
                "id": sem.id,
                "semester_name": sem.semester_name,
                "semester_number": sem.semester_number,
                "course_id": course_id,
                "template_count": template_qs.count()
            })

        response_ = {
            "n": 1,
            "msg": "Semester list found successfully",
            "data": semester_data
        }

        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        else:
            return Response(response_, status=200)


class TimetableTimeTableByFilters(GenericAPIView):
    """
    Fetch timetable rows by template / academic year / semester / class / course.
    This matches the actual DB schema in schedule.models.TimetableTemplate:
    - academic_year_id
    - class_group_id
    - template_name
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encrypted_header = ""
        if 'encrypted' in request.headers.keys():
            encrypted_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        academic_year_id = request_data.get('academic_year_id')
        semester_id = request_data.get('semester_id') or request_data.get('semister_id')
        class_id = request_data.get('class_id')
        course_id = request_data.get('course_id')

        template_queryset = TimetableTemplate.objects.filter(isActive=True)

        if template_id not in (None, ''):
            template_queryset = template_queryset.filter(id=template_id)
        if academic_year_id not in (None, ''):
            template_queryset = template_queryset.filter(academic_year_id=academic_year_id)
        if semester_id not in (None, ''):
            class_qs = ClassGroup.objects.filter(semester_ids__contains=[int(semester_id)], isActive=True)
            if not class_qs.exists():
                try:
                    resolved_sem = Semester.objects.filter(semester_number=int(semester_id), isActive=True).first()
                    if resolved_sem is not None and int(semester_id) != resolved_sem.id:
                        class_qs = ClassGroup.objects.filter(semester_ids__contains=[resolved_sem.id], isActive=True)
                except (TypeError, ValueError):
                    pass
            class_group_ids = class_qs.values_list('id', flat=True)
            template_queryset = template_queryset.filter(class_group_id__in=list(class_group_ids))
        if class_id not in (None, ''):
            template_queryset = template_queryset.filter(class_group_id=class_id)

        if not template_queryset.exists():
            response_ = {
                "n": 0,
                "msg": "No timetable template found for the given filters",
                "data": []
            }
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        result = []
        templates = list(template_queryset.order_by('-createdAt'))

        class_group_map = {
            cg.id: cg
            for cg in ClassGroup.objects.filter(
                id__in={t.class_group_id for t in templates},
                isActive=True
            )
        }
        semester_ids_all = set()
        for cg in class_group_map.values():
            for sid in (cg.semester_ids or []):
                semester_ids_all.add(int(sid))
        semester_map = {
            s.id: s
            for s in Semester.objects.filter(
                id__in=semester_ids_all,
                isActive=True
            )
        }
        year_map = {
            y.id: y
            for y in AcademicYear.objects.filter(
                id__in={t.academic_year_id for t in templates},
                isActive=True
            )
        }

        slots_qs = TimetableSlot.objects.filter(
            timetable_template_id__in=[t.id for t in templates],
            isActive=True
        ).order_by('day_of_week', 'period_number')
        if course_id not in (None, ''):
            slots_qs = slots_qs.filter(course_id=course_id)

        slot_list = list(slots_qs)

        course_map = {
            c.id: c
            for c in Course.objects.filter(
                id__in={s.course_id for s in slot_list},
                isActive=True
            )
        }

        faculty_ids = set()
        for slot in slot_list:
            if slot.faculty_id in (None, ''):
                continue
            try:
                uuid.UUID(str(slot.faculty_id).strip())
            except (AttributeError, TypeError, ValueError):
                continue
            faculty_ids.add(str(slot.faculty_id))

        user_map = {
            str(u.id): u
            for u in UserAdmin.objects.filter(id__in=faculty_ids, isActive=True)
        }

        def faculty_name(faculty_id):
            if faculty_id in (None, ''):
                return ""
            user = user_map.get(str(faculty_id))
            if user is None:
                return ""
            if getattr(user, 'user_type', None) == 5:
                return f"{user.first_name or ''} {user.last_name or ''}".strip()
            return user.name or ""

        slots_by_template = {}
        for slot in slot_list:
            slots_by_template.setdefault(slot.timetable_template_id, []).append(slot)

        for template_obj in templates:
            class_group = class_group_map.get(template_obj.class_group_id)
            semester_obj = None
            semester_id = None
            if class_group is not None and class_group.semester_ids:
                semester_id = int(class_group.semester_ids[0])
                semester_obj = semester_map.get(semester_id)
            year_obj = year_map.get(template_obj.academic_year_id)

            template_slots = slots_by_template.get(template_obj.id, [])

            slots_by_day = {}
            for slot in template_slots:
                day_index = slot.day_of_week
                if day_index not in slots_by_day:
                    slots_by_day[day_index] = []

                course_obj = course_map.get(slot.course_id)

                slots_by_day[day_index].append({
                    "id": slot.id,
                    "period_number": slot.period_number,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time,
                    "course_id": slot.course_id,
                    "course_name": course_obj.course_name if course_obj else "",
                    "faculty_id": slot.faculty_id,
                    "faculty_name": faculty_name(slot.faculty_id),
                    "entry_for": slot.entry_for,
                    "lecture_type": slot.lecture_type,
                })

            timetable_rows = []
            for day in range(7):
                lectures = slots_by_day.get(day, [])
                timetable_rows.append({
                    "day_of_week": day,
                    "day_name": day_names[day] if 0 <= day < len(day_names) else "",
                    "lectures": lectures
                })

            class_name = ""
            if class_group:
                class_name = " ".join(part for part in [class_group.class_name, class_group.division] if part).strip()

            result.append({
                "template_id": template_obj.id,
                "template_name": template_obj.template_name,
                "academic_year_id": template_obj.academic_year_id,
                "academic_year_name": year_obj.academic_year_name if year_obj else "",
                "semester_id": semester_id,
                "semester_name": semester_obj.semester_name if semester_obj else "",
                "class_id": template_obj.class_group_id,
                "class_name": class_name,
                "slots": timetable_rows,
                "total_lectures": sum(len(v) for v in slots_by_day.values())
            })

        response_ = {
            "n": 1,
            "msg": "Timetable found successfully",
            "data": result[0] if len(result) == 1 else result
        }

        if encrypted_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


class TemplateDetails(GenericAPIView):
    """Backward-compatible template detail API using actual DB fields."""
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encrypted_header = ""
        if 'encrypted' in request.headers.keys():
            encrypted_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_id = request_data.get('template_id')
        if template_id in (None, ''):
            response_ = {"n": 0, "msg": "template_id is required", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        template_obj = TimetableTemplate.objects.filter(id=template_id, isActive=True).first()
        if template_obj is None:
            response_ = {"n": 0, "msg": "Template not found", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        class_group = ClassGroup.objects.filter(id=template_obj.class_group_id, isActive=True).first()
        class_semester_id = None
        if class_group is not None and class_group.semester_ids:
            class_semester_id = class_group.semester_ids[0]
        semester_obj = None
        if class_semester_id is not None:
            semester_obj = Semester.objects.filter(id=class_semester_id, isActive=True).first()
        year_obj = AcademicYear.objects.filter(id=template_obj.academic_year_id, isActive=True).first()

        class_name = ""
        if class_group:
            class_name = " ".join(part for part in [class_group.class_name, class_group.division] if part).strip()

        slots_qs = TimetableSlot.objects.filter(timetable_template_id=template_obj.id, isActive=True).order_by('day_of_week', 'period_number')
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_map = {idx: [] for idx in range(7)}

        slot_list = list(slots_qs)

        course_map = {
            c.id: c
            for c in Course.objects.filter(
                id__in={s.course_id for s in slot_list},
                isActive=True
            )
        }

        faculty_ids = set()
        for slot in slot_list:
            if slot.faculty_id in (None, ''):
                continue
            try:
                uuid.UUID(str(slot.faculty_id).strip())
            except (AttributeError, TypeError, ValueError):
                continue
            faculty_ids.add(str(slot.faculty_id))

        user_map = {
            str(u.id): u
            for u in UserAdmin.objects.filter(id__in=faculty_ids, isActive=True)
        }

        for slot in slot_list:
            course_obj = course_map.get(slot.course_id)
            faculty_name = ""
            user = user_map.get(str(slot.faculty_id))
            if user is not None:
                if getattr(user, 'user_type', None) == 5:
                    faculty_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                else:
                    faculty_name = user.name or ""

            day_map.setdefault(slot.day_of_week, []).append({
                "id": slot.id,
                "period_number": slot.period_number,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "course_id": slot.course_id,
                "course_name": course_obj.course_name if course_obj else "",
                "faculty_id": slot.faculty_id,
                "faculty_name": faculty_name,
                "entry_for": slot.entry_for,
                "lecture_type": slot.lecture_type,
            })

        slots_data = [{
            "day_of_week": day,
            "day_name": day_names[day] if 0 <= day < len(day_names) else "",
            "lectures": day_map.get(day, [])
        } for day in range(7) if day_map.get(day)]

        response_ = {
            "n": 1,
            "msg": "Template details found successfully",
            "data": {
                "template_id": template_obj.id,
                "template_name": template_obj.template_name,
                "academic_year_id": template_obj.academic_year_id,
                "academic_year_name": year_obj.academic_year_name if year_obj else "",
                "semester_id": class_semester_id,
                "semester_name": semester_obj.semester_name if semester_obj else "",
                "class_id": template_obj.class_group_id,
                "class_name": class_name,
                "total_lectures": len(slot_list),
                "slots": slots_data,
            }
        }

        if encrypted_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)


def parse_period_time(value):
    """Parse a time string (24h 'HH:MM' or 12h 'hh:mm AM/PM') into datetime.time."""
    value = str(value or "").strip()
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError("Invalid time format")


def build_period_times(start_time_str, duration_minutes, count):
    """Return a list of (start_time, end_time) 'HH:MM' strings for `count` periods."""
    base = datetime.combine(date.today(), parse_period_time(start_time_str))
    times = []
    for i in range(count):
        start_dt = base + timedelta(minutes=i * duration_minutes)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        times.append((start_dt.strftime("%H:%M"), end_dt.strftime("%H:%M")))
    return times


class AddTemplate(GenericAPIView):
    """
    Create a timetable template and auto-generate its weekly slot grid.

    POST /api/schedule/add-template

    Request Body:
    {
        "template_name": "Regular Week 1",   # Required
        "academic_year": 1,                  # Required (academic year id)
        "semester": 6,                       # Required (semester id)
        "subject": 11                        # Required (subject id)
    }

    Semester -> ClassGroup(s): the class(es) whose semester_ids contain the
    semester are resolved automatically and a default weekly grid is generated
    for the first matching class (Mon-Fri, 7 periods, 09:00 start, 60 min).

    Response:
    {
        "n": 1,
        "msg": "Template created successfully",
        "data": { ...template metadata, "course_id": subject, "slots_count": N, "slots": [...] }
    }
    """
    authentication_classes = [UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encrypted_header = ""
        if 'encrypted' in request.headers.keys():
            encrypted_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        template_name = request_data.get('template_name')
        academic_year_id = request_data.get('academic_year') or request_data.get('academic_year_id')
        semester_id = request_data.get('semester') or request_data.get('semester_id') or request_data.get('semister_id')
        subject_id = request_data.get('subject') or request_data.get('course_id')

        msg = ""
        validation_status = True

        if template_name in (None, ''):
            msg = 'template_name is required'
            validation_status = False
        elif academic_year_id in (None, ''):
            msg = 'academic_year is required'
            validation_status = False
        elif semester_id in (None, ''):
            msg = 'semester is required'
            validation_status = False
        elif subject_id in (None, ''):
            msg = 'subject is required'
            validation_status = False

        if not validation_status:
            response_ = {"n": 0, "msg": msg, "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        if not AcademicYear.objects.filter(id=academic_year_id, isActive=True).exists():
            response_ = {"n": 0, "msg": "Academic year not found", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        subject_obj = None
        try:
            subject_id = int(subject_id)
        except (TypeError, ValueError):
            subject_id = None
        if subject_id is not None:
            subject_obj = Subject.objects.filter(id=subject_id, isActive=True).first() or Subject.objects.filter(id=subject_id).first()
        if subject_obj is None:
            response_ = {"n": 0, "msg": "Subject not found", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        try:
            semester_id = int(semester_id)
        except (TypeError, ValueError):
            response_ = {"n": 0, "msg": "semester must be an integer", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        semester_obj = Semester.objects.filter(id=semester_id, isActive=True).first()
        if semester_obj is None:
            resolved = Semester.objects.filter(semester_number=semester_id, isActive=True).first()
            if resolved is not None and resolved.id != semester_id:
                semester_obj = resolved
        if semester_obj is None:
            response_ = {"n": 0, "msg": "Semester not found", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        class_group = ClassGroup.objects.filter(
            semester_ids__contains=[semester_obj.id],
            isActive=True,
        ).order_by('id').first()
        if class_group is None:
            response_ = {"n": 0, "msg": "No class found for this semester", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        existing = TimetableTemplate.objects.filter(
            academic_year_id=academic_year_id,
            class_group_id=class_group.id,
            template_name=template_name,
            is_active=True,
        ).first()
        if existing is not None:
            response_ = {"n": 0, "msg": "A template with this name already exists for this class", "data": []}
            if encrypted_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata, status=200)
            return Response(response_, status=200)

        periods_per_day = 7
        days = [0, 1, 2, 3, 4]
        start_time = "09:00"
        period_duration_minutes = 60
        year_obj = AcademicYear.objects.filter(id=academic_year_id, isActive=True).first()
        effective_from_date = year_obj.start_date if year_obj and getattr(year_obj, 'start_date', None) else None
        effective_to_date = year_obj.end_date if year_obj and getattr(year_obj, 'end_date', None) else None
        if effective_from_date is None:
            effective_from_date = date.today()

        try:
            period_times = build_period_times(start_time, period_duration_minutes, periods_per_day)
        except ValueError:
            period_times = None

        template_obj = TimetableTemplate.objects.create(
            academic_year_id=academic_year_id,
            class_group_id=class_group.id,
            template_name=template_name,
            effective_from=effective_from_date,
            effective_to=effective_to_date,
            is_published=False,
            is_active=True,
            created_by=str(request.user.id) if request.user else "admin",
            createdBy=str(request.user.id) if request.user else "admin",
        )

        slot_objs = []
        if period_times:
            for day in days:
                for i in range(periods_per_day):
                    start_time_str, end_time_str = period_times[i]
                    slot_objs.append(
                        TimetableSlot(
                            timetable_template_id=template_obj.id,
                            day_of_week=day,
                            period_number=i + 1,
                            start_time=start_time_str,
                            end_time=end_time_str,
                            course_id=subject_obj.id,
                            faculty_id="",
                            room_number="",
                            entry_for="lecture",
                            lecture_type="THEORY",
                            is_active=True,
                        )
                    )

        TimetableSlot.objects.bulk_create(slot_objs)

        slots_data = [{
            "id": slot.id,
            "day_of_week": slot.day_of_week,
            "period_number": slot.period_number,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "course_id": slot.course_id,
        } for slot in slot_objs]

        response_ = {
            "n": 1,
            "msg": "Template created successfully",
            "data": {
                "template_id": template_obj.id,
                "template_name": template_obj.template_name,
                "academic_year_id": template_obj.academic_year_id,
                "semester_id": semester_obj.id,
                "semester_name": semester_obj.semester_name,
                "class_group_id": template_obj.class_group_id,
                "class_name": f"{class_group.class_name} {class_group.division or ''}".strip(),
                "course_id": subject_obj.id,
                "course_name": subject_obj.subject_name if getattr(subject_obj, 'subject_name', None) else (subject_obj.name if getattr(subject_obj, 'name', None) else ""),
                "effective_from": template_obj.effective_from.isoformat() if template_obj.effective_from else None,
                "effective_to": template_obj.effective_to.isoformat() if template_obj.effective_to else None,
                "slots_count": len(slot_objs),
                "slots": slots_data,
            },
        }

        if encrypted_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata, status=200)
        return Response(response_, status=200)








