from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from .serializers import *
from lms.settings import *
from django.contrib.auth.hashers import make_password,check_password
from adminauth.jwt import *
from adminauth.serializers import *
from helpers.validations import *
from rest_framework import permissions
from course.models import *
from master.models import *
from master.serializers import *
# Create your views here.
from django.db.models import Q
from enrollments.models import *
from enrollments.serializers import *
from schedule.models import *
from schedule.serializers import *
from django.db.models import Count
from datetime import date  # Make sure this import is at the top of your views.py
from ticket.models import *
from ticket.serializers import *
from candidate.models import *
from candidate.serializers import *
from exam.models import *
from exam.serializers import *
from django.db.models import Sum, IntegerField,FloatField
from django.db.models.functions import Cast
# Create your views here.

class FilterCollegeReportApi(GenericAPIView):
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
        
        og_code=str(request.user.og_code)

        college_objs=UserAdmin.objects.filter(isActive=True,og_code=og_code,)
        college_objs=college_objs.filter(Q(user_type=3,is_parent_college=True,is_member=False,)|Q(user_type=4,is_member=False,))

        
        country_id=request_data.get('country_id')
        if country_id is not None and country_id !='':
            college_objs=college_objs.filter(country=country_id) 
        
        search=request_data.get('search')
        if search is not None and search !='':
            college_objs=college_objs.filter(name__icontains=search) 
        



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      college_objs=college_objs.filter(sort_by=sort_by) 







        if college_objs.exists():
            page4 = self.paginate_queryset(college_objs)
            serializer=UserAdminSerializer(page4,many=True)


            if encryped_header == "1" :
                for college in serializer.data:
                    
                    if college['name'] == 'None' or  college['name'] =='' or college['name'] is None:
                        user_obj=UserAdmin.objects.filter(id=str(college['id'])).first()
                        if user_obj is not None:
                            college['name']=user_obj.name
                            


                    course_conducted=Schedule.objects.filter(college_ids__in=[college['id']],isActive=True,action_status="Approved")
                    candidate_enrolled=Enrollments.objects.filter(college_id=college['id'],enrollments_status='2')
                    total_revenue= EnrollPayment.objects.filter(college_id=college['id'])
                    
                    if int(college['user_type']) == 3:
                        reported_complaints=Ticket.objects.filter(parent_college_id=college['id'])
                    elif int(college['user_type']) == 4:
                        reported_complaints=Ticket.objects.filter(sub_college_id=college['id'])
                    else:
                        reported_complaints=Ticket.objects.filter(isActive=True).none()





                    start_date=request_data.get('startdate')
                    if start_date is not None and start_date !='':
                        course_conducted=course_conducted.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
                        candidate_enrolled=candidate_enrolled.filter(createdAt__gte=start_date)
                        reported_complaints=reported_complaints.filter(createdAt__gte=start_date) 
                        total_revenue=total_revenue.filter(createdAt__gte=start_date) 

                    
                    end_date=request_data.get('enddate')

                    if end_date is not None and end_date !='':
                        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                        new_end_date = end_date_obj + timedelta(days=1)
                        cend_date =str(new_end_date.strftime("%Y-%m-%d"))
                        course_conducted=course_conducted.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 
                        candidate_enrolled=candidate_enrolled.filter(createdAt__lte=cend_date)
                        reported_complaints=reported_complaints.filter(createdAt__lte=cend_date) 
                        total_revenue=total_revenue.filter(createdAt__lte=cend_date) 
                        
                    college['course_conducted']=course_conducted.count()
                    college['candidate_enrolled']=candidate_enrolled.count()
                    college['reported_complaints']=reported_complaints.count()
                    college['total_revenue'] = round(total_revenue.annotate(final_amount_float=Cast("final_amount", FloatField())).aggregate(total=Sum("final_amount_float"))["total"] or 0)
                    college['revenue_per_candidate'] =0
                    if float(college['candidate_enrolled']) !=0: 
                        college['revenue_per_candidate'] =round(float(college['total_revenue'])/float(college['candidate_enrolled']),2)
                    else:
                        0

                paigna=self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))



                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'ticket not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class GetCollegeReportCountsApi(GenericAPIView):
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
        
        og_code=str(request.user.og_code)

        college_objs=UserAdmin.objects.filter(isActive=True,og_code=og_code,user_type__in=[3,4],is_member=False)
        college_objs=college_objs.filter(Q(user_type=3,is_parent_college=True,is_member=False,)|Q(user_type=4,is_member=False,))

        
        country_id=request_data.get('country_id')
        if country_id is not None and country_id !='':
            college_objs=college_objs.filter(country=country_id) 
        
        search=request_data.get('search')
        if search is not None and search !='':
            college_objs=college_objs.filter(name__icontains=search) 





        total_colleges=college_objs.count()
        total_parent_colleges=college_objs.filter(user_type=3,is_parent_college=True,is_member=False,).count()
        total_sub_colleges=college_objs.filter(user_type=4,is_parent_college=False,is_member=False,).count()
        total_active_colleges=0
        total_inactive_colleges=0




        response_={
                "n": 1,
                "msg": 'Schedule attendance found successfully',
                "data":{
                        "total_colleges":total_colleges,
                        "total_parent_colleges":total_parent_colleges,
                        "total_sub_colleges":total_sub_colleges,
                        "total_active_colleges":total_active_colleges,
                        "total_inactive_colleges":total_inactive_colleges,
                }                     
            }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
        
    
