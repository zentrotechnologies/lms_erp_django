from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
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
# Create your views here.
class MarkCandidateAttendance(GenericAPIView):
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
        candidate_id=request_data.get('candidate_id')
        if candidate_id is None or candidate_id =='':
            msg="Please provide candidate id "
            validation_status=False 
            
        schedule_id=request_data.get('schedule_id')
        if schedule_id is None or schedule_id =='':
            msg="Please provide schedule id "
            validation_status=False 

        course_id=request_data.get('course_id')
        if course_id is None or course_id =='':
            msg="Please provide course id "
            validation_status=False 


        college_id=request_data.get('college_id')
        if college_id is None or college_id =='':
            msg="Please provide college id "
            validation_status=False 

        faculty_id=str(request.user.id)

        attendance_date=request_data.get('attendance_date')
        if attendance_date is None or attendance_date =='':
            msg="Please provide attendance date "
            validation_status=False 


        attendance_obj=CandidateAttendance.objects.filter(attendance_date=attendance_date,schedule_id=schedule_id,candidate_id=candidate_id,course_id=course_id,college_id=college_id).first()

        checkin_time=request_data.get('checkin_time')
        checkout_time=request_data.get('checkout_time')
        absent=request_data.get('absent')
        if absent.lower() in ['True','TRUE','true']:
            absent=True
            present=False
        else:
            absent=False
            present=True
            if attendance_obj.absent == False:

                if (checkin_time is None or checkin_time == '') and (checkout_time is None or checkout_time == ''):
                    msg = "Please provide check-in time or check-out time"
                    validation_status = False


        if validation_status:
            data={}
            data['checkin_time']=checkin_time
            data['checkout_time']=checkout_time
            data['attendance_date']=attendance_date
            data['absent']=absent
            data['present']=present
            data['faculty_id']=faculty_id
            data['college_id']=college_id
            data['course_id']=course_id
            data['schedule_id']=schedule_id
            data['candidate_id']=candidate_id
            data['isActive']=True

            if attendance_obj is not None:
                serializer=CandidateAttendanceSerializer(attendance_obj,data=data,partial=True)
            else:
                serializer=CandidateAttendanceSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                response_={
                        "n": 1,
                        "msg": 'Attendance marked successfully',
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
