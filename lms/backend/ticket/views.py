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
from adminauth.common import *

def format_datetime(timestamp_str):
    # Parse the input timestamp
    dt = datetime.fromisoformat(timestamp_str)
    
    # Format the datetime as "DD/MM/YYYY (HH:MM)"
    formatted_date = dt.strftime("%d/%m/%Y (%H:%M)")
    
    return formatted_date

def time_difference(timestamp_str):
    # Convert the input timestamp to a datetime object
    given_time = datetime.fromisoformat(timestamp_str)
    
    # Get the current time in the same timezone
    current_time = datetime.now(given_time.tzinfo)
    

    # Calculate the time difference
    time_diff = given_time - current_time
    total_seconds = int(time_diff.total_seconds())  # Get absolute total seconds
    
    # Extract days, hours, and minutes correctly
    days, remainder = divmod(abs(total_seconds), 86400)  # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
    minutes, _ = divmod(remainder, 60)  # 60 seconds in a minute

    return f"{days} days, {hours} hours, {minutes} minutes"

def extract_filename_and_extension(file_path):
    filename, file_extension = os.path.splitext(os.path.basename(file_path))
    return filename, file_extension.lstrip('.').lower()  # Remove leading "."


class AddTicket(GenericAPIView):
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
        data={}
        subject=request_data.get('subject')
        if subject is None or subject =='':
            msg="Please provide ticket subject "
            validation_status=False 
        else:
            data['subject']=subject 
            
            
        priority=request_data.get('priority')
        if priority is None or priority =='':
            msg="Please select ticket priority"
            validation_status=False 
        else:
            data['priority']=priority 
        category=request_data.get('category')
        if category is None or category =='':
            msg="Please select ticket category"
            validation_status=False 
        else:
            data['category']=category 
        description=request_data.get('description')
        if description is None or description =='':
            msg="Please enter ticket description"
            validation_status=False 
        else:
            data['description']=description 
        if (request.user.user_type == 5) or (request.user.user_type == 3 and request.user.is_member == True) or (request.user.user_type == 4 and request.user.is_member == True):
            data['requestername']=str(request.user.first_name) +' '+str(request.user.last_name)
        else:
            data['requestername']=request.user.name

        data['email']=request.user.email
        data['status']='Pending'
        og_code=str(request.user.og_code)

        data['ticketid']='#LMS'+str(int(Ticket.objects.filter(isActive=True,og_code=og_code).count())+1)
        data['raiseby']=str(request.user.id)
        data['og_code']=str(request.user.og_code)
        
        if validation_status:
            user_type=request.user.user_type
            is_parent_college=request.user.is_parent_college
            is_member=request.user.is_member
            member_of=str(request.user.member_of)
            parent_college=request.user.parent_college

            #Parent college Admin
            if user_type == 3 and is_parent_college==True and is_member == False and member_of in ['','None',None]:
                data['parent_college_id']=str(request.user.id)
                data['sub_college_id']=''
                print("Parent college Admin",)


            #Parent college Member
            if user_type == 3 and is_parent_college == False and is_member == True and member_of != '':
                data['parent_college_id']=member_of
                data['sub_college_id']=''
                print("Parent college Member",)

            #Sub college Admin
            elif user_type == 4 and is_parent_college == False and is_member == False  and parent_college != '':
                data['parent_college_id']=parent_college
                data['sub_college_id']=str(request.user.id)
                print("Sub college Admin",)

            #Sub college Member
            elif user_type == 4 and is_parent_college == False and is_member == True  and parent_college != '':
                user_obj=UserAdmin.objects.filter(id=member_of).first()
                if user_obj is not None:

                    data['parent_college_id']=str(user_obj.parent_college)
                    data['sub_college_id']=str(user_obj.id)
                    
                print("Sub college Member",parent_college,member_of)

            # college Faculty
            elif user_type == 5 and parent_college !='':
                user_obj=UserAdmin.objects.filter(id=parent_college).first()
                # Parent college Faculty
                if user_obj.is_parent_college==True and user_obj.user_type==3:
                    data['parent_college_id']=parent_college
                    data['sub_college_id']=''
                    print("Parent college Faculty",)

                #Sub college Faculty
                elif user_obj.is_parent_college==False and user_obj.user_type==4:
                    data['parent_college_id']=member_of
                    data['sub_college_id']=str(user_obj.id)
                    print("Sub college Faculty",)
            elif user_type == 6:

                schedules_ids=list(Enrollments.objects.filter(candidate=str(request.user.id),enrollments_status='2',isActive=True).values_list('schedule',flat=True))

                today = timezone.now().date()

                # Query for schedules where today is between start_date and end_date
                todays_schedules_ids = list(Schedule.objects.filter(
                    id__in=schedules_ids,
                    start_date__lte=today,
                    end_date__gte=today
                ).values_list('id',flat=True))


                
                colleges_ids=list(Enrollments.objects.filter(candidate=str(request.user.id),schedule=todays_schedules_ids,enrollments_status='2',isActive=True).values_list('college_id',flat=True))

                college_obj=UserAdmin.objects.filter(id__in=colleges_ids).first()
                if college_obj is not None:
                    if college_obj.user_type == 3 and college_obj.is_parent_college==True and college_obj.is_member == False and college_obj.member_of == '':
                        data['parent_college_id']=college_obj.id
                        data['sub_college_id']=''
                        print("Candidate With Parent college",)
                    elif college_obj.user_type == 4 and college_obj.is_parent_college == False and college_obj.is_member == False  and college_obj.parent_college != '':
                        data['parent_college_id']=college_obj.parent_college
                        data['sub_college_id']=college_obj.id
                        print("Candidate With Sub college",)
                    else:
                        data['parent_college_id']=''
                        data['sub_college_id']=''
                        print("Candidate With No college",)  
                else:
                    data['parent_college_id']=''
                    data['sub_college_id']=''
                    print("Candidate With No college",)    


            
            serializer=TicketSerializer(data=data)
            if serializer.is_valid():

                serializer.save()
                print("request_data",request_data,request.FILES)
                if request.FILES.get('attachments') is not None and request.FILES.get('attachments') !='':
                    attachments=request.FILES.get('attachments')
                    a_data={
                        'ticket':serializer.data['id'],
                        'attachment':attachments,
                        'comment':'',
                    }
                    attachment_ser=TicketAttachmentsSerializer(data=a_data)
                    if attachment_ser.is_valid():
                        attachment_ser.save()
                    else:
                        print("error",attachment_ser.errors)



                response_={
                        "n": 1,
                        "msg": 'New Ticket added successfully',
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



class DeleteTicket(GenericAPIView):
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
        

        

            

        id=request_data.get('ticket_id')
        if id is None or id =='':
            msg="Please provide ticket id "
            validation_status=False 
            
            
        Ticket_obj=Ticket.objects.filter(id=id,isActive=True).first()
        if Ticket_obj is None:
            msg="ticket not found "
            validation_status=False 
        

        if validation_status:
            data={}
            data['isActive']=False
            serializer=TicketSerializer(Ticket_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                response_={
                        "n": 1,
                        "msg": 'Ticket deleted successfully',
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

class CloseTicket(GenericAPIView):
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
        

        

            

        id=request_data.get('ticket_id')
        if id is None or id =='':
            msg="Please provide ticket id "
            validation_status=False 
            
            
        Ticket_obj=Ticket.objects.filter(id=id,isActive=True).first()
        if Ticket_obj is None:
            msg="ticket not found "
            validation_status=False 
        

        if validation_status:
            data={}
            data['status']='Closed'
            serializer=TicketSerializer(Ticket_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                response_={
                        "n": 1,
                        "msg": 'Ticket closed successfully',
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

class MarkDuplicateTicket(GenericAPIView):
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
        

        

            

        id=request_data.get('ticket_id')
        if id is None or id =='':
            msg="Please provide ticket id "
            validation_status=False 
            
            
        Ticket_obj=Ticket.objects.filter(id=id,isActive=True).first()
        if Ticket_obj is None:
            msg="ticket not found "
            validation_status=False 

        if Ticket_obj.isduplicate:
            msg="Ticket is already marked as duplicate."
            validation_status=False 

        if validation_status:
            data={}
            data['isduplicate']=True
            serializer=TicketSerializer(Ticket_obj,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                response_={
                        "n": 1,
                        "msg": 'Ticket marked as duplicate successfully',
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



class TicketInfo(GenericAPIView):
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

        id=request_data.get('ticket_id')
        if id is None or id =='':
            msg="Please provide ticket id"
            validation_status=False 
            
            
        Ticket_obj=Ticket.objects.filter(id=id,isActive=True).first()
        if Ticket_obj is None:
            msg="ticket not found "
            validation_status=False 
        

        if validation_status:
            serializer=TicketSerializer(Ticket_obj)
            data=serializer.data
            data['assign_user']=''
            assign_user_obj=TicketAssign.objects.filter(ticket=data['id'],active=True).order_by('-id').first()
            if assign_user_obj is not None:
                data['assign_user']=assign_user_obj.userid
            
            faq_obj=FAQTicket.objects.filter(ticket=data['id'],isActive=True).first()

            if faq_obj is not None:
                departmentId=faq_obj.departmentId
                departmentId_obj=Department.objects.filter(id=departmentId).first()
                data['departmentname']=departmentId_obj.department_name
            else:
                data['departmentname']='NA'





            category_obj=TicketCategory.objects.filter(id=str(data['category']),isActive=True).first()
            if category_obj is not None:
                data['categoryname']=category_obj.name
            else:
                data['categoryname']='NA'


            submited_date_time=format_datetime(data['createdAt'])
            data['submited_date_time']=submited_date_time
            if data['updatedAt'] is not None and data['updatedAt'] !='':
                last_updated=time_difference(data['updatedAt'])
            else:
                last_updated=time_difference(data['createdAt'])
                data['last_updated']=last_updated


            faq_obj=FAQTicket.objects.filter(ticket=data['id'],isActive=True).first()
            if faq_obj is not None:
                data['categoryId']=Ticket_obj.category
                data['departmentId']=faq_obj.departmentId
                data['tags']=faq_obj.tags
                data['faqattachment']=str(faq_obj.attachment)
                data['is_faq']=True
            else:
                data['categoryId']=''
                data['departmentId']=''
                data['tags']=''
                data['faqattachment']=''
                data['is_faq']=False



            response_={
                    "n": 1,
                    "msg": 'Ticket found successfully',
                    "data":data                  
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



class GetTicketCounts(GenericAPIView):
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

        ticket_objs=Ticket.objects.filter(isActive=True,og_code=og_code)    
        if request.user.user_type == 2:
            print("Organization Admin",)
        elif request.user.user_type == 3:
            if request.user.is_parent_college==True and request.user.is_member == False and request.user.member_of in ['',None,'None']:
                print("Parent college Admin",)
                ticket_objs=ticket_objs.filter(Q(parent_college_id=request.user.id)|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
            elif request.user.is_parent_college == False and request.user.is_member == True and request.user.member_of != '':
                print("Parent college Member",)
                ticket_objs=ticket_objs.filter(Q(parent_college_id=request.user.member_of)|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))




            else:
                ticket_objs=ticket_objs.none()
                print("hii",
                      request.user.is_parent_college,
                      request.user.is_member,
                      request.user.member_of
                      )
        elif request.user.user_type == 4:
            if request.user.is_parent_college == False and request.user.is_member == False  and request.user.parent_college != '':
                print("Sub college Admin",)
                ticket_objs=ticket_objs.filter(Q(sub_college_id=str(request.user.id))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')


                

            elif request.user.is_parent_college == False and request.user.is_member == True  and request.user.parent_college != '':
                print("Sub college Member",request.user.parent_college)
                ticket_objs=ticket_objs.filter(Q(sub_college_id=str(request.user.member_of))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))
        elif request.user.user_type == 5:
                user_obj=UserAdmin.objects.filter(id=request.user.parent_college).first()
                if user_obj is not None:
                    if user_obj.is_parent_college==True and user_obj.user_type==3:
                        ticket_objs=ticket_objs.filter(Q(parent_college_id=str(user_obj.id))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                        assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                        ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))
                        print("Parent college Faculty",)
                    elif user_obj.is_parent_college==False and user_obj.user_type==4:
                        ticket_objs=ticket_objs.filter(Q(sub_college_id=str(user_obj.id))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                        assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                        ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))
                        print("Sub college Faculty",)
        else:
            ticket_objs=ticket_objs.none()


        
        status=request_data.get('status')
        if status is not None and status !='':
            ticket_objs=ticket_objs.filter(status=status) 
        

        raiseby=request_data.get('raiseby')
        if raiseby is not None and raiseby !='':
            ticket_objs=ticket_objs.filter(raiseby=raiseby) 
        
        priority=request_data.get('priority_search')
        if priority is not None and priority !='':
            ticket_objs=ticket_objs.filter(priority=priority) 



        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            ticket_objs=ticket_objs.filter(createdAt__gte=start_date) 
        
        end_date=request_data.get('enddate')


        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            ticket_objs=ticket_objs.filter(createdAt__lte=cend_date) 

        subject_search=request_data.get('subject_search')
        if subject_search is not None and subject_search !='':
            ticket_objs=ticket_objs.filter(subject__icontains=subject_search) 

        allticket=ticket_objs.count()
        closedticket=ticket_objs.filter(status="Closed").count()
        openticket=ticket_objs.filter(status="Pending").count()
        pendingticket=ticket_objs.filter(status="Pending").count()
        reopenticket=ticket_objs.filter(status="Reopen").count()
        assigned_ticket_ids=list(TicketAssign.objects.filter(active=True).order_by('ticket').distinct('ticket').values_list('ticket',flat=True))
        unassignedticket=ticket_objs.exclude(id__in=assigned_ticket_ids).count()

        data={}
        data['allticket']=allticket
        data['closedticket']=closedticket
        data['openticket']=openticket
        data['pendingticket']=pendingticket
        data['reopenticket']=reopenticket
        data['unassignedticket']=unassignedticket



        if encryped_header == "1" :
            response_={
                        "n": 0,
                        "msg": 'Counts found successfully',
                        "data":data                    
                    }
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))



            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
    














class FilterTicket(GenericAPIView):
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

        ticket_objs=Ticket.objects.filter(isActive=True,og_code=og_code)
        if request.user.user_type == 2:
            print("Organization Admin",)
        elif request.user.user_type == 3:
            if request.user.is_parent_college==True and request.user.is_member == False and request.user.member_of in ['',None,'None']:
                print("Parent college Admin",)
                ticket_objs=ticket_objs.filter(Q(parent_college_id=request.user.id)|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
            elif request.user.is_parent_college == False and request.user.is_member == True and request.user.member_of != '':
                print("Parent college Member",)
                ticket_objs=ticket_objs.filter(Q(parent_college_id=request.user.member_of)|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))

            else:
                ticket_objs=ticket_objs.none()
                print("hii",
                      request.user.is_parent_college,
                      request.user.is_member,
                      request.user.member_of
                      )
                
        elif request.user.user_type == 4:
            if request.user.is_parent_college == False and request.user.is_member == False  and request.user.parent_college != '':
                print("Sub college Admin",)
                ticket_objs=ticket_objs.filter(Q(sub_college_id=str(request.user.id))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')


                

            elif request.user.is_parent_college == False and request.user.is_member == True  and request.user.parent_college != '':
                print("Sub college Member",request.user.parent_college)
                ticket_objs=ticket_objs.filter(Q(sub_college_id=str(request.user.member_of))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))
        elif request.user.user_type == 5:
                user_obj=UserAdmin.objects.filter(id=request.user.parent_college).first()
                if user_obj is not None:
                    if user_obj.is_parent_college==True and user_obj.user_type==3:
                        ticket_objs=ticket_objs.filter(Q(parent_college_id=str(user_obj.id))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                        assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                        ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))
                        print("Parent college Faculty",)
                    elif user_obj.is_parent_college==False and user_obj.user_type==4:
                        ticket_objs=ticket_objs.filter(Q(sub_college_id=str(user_obj.id))|Q(raiseby=str(request.user.id))).order_by('id').distinct('id')
                        assign_tickets_ids=list(TicketAssign.objects.filter(userid=str(request.user.id),active=True).values_list('ticket',flat=True))
                        ticket_objs=ticket_objs.filter(Q(id__in=assign_tickets_ids)|Q(raiseby=str(request.user.id)))
                        print("Sub college Faculty",)
        else:
            ticket_objs=ticket_objs.none()






        
        status=request_data.get('status')
        if status is not None and status !='':
            ticket_objs=ticket_objs.filter(status=status) 
        

        raiseby=request_data.get('raiseby')
        if raiseby is not None and raiseby !='':
            ticket_objs=ticket_objs.filter(raiseby=raiseby) 
        
        priority=request_data.get('priority_search')
        if priority is not None and priority !='':
            ticket_objs=ticket_objs.filter(priority=priority) 



        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            ticket_objs=ticket_objs.filter(createdAt__gte=start_date) 
        
        end_date=request_data.get('enddate')


        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            ticket_objs=ticket_objs.filter(createdAt__lte=cend_date) 

        subject_search=request_data.get('subject_search')
        if subject_search is not None and subject_search !='':
            ticket_objs=ticket_objs.filter(subject__icontains=subject_search) 


        if ticket_objs.exists():
            page4 = self.paginate_queryset(ticket_objs)
            serializer=TicketSerializer(page4,many=True)


            if encryped_header == "1" :
                for ticket in serializer.data:
                    if ticket['raiseby']==str(request.user.id):
                        ticket['requestername']="You"
                    elif ticket['requestername'] == 'None' or  ticket['requestername'] =='' or ticket['requestername'] is None:
                        user_obj=UserAdmin.objects.filter(id=str(ticket['raiseby'])).first()
                        if user_obj is not None:
                            ticket['requestername']=user_obj.name
                        
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

class AssignUserToTicket(GenericAPIView):
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
        ticket=request_data.get('ticket')
        if ticket is None or ticket =='':
            msg="Please provide ticket id "
            validation_status=False 
            
            
            
        userid=request_data.get('userid')
        if userid is None or userid =='':
            msg="Please select ticket user id"
            validation_status=False 
            
        
        data={}
        data['userid']=str(userid)

        user_obj=UserAdmin.objects.filter(id=str(userid),isActive=True).first()
        if user_obj is None:
            msg="provided user is not active"
            validation_status=False 

        if (user_obj.user_type == 5) or (user_obj.user_type == 3 and user_obj.is_member == True) or (user_obj.user_type == 4 and user_obj.is_member == True) or (user_obj.user_type == 2 and user_obj.is_member == True):
            data['username']=str(user_obj.first_name) +' '+str(user_obj.last_name)
        else:
            data['username']=user_obj.name
        
        data['ticket']=ticket
        data['active']=True
        data['updatedAt'] = timezone.now()

        previous_user_activate=False
        previous_assign_user_obj=TicketAssign.objects.filter(ticket=ticket,userid=str(userid)).first()
        if previous_assign_user_obj is not None:
            if previous_assign_user_obj.active==True:
                msg="User is already assigned to this ticket and active."
                validation_status=False 
            else:
                previous_user_activate=True


        if validation_status:
            deactivate_assign_user=TicketAssign.objects.filter(ticket=ticket,active=True).update(active=False)
            if previous_user_activate:
                serializer=TicketAssignSerializer(previous_assign_user_obj,data=data,partial=True)
                msg='Previous assign user is activated'
            else:
                serializer=TicketAssignSerializer(data=data)
                msg='New user assign to ticket'



            if serializer.is_valid():
                serializer.save()
                response_={
                        "n": 1,
                        "msg": msg,
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

class AssignUserList(GenericAPIView):
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
        userobj = UserAdmin.objects.filter(isActive=True,og_code=og_code,).order_by('-id')



        active_user_id=''

        if request_data['ticket'] is not None and request_data['ticket'] !='':
            ticket=request_data['ticket']
            previous_assign_user_obj=TicketAssign.objects.filter(ticket=ticket,active=True).first()
            if previous_assign_user_obj is not None:
                active_user_id=previous_assign_user_obj.userid

            ticket_obj=Ticket.objects.filter(id=request_data['ticket']).first()
            if ticket_obj is not None:
                
                
                if request.user.user_type == 2:
                    # if request.user.is_parent_college==false and request.user.is_member == False and request.user.member_of in ['',None,'None']:
                    member_type = request.user.user_type
                    if request.user.member_of is None :
                        member_of = str(request.user.id)
                    else:
                        member_of = str(request.user.member_of)
                    member_ids = list(UserAdmin.objects.filter(Q(member_type = member_type,member_of=member_of,og_code=og_code,is_member=True,isActive=True)|Q(id=member_of)).values_list('id',flat=True))
                    userobj=userobj.filter(Q(is_parent_college=True)|Q(id__in=member_ids)).exclude(id=str(request.user.id)).order_by('id').distinct('id')
                elif request.user.user_type == 3:
                    if request.user.is_parent_college==True and request.user.is_member == False and request.user.member_of in ['',None,'None']:
                        member_type = request.user.user_type
                        if request.user.member_of is None :
                            member_of = str(request.user.id)
                        else:
                            member_of = str(request.user.member_of)


                        member_ids = list(UserAdmin.objects.filter(Q(member_type = member_type,member_of=member_of,is_member=True,isActive=True)|Q(id=member_of)).values_list('id',flat=True))

                        org_admin_ids=list(UserAdmin.objects.filter(Q(user_type = 2,is_member=False,isActive=True,og_code=og_code)).values_list('id',flat=True))

                        sub_training_admin_ids = list(UserAdmin.objects.filter(Q(user_type = 4,parent_college=str(request.user.id),is_member=False,isActive=True)).values_list('id',flat=True))

                        # tc_members+orgadmin+subtrainingadmin+tc_faculty
                        faculty_ids = list(UserAdmin.objects.filter(Q(user_type =5,parent_college=str(request.user.id),is_member=False,isActive=True)).values_list('id',flat=True))

                        user_ids=member_ids+org_admin_ids+sub_training_admin_ids+faculty_ids
                        userobj=userobj.filter(Q(id__in=user_ids)).exclude(id=str(request.user.id)).order_by('id').distinct('id')

                        
                    elif request.user.is_parent_college == False and request.user.is_member == True and request.user.member_of != '':
                        print("Parent college Member",)
                        userobj=userobj.none()


                    else:
                        userobj=userobj.none()
                elif request.user.user_type == 4:
                    if request.user.is_parent_college == False and request.user.is_member == False  and request.user.parent_college != '':
                        
                        print("Sub college Admin",)
                        member_type = request.user.user_type
                        if request.user.member_of is None :
                            member_of = str(request.user.id)
                        else:
                            member_of = str(request.user.member_of)


                        member_ids = list(UserAdmin.objects.filter(Q(member_type = member_type,member_of=member_of,is_member=True,isActive=True)|Q(id=member_of)).values_list('id',flat=True))

                        ptc_admin_ids=list(UserAdmin.objects.filter(user_type = 3,is_parent_college=True,isActive=True,id=str(request.user.parent_college)).values_list('id',flat=True))



                        faculty_ids = list(UserAdmin.objects.filter(Q(user_type = 5,parent_college=str(request.user.id),is_member=False,isActive=True)).values_list('id',flat=True))
                        # stc_members+ptc_admin+stc_faculty

                        user_ids=member_ids+ptc_admin_ids+faculty_ids
                        userobj=userobj.filter(id__in=user_ids).exclude(id=str(request.user.id)).order_by('id').distinct('id')

                    elif request.user.is_parent_college == False and request.user.is_member == True  and request.user.parent_college != '':
                        print("Sub college Member",)
                        userobj=userobj.none()
                elif request.user.user_type == 5:
                    userobj=userobj.none()
                else:
                    userobj=userobj.none()

                userobj=userobj.exclude(id=str(ticket_obj.raiseby))
                userobj=userobj.exclude(id=str(request.user.id))
                assign_user_obj=TicketAssign.objects.filter(ticket=ticket_obj.id,active=True).order_by('-id').first()
                if assign_user_obj is not None:
                    userobj=userobj.exclude(id=str(assign_user_obj.userid))




        userser = UserAdminSerializer(userobj,many=True)
        for i in userser.data:
            if i['name']=='' or i['name'] is None:
                i['name']=i['first_name'] +' '+i['last_name']
            country_object = Country.objects.filter(id=i['country']).first()
            if country_object is not None:
                i['country_name'] = country_object.name
            else:
                i['country_name'] = ""


        response_={
                    "n": 1,
                    "msg": 'user list found successfully',
                    "data":userser.data  ,                      
                    "active_user_id":active_user_id                        
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
       
class TicketAssignUserList(GenericAPIView):
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
        assigned_user_ids=TicketAssign.objects.filter(ticket=request_data['ticket'],isActive=True)
        serializer=CustomTicketAssignSerializer(assigned_user_ids,many=True)
        for i in serializer.data:
            # date_str=str(i['createdAt']).split('T')[0]
            # time_str=str(i['createdAt']).split('T')[0]

            # i['createdAt']= date_str+' '+ time_str  # Jan 14, 2025 · 10:00 AM format
            i['createdAt_formatted']=convert_iso_to_human_readable(i['updatedAt'])
                # 2025-07-04T17:27:02.903305+05:30

        response_={
                    "n": 1,
                    "msg": 'user list found successfully',
                    "data":serializer.data  ,                      
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
       
class GetTicketActivity(GenericAPIView):
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
        activity_objs=TicketActivity.objects.filter(ticket=request_data['ticket'],isActive=True).order_by('createdAt')
        serializer=CustomTicketActivitySerializer(activity_objs,many=True)

        response_={
                    "n": 1,
                    "msg": 'Ticket activity found successfully',
                    "data":serializer.data  , 
                    'logined_userid':str(request.user.id)                     
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
    
class AddTicketActivity(GenericAPIView):
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
        ticket=request_data.get('ticket')
        if ticket is None or ticket =='':
            msg="Please provide ticket id "
            validation_status=False 
        attachment=request_data.get('attachment')

        comment=request_data.get('comment')
        if comment is None or comment =='' and attachment is None or attachment =='':
            msg="Please provide valid comment"
            validation_status=False 
        
          

        data=request_data.copy()
        data['userid']=str(request.user.id)



        if (request.user.user_type == 5) or (request.user.user_type == 3 and request.user.is_member == True) or (request.user.user_type == 4 and request.user.is_member == True) or (request.user.user_type == 2 and request.user.is_member == True):
            data['username']=str(request.user.first_name) +' '+str(request.user.last_name)
        else:
            data['username']=request.user.name

        data['isActive']=True
        if request.FILES.get('attachment') is not None and request.FILES.get('attachment') !='':
            data['attachment']=request.FILES.get('attachment')

        if validation_status:
            serializer=TicketActivitySerializer(data=data)
            if serializer.is_valid():
                serializer.save()

                response_={
                            "n": 1,
                            "msg": 'Ticket activity added successfully',
                            "data":serializer.data  ,                      
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


class GetTicketAllAttachments(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response







        activity_objs=TicketActivity.objects.filter(ticket=request_data['ticket'],isActive=True).exclude(Q(attachment__isnull=True)|Q(attachment='')|Q(attachment=None)).order_by('-createdAt')
        activity_serializer=CustomTicketActivitySerializer(activity_objs,many=True)
        
        ticketsattachments_objs=TicketAttachments.objects.filter(ticket=request_data['ticket'],isActive=True).order_by('-createdAt')
        tickets_serializer=CustomTicketAttachmentsSerializer(ticketsattachments_objs,many=True)

        data=activity_serializer.data+tickets_serializer.data
        for i in data:
            i['filename'], i['file_extension'] = extract_filename_and_extension(i['attachment'])

        response_={
                    "n": 1,
                    "msg": 'Ticket attachments found successfully',
                    "data":data, 
                }

        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
    

class MarkTicketAsFAQ(GenericAPIView):
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

        ticket=request_data.get('ticket')
        if ticket is None or ticket =='':
            msg="Please provide ticket id "
            validation_status=False 

        category=request_data.get('categoryId')
        if category is None or category =='':
            msg="Please provide category id "
            validation_status=False 

        department=request_data.get('departmentId')
        if department is None or department =='':
            msg="Please provide department id "
            validation_status=False 

        tags=request_data.get('tags')
        if tags is None or tags =='':
            msg="Please provide tags "
            validation_status=False 

        # attachment=request_data.get('attachment')
        # if attachment is None or attachment =='':
        #     msg="Please provide valid attachment"
        #     validation_status=False 


        data['isActive']=True
        if request.FILES.get('attachment') is not None and request.FILES.get('attachment') !='':
            data['attachment']=request.FILES.get('attachment')

        if validation_status:

            update_obj=FAQTicket.objects.filter(ticket=ticket,isActive=True).first()
            if update_obj is not None:
                serializer=FAQTicketSerializer(update_obj,data=data,partial=True)
            else:
                serializer=FAQTicketSerializer(data=data)



            if serializer.is_valid():
                serializer.save()

                response_={
                            "n": 1,
                            "msg": 'Ticket marked as faq successfully',
                            "data":serializer.data  ,                      
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