class FilterCoursesScheduleReportApi(GenericAPIView):
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
        
        og_code=str(request.user.og_code)


        query_objs=Schedule.objects.filter(isActive=True,action_status='Approved')
        country_id=request_data.get('country_id')
        if country_id is not None and country_id !='':
            tc_query_objs_ids=list(UserAdmin.objects.filter(Q(user_type=3,is_parent_college=True,is_member=False,isActive=True,og_code=og_code,country=country_id)|Q(user_type=4,is_member=False,isActive=True,og_code=og_code,country=country_id)).values_list('id',flat=True))
            query_objs=query_objs.filter(college_ids__in=tc_query_objs_ids)

        search=request_data.get('search')
        if search is not None and search !='':
            tc_query_objs_ids=list(UserAdmin.objects.filter(Q(user_type=3,is_parent_college=True,is_member=False,isActive=True,og_code=og_code,name__icontains=search)|Q(user_type=4,is_member=False,isActive=True,og_code=og_code,name__icontains=search)).values_list('id',flat=True))
            query_objs=query_objs.filter(college_ids__in=tc_query_objs_ids)



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_objs=query_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
                    
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_objs=query_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 

        query_objs=query_objs.values('id', 'course_ids','college_ids','mode').distinct()

     

        today = date.today()
        if query_objs.exists():
            new_list=[]
            for i in query_objs:
                status='Inactive'

                # scheduale_obj=Schedule.objects.filter(id=i['id']).first()
                # if scheduale_obj is not None:
                #     if scheduale_obj.start_date <= today and scheduale_obj.end_date >= today:
                #         status='Active'





                course_obj=Course.objects.filter(id=i['course_ids']).first()
                if course_obj is not None:
                    course_name=course_obj.course_name 
                else:
                    course_name='' 
                college_obj=UserAdmin.objects.filter(id=str(i['college_ids'])).first()
                if college_obj is not None:
                    college_name=college_obj.name 
                else:
                    college_name=''

                total_schedules=Schedule.objects.filter(course_ids__in=[i['course_ids']],college_ids__in=[str(i['college_ids'])],mode=i['mode'])
                total_enrollments_obj=Enrollments.objects.filter(course=i['course_ids'],college_id=str(i['college_ids']))

                start_date=request_data.get('startdate')
                if start_date is not None and start_date !='':
                    total_schedules=total_schedules.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
                    total_enrollments_obj=total_enrollments_obj.filter(createdAt__gte=start_date)
        
                end_date=request_data.get('enddate')
                if end_date is not None and end_date !='':
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    new_end_date = end_date_obj + timedelta(days=1)
                    cend_date =str(new_end_date.strftime("%Y-%m-%d"))
                    total_schedules=total_schedules.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 
                    total_enrollments_obj=total_enrollments_obj.filter(createdAt__lte=cend_date)



                total_faculties1=list(total_schedules.order_by('faculty_id').order_by('faculty_id').values_list('faculty_id',flat=True))
                total_faculties2=list(total_schedules.order_by('faculty2_id').order_by('faculty2_id').values_list('faculty2_id',flat=True))
                total_faculties = len(list(dict.fromkeys(total_faculties1+total_faculties2)))



                d1={
                    'id':i['id'],
                    'course_id':i['course_ids'],
                    'course_name':course_name,
                    'college_anme':college_name,
                    'total_schedules':total_schedules.count(),
                    'total_faculties':total_faculties,
                    'total_enrollments':total_enrollments_obj.count(),
                    'status':status,
                    'college_id':str(i['college_ids']),
                    'mode':i['mode'],
                }

                new_list.append(d1)
            if encryped_header == "1" :


                data_to_serialize = convert_decimals_to_float(new_list)
                encdata = encrypt_data(json.dumps(data_to_serialize))



                return Response(encdata,status=200)
            
            else:
                response_={
                        "n": 1,
                        "msg": 'ticket not found',
                        "data":new_list
                }
                return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'ticket not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class GetCoursesScheduleReportCountsApi(GenericAPIView):
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
        
        og_code=str(request.user.og_code)

        cancel_courses_schedules=Schedule.objects.filter(isActive=True,action_status='Decline').count()

        query_objs=Schedule.objects.filter(isActive=True,action_status='Approved')
        country_id=request_data.get('country_id')
        if country_id is not None and country_id !='':
            tc_query_objs_ids=list(UserAdmin.objects.filter(Q(user_type=3,is_parent_college=True,is_member=False,isActive=True,og_code=og_code,country=country_id)|Q(user_type=4,is_member=False,isActive=True,og_code=og_code,country=country_id)).values_list('id',flat=True))
            query_objs=query_objs.filter(college_ids__in=tc_query_objs_ids)

        search=request_data.get('search')
        if search is not None and search !='':
            tc_query_objs_ids=list(UserAdmin.objects.filter(Q(user_type=3,is_parent_college=True,is_member=False,isActive=True,og_code=og_code,name__icontains=search)|Q(user_type=4,is_member=False,isActive=True,og_code=og_code,name__icontains=search)).values_list('id',flat=True))
            query_objs=query_objs.filter(college_ids__in=tc_query_objs_ids)


        today = date.today()

        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 
        total_courses=query_objs.order_by('course_ids').values('course_ids').distinct().count()
        total_courses_schedules=query_objs.order_by('id').distinct('id').count()
        upcoming_courses_schedules=query_objs.filter(Q(start_date__gte=today)|Q(end_date__gte=today)).order_by('course_ids').values('course_ids').distinct().count()

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_objs=query_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
                    
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_objs=query_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 



        ongoing_courses_schedules=query_objs.order_by('id').distinct('id').count()

        

        context={
            'total_courses':total_courses,
            'total_courses_schedules':total_courses_schedules,
            'ongoing_courses_schedules':ongoing_courses_schedules,
            'upcoming_courses_schedules':upcoming_courses_schedules,
            'cancel_courses_schedules':cancel_courses_schedules,

        }
        if encryped_header == "1" :


            data_to_serialize = convert_decimals_to_float(context)
            encdata = encrypt_data(json.dumps(data_to_serialize))



            return Response(encdata,status=200)
        
        else:
            response_={
                    "n": 1,
                    "msg": 'ticket  found',
                    "data":context
            }
            return Response(response_,status=200)

