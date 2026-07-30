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
# Create your views here.
from django.db.models import Q
from candidate.models import *
from candidate.serializers import *

from enrollments.models import *
from enrollments.serializers import *

from attendance.models import *
from attendance.serializers import *
from datetime import date

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
        
        training_center_ids=json.loads(request_data.get('training_center_ids'))
        if training_center_ids is None or training_center_ids =='':
            msg="Please provide training center ids"
            validation_status=False 
            
        request_data['training_center_ids']=training_center_ids
            

        
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
        training_center_ids=json.loads(request_data.get('training_center_ids'))
        if training_center_ids is None or training_center_ids =='':
            msg="Please provide training center ids"
            validation_status=False 
            
        request_data['training_center_ids']=training_center_ids
            
            

        
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
        
        schedule_objs=Schedule.objects.filter(training_center_ids=member_of,isActive=True).exclude(action_status='Decline')
        course_id=request_data.get('course')
        if course_id is not None and course_id !='':
            schedule_objs=schedule_objs.filter(course_ids__in=[course_id]) 
        # Apply non-empty filters
        filters = {
            'course_ids__in': [request_data.get('course')] if request_data.get('course') else None,
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        
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
        

        schedule_objs = Schedule.objects.filter(isActive=True,training_center_ids__in=[str(request.user.id)])

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
                        "title": f"{serializer.data['schedulename']}  - {', '.join(serializer.data['training_center_names'])} - {', '.join(serializer.data['course_names'])} - {serializer.data['faculty_name']}",
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
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            # 'branch_id': request_data.get('branch_id'),
            # 'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        

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
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            # 'branch_id': request_data.get('branch_id'),
            # 'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        

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
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            # 'branch_id': request_data.get('branch_id'),
            # 'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        

        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        

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
        """Expand schedule objects to unique training_center_id and course_id combinations"""
        expanded_schedules = []

        for schedule in schedule_objs:
            branch = Branch.objects.filter(id=schedule.branch_id, isActive=True).values('name').first()
            branch_name = branch['name'] if branch else None  # Extract name safely

            for training_center in schedule.training_center_ids.all():
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
                        "training_center_id": training_center.id,
                        "training_center_name": training_center.name,
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
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        
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
        """Expand schedule objects to unique training_center_id and course_id combinations"""
        expanded_schedules = []

        for schedule in schedule_objs:
            branch = Branch.objects.filter(id=schedule.branch_id, isActive=True).values('name').first()
            branch_name = branch['name'] if branch else None  # Extract name safely

            for training_center in schedule.training_center_ids.all():
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
                        "training_center_id": training_center.id,
                        "training_center_name": training_center.name,
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
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        
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
        """Expand schedule objects to unique training_center_id and course_id combinations"""
        expanded_schedules = []

        for schedule in schedule_objs:
            branch = Branch.objects.filter(id=schedule.branch_id, isActive=True).values('name').first()
            branch_name = branch['name'] if branch else None  # Extract name safely

            for training_center in schedule.training_center_ids.all():
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
                        "training_center_id": training_center.id,
                        "training_center_name": training_center.name,
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
            'training_center_ids__in': [request_data.get('trainingcenters')] if request_data.get('trainingcenters') else None,
            'branch_id': request_data.get('branch_id'),
            'faculty_id': request_data.get('faculty_id'),
        }

        for key, value in filters.items():
            if value:
                schedule_objs = schedule_objs.filter(**{key: value})
        
        
        training_center_id=request_data.get('trainingcenters')
        if training_center_id is not None and training_center_id !='':
            schedule_objs=schedule_objs.filter(training_center_ids__in=[training_center_id]) 
        
        
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

        training_center_id=request_data.get('training_center_id')
        # if training_center_id is None or training_center_id =='':
            # msg="Please provide training center id"
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

                if training_center_id is None or training_center_id =='':
                    training_center_id=new_serializer['training_center_ids'][0]

                schedule_list_obj=Schedule.objects.filter(faculty_id=faculty_id,start_date__lte=schedule_date,end_date__gte=schedule_date,isActive=True).exclude(action_status="Decline")
                schedule_list_serializer=CustomScheduleSerializer(schedule_list_obj,many=True)
                

                candidate_ids=list(Enrollments.objects.filter(course=course_id,schedule=serializer.data['id'],isActive=True).order_by('candidate').distinct("candidate").values_list('candidate',flat=True))

                candidate_objs=Candidate.objects.filter(id__in=candidate_ids,isActive=True)
                candidate_serializer=CandidateSerializer(candidate_objs,many=True)
                schedule_attendance=[]
                for candidate in candidate_serializer.data:
                    candidate['candidate_name']=candidate['first_name']+' '+candidate['middle_name']+' '+candidate['last_name']

                    attendance_obj=CandidateAttendance.objects.filter(candidate_id=candidate['id'],schedule_id=serializer.data['id'],course_id=course_id,training_center_id=training_center_id,faculty_id=faculty_id,attendance_date=schedule_date).first()
                    candidate['checkin_time']=''
                    candidate['checkout_time']=''
                    candidate['absent']=False

                    if attendance_obj is not None:
                        candidate['checkin_time']=attendance_obj.checkin_time
                        candidate['checkout_time']=attendance_obj.checkout_time
                        candidate['absent']=attendance_obj.absent
                    

                    candidate['course_id']=course_id
                    candidate['training_center_id']=training_center_id

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

        training_center_id=request_data.get('training_center_id')
        if training_center_id is None or training_center_id =='':
            msg="Please provide training center id"
            validation_status=False 
        faculty_id=str(request.user.id)

               
        if validation_status:
            schedule_obj=Schedule.objects.filter(id=schedule_id,isActive=True,
                    # training_center_ids__in=[str(training_center_id)],course_ids__in=[course_id]
                                                 ).first()

            if schedule_obj is not None:
                serializer=CustomScheduleSerializer(schedule_obj)
                new_serializer=serializer.data
                new_serializer['total_days']=calculate_days_difference(new_serializer['start_date'],new_serializer['end_date'])
                candidate_ids=list(Enrollments.objects.filter(course=course_id,schedule=serializer.data['id'],isActive=True).order_by('candidate').distinct("candidate").values_list('candidate',flat=True))

                new_serializer['training_center_name']=''
                # training_center_obj = UserAdmin.objects.filter(id=str(training_center_id), isActive=True).values('name').first()
                # new_serializer['training_center_name'] = training_center_obj['name'] if training_center_obj else None  # Extract name safely

                course_obj = Course.objects.filter(id=course_id, isActive=True).values('course_name').first()
                new_serializer['course_name'] = course_obj['course_name'] if course_obj else None  # Extract name safely

                candidate_objs=Candidate.objects.filter(id__in=candidate_ids,isActive=True)
                candidate_serializer=CandidateSerializer(candidate_objs,many=True)
                schedule_attendance=[]

                sum_of_attendance=0

                for candidate in candidate_serializer.data:
                    candidate['candidate_name']=candidate['first_name']+' '+candidate['middle_name']+' '+candidate['last_name']
                    candidate['course_id']=course_id
                    candidate['training_center_id']=training_center_id
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
           






                    
                    candidate['present_count']=CandidateAttendance.objects.filter(candidate_id=candidate['id'],schedule_id=serializer.data['id'],course_id=course_id,training_center_id=training_center_id,faculty_id=faculty_id,attendance_date__gte=new_serializer['start_date'],attendance_date__lte=new_serializer['end_date']).exclude(absent=True).count()
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