class FilterCandidateReportApi(GenericAPIView):
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
        
        og_code=str(request.user.og_code)


        query_objs=Candidate.objects.filter(isActive=True,)
        country_id=request_data.get('country_id')
        if country_id is not None and country_id !='':
            query_objs=query_objs.filter(country=country_id)

        search=request_data.get('search')
        if search is not None and search !='':
            query_objs=query_objs.filter(Q(first_name__icontains=search)|Q(middle_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        # start_date=request_data.get('startdate')
        # if start_date is not None and start_date !='':
        #     query_objs=query_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
                    
        # end_date=request_data.get('enddate')
        # if end_date is not None and end_date !='':
        #     end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        #     new_end_date = end_date_obj + timedelta(days=1)
        #     cend_date =str(new_end_date.strftime("%Y-%m-%d"))
        #     query_objs=query_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 


     

        today = date.today()
        if query_objs.exists():
            page4 = self.paginate_queryset(query_objs)
            serializer=CandidateSerializer(page4,many=True)

            
            for i in serializer.data:
                enroll_obj=Enrollments.objects.filter(candidate=i['id'],enrollments_status='2').order_by('createdAt')
                first_enroll=enroll_obj.first()
                if first_enroll is not None:
                    i['enroll_date']=str(first_enroll.createdAt).split(' ')[0]
                else:
                    i['enroll_date']=''

                i['total_courses_enrolled_count']=enroll_obj.filter(candidate=i['id']).order_by('course').distinct('course').count()
                i['status']='Active'
                rank_obj=Rank.objects.filter(id=i['rank']).first()
                i['rank_name']=''
                if rank_obj is not None:
                    i['rank_name']=rank_obj.rank

                department_obj=Department.objects.filter(id=i['department']).first()
                i['department_name']=''
                if department_obj is not None:
                    i['department_name']=department_obj.department_name

                country_obj=Country.objects.filter(id=i['country']).first()
                i['country_name']=''
                if country_obj is not None:
                    i['country_name']=country_obj.name



                last_login_date = CandidateToken.objects.filter(user_id=i['id']).order_by('-createdAt').first()       


                i['last_login_date']=''
                if last_login_date is not None:
                    i['last_login_date']=str(last_login_date.createdAt).split(' ')[0]
                    i['inactive_since_date']=str(last_login_date.createdAt).split(' ')[0]


                i['last_certification_date']=''
                i['success_rate']=100
                i['total_certifications']=0




  
 

                # start_date=request_data.get('startdate')
                # if start_date is not None and start_date !='':
                   
        
                # end_date=request_data.get('enddate')
                # if end_date is not None and end_date !='':
                #     end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                #     new_end_date = end_date_obj + timedelta(days=1)
                #     cend_date =str(new_end_date.strftime("%Y-%m-%d"))







            if encryped_header == "1" :

                paigna=self.get_paginated_response(serializer.data)

                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            
            else:

                response_={
                            "n": 0,
                            "msg": 'Candidates found',
                            "data":serializer.data,                   
                        }

                return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'ticket not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class FilterCandidateReportCountsApi(GenericAPIView):
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
        
        og_code=str(request.user.og_code)


        query_objs=Candidate.objects.filter(isActive=True,walkin_by=og_code)

        country_id=request_data.get('country_id')
        if country_id is not None and country_id !='':
            query_objs=query_objs.filter(country=country_id)

        search=request_data.get('search')
        if search is not None and search !='':
            query_objs=query_objs.filter(Q(first_name__icontains=search)|Q(middle_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        # start_date=request_data.get('startdate')
        # if start_date is not None and start_date !='':
        #     query_objs=query_objs.filter(Q(start_date__gte=start_date)|Q(end_date__gte=start_date)) 
                    
        # end_date=request_data.get('enddate')
        # if end_date is not None and end_date !='':
        #     end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        #     new_end_date = end_date_obj + timedelta(days=1)
        #     cend_date =str(new_end_date.strftime("%Y-%m-%d"))
        #     query_objs=query_objs.filter(Q(end_date__lte=end_date)|Q(start_date__lte=end_date)) 


        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        total_candidates=query_objs.count()
        coc_candidates=0
        enrolled_candidates=Enrollments.objects.filter(enrollments_status='2').order_by('candidate').distinct('candidate').count()
        active_candidates=CandidateToken.objects.filter(createdAt__gte=thirty_days_ago).order_by('user_id').distinct('user_id').count()
        inactive_candidates=total_candidates-active_candidates




        context={
            "total_candidates":total_candidates,
            "enrolled_candidates":enrolled_candidates,
            "active_candidates":active_candidates,
            "inactive_candidates":inactive_candidates,
            "coc_candidates":coc_candidates,

        }

        response_={
                    "n": 0,
                    "msg": 'Candidates found',
                    "data":context,                   
                }

        return Response(response_,status=200)



class FilterRevenueReportApi(GenericAPIView):
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
        


        og_code=str(request.user.og_code)


        query_objs=Enrollments.objects.filter(isActive=True,)
        # country_id=request_data.get('country_id')
        # if country_id is not None and country_id !='':
        #     query_objs=query_objs.filter(country=country_id)

        # search=request_data.get('search')
        # if search is not None and search !='':
        #     query_objs=query_objs.filter(Q(first_name__icontains=search)|Q(middle_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_objs=query_objs.filter(createdAt__gte=start_date) 
                    
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_objs=query_objs.filter(createdAt__lte=cend_date) 


     

        today = date.today()
        if query_objs.exists():
            page4 = self.paginate_queryset(query_objs)
            serializer=EnrollmentsSerializer(page4,many=True)

            
            for i in serializer.data:
                enroll_obj=EnrollPayment.objects.filter(enrollment_id=i['id']).first()
                candidate_obj=Candidate.objects.filter(id=i['candidate']).first()
                if candidate_obj is not None:
                    i['first_name']=candidate_obj.first_name  
                    i['middle_name']=candidate_obj.middle_name 
                    i['last_name']=candidate_obj.last_name
                else:   
                    i['first_name']=''   
                    i['middle_name']=''   
                    i['last_name']=''   

                i['course_name']='' 
                course_obj=Course.objects.filter(id=i['course']).first()  
                if course_obj is not None:
                    i['course_name']=course_obj.course_name



                i['college_name']=''  
                college_obj=UserAdmin.objects.filter(id=str(i['college_id'])).first()
                if college_obj is not None:
                    i['college_name']=college_obj.name

                i['date']=str(i['createdAt']).split('T')[0]
                if enroll_obj is not None:

                    i['fees']=enroll_obj.final_amount 
                    i['payment_status']='Done'   
                    i['mode']=enroll_obj.payment_method
                else:
                    i['fees']=0 
                    i['payment_status']='Pending'   
                    i['mode']=''


            if encryped_header == "1" :

                paigna=self.get_paginated_response(serializer.data)

                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            
            else:

                response_={
                            "n": 0,
                            "msg": 'Revenue found',
                            "data":serializer.data,                   
                        }

                return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'Revenue not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class FilterRevenueReportCountsApi(GenericAPIView):
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
        


        og_code=str(request.user.og_code)


        query_objs=EnrollPayment.objects.filter(isActive=True,)
        # country_id=request_data.get('country_id')
        # if country_id is not None and country_id !='':
        #     query_objs=query_objs.filter(country=country_id)

        # search=request_data.get('search')
        # if search is not None and search !='':
        #     query_objs=query_objs.filter(Q(first_name__icontains=search)|Q(middle_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_objs=query_objs.filter(createdAt__gte=start_date) 
                    
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_objs=query_objs.filter(createdAt__lte=cend_date) 


     

        today = date.today()

        total_revenue=round(query_objs.annotate(final_amount_float=Cast("final_amount", FloatField())).aggregate(total=Sum("final_amount_float"))["total"] or 0)

        revenue_pending=0
        revenue_from_certificates=0


        context={
            "total_revenue":total_revenue,
            "revenue_pending":revenue_pending,
            "revenue_from_certificates":revenue_from_certificates,
        }
        if encryped_header == "1" :


            data_to_serialize = convert_decimals_to_float(context)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        
        else:

            response_={
                        "n": 0,
                        "msg": 'Revenue found',
                        "data":context,                   
                    }

            return Response(response_,status=200)



class FilterCertificationReportApi(GenericAPIView):
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
        


        og_code=str(request.user.og_code)


        query_objs=ExamCandidateResult.objects.filter(isActive=True,is_passed=True)
        # country_id=request_data.get('country_id')
        # if country_id is not None and country_id !='':
        #     query_objs=query_objs.filter(country=country_id)

        # search=request_data.get('search')
        # if search is not None and search !='':
        #     query_objs=query_objs.filter(Q(first_name__icontains=search)|Q(middle_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))



        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_objs=query_objs.filter(createdAt__gte=start_date) 
                    
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_objs=query_objs.filter(createdAt__lte=cend_date) 


     

        today = date.today()
        if query_objs.exists():
            page4 = self.paginate_queryset(query_objs)
            serializer=ExamCandidateResultSerializer(page4,many=True)

            
            for i in serializer.data:

                candidate_obj=Candidate.objects.filter(id=i['candidate_id']).first()
                if candidate_obj is not None:
                    i['first_name']=candidate_obj.first_name  
                    i['middle_name']=candidate_obj.middle_name 
                    i['last_name']=candidate_obj.last_name
                else:   
                    i['first_name']=''   
                    i['middle_name']=''   
                    i['last_name']=''   
                i['course_name']='' 
                i['college_name']=''  
                i['expiry_date']=''  
                i['status']=''  
                i['date']=str(i['createdAt']).split('T')[0]
        
                exam_schedule_obj=ScheduleExam.objects.filter(id=i['exam_schedule_id']).first()
                if exam_schedule_obj is not None:

                    course_obj=Course.objects.filter(id=exam_schedule_obj.course).first()  
                    if course_obj is not None:
                        i['course_name']=course_obj.course_name
                        i['expiry_date']=course_obj.expiry
                        if i['expiry_date'] < today:
                            i['status']='Inactive'

                    college_obj=UserAdmin.objects.filter(id=exam_schedule_obj.college).first()
                    if college_obj is not None:
                        i['college_name']=college_obj.name





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
                        "n": 0,
                        "msg": 'Revenue not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)




class FilterCertificationReportCountsApi(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        


        og_code=str(request.user.og_code)


        query_objs=ExamCandidateResult.objects.filter(isActive=True,is_passed=True)
        # country_id=request_data.get('country_id')
        # if country_id is not None and country_id !='':
        #     query_objs=query_objs.filter(country=country_id)

        # search=request_data.get('search')
        # if search is not None and search !='':
        #     query_objs=query_objs.filter(Q(first_name__icontains=search)|Q(middle_name__icontains=search)|Q(last_name__icontains=search)|Q(email__icontains=search))

        # sort_by=request_data.get('sort_by')
        # if sort_by is not None and sort_by !='':
        #      query_objs=query_objs.filter(sort_by=sort_by) 

        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_objs=query_objs.filter(createdAt__gte=start_date) 
                    
        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_objs=query_objs.filter(createdAt__lte=cend_date) 


     
        total_certifications=query_objs.count()



        today = date.today()
        inactive_cources_ids=list(Course.objects.filter(expiry__lte=today,isActive=True).values_list('id',flat=True))
        inactive_schedule_exam_couses_exam_ids=list(ScheduleExam.objects.filter(course__in=inactive_cources_ids).values_list('id',flat=True))
        certification_inactive=query_objs.filter(exam_schedule_id__in=inactive_schedule_exam_couses_exam_ids).count()
        
        
        active_cources_ids=list(Course.objects.filter(expiry__gt=today,isActive=True).values_list('id',flat=True))
        active_schedule_exam_couses_exam_ids=list(ScheduleExam.objects.filter(course__in=active_cources_ids).values_list('id',flat=True))
        certification_active=query_objs.filter(exam_schedule_id__in=active_schedule_exam_couses_exam_ids).count()






        context={
            "total_certification":total_certifications,
            "certification_inactive":certification_inactive,
            "certification_active":certification_active,
        }
        response_={
                    "n": 1,
                    "msg": 'Certification count found',
                    "data":context                     
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)







































