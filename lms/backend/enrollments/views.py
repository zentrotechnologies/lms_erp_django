from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import *
from enrollments.serializers import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.jwt import UserAdminJWTAuthentication
from candidate.jwt import CandidateJWTAuthentication
from adminauth.models import *
# Create your views here.
from adminauth.views import save_file
from feedback.validation import *
from candidate.serializers import *
from course.models import *
from course.serializers import *
from schedule.models import *
from schedule.serializers import *
from django.template.loader import get_template
from django.core.mail import EmailMessage

# CATEGORY
class AddEnrollments(GenericAPIView):
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
        
        data['course'] = request_data.get('course')
        data['schedule'] = request_data.get('schedule')
        data['college_id'] = str(request.user.id)
        data['enrollments_status'] = 1
        
        if request_data.get('candidate') is not None and request_data.get('candidate') !="":
            
            for e in request_data.get('candidate'):
                obj = Candidate.objects.filter(id=e,isActive=True).first()
                data['candidate'] = e
                if obj is not None and obj != "":
                    fser = EnrollmentsSerializer(data=data)
                    if fser.is_valid():
                        fser.save()
                        payment_array = {
                            'candidate':data['candidate'],
                            'course':data['course'],
                            'schedule':data['schedule'],
                            'id':fser.data['id'],
                            'college_id':data['college_id']
                        }
                        base_data_to_serialize = convert_decimals_to_float(payment_array)
                        encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
                        
                        payment_link = candidateURL + '/' + encrypt_base_test_examination_link
                        # subject = "Course payment link"
                        # data2 = {"subject": subject,"template":'pay-link-mail.html',
                        #     'email':'sushmakarki0722@gmail.com','payment_link':payment_link}
                        # #'email':obj.email
                        # template = get_template(data2['template'])
                        # message = template.render(data2)
                        # sendmailtouser = EmailMessage(data2, message)
                        # sendmailtouser.send()
                        
                        dicti = {'email': 'ss2766686@gmail.com','payment_link': payment_link}

                        message = get_template(
                            'pay-link-mail.html').render(dicti)
                        msg = EmailMessage(
                            'Candidate Payment Link!',
                            message,
                            EMAIL_HOST_USER,
                            ['ss2766686@gmail.com'],
                        )
                        msg.content_subtype = "html"  # Main content is now text/html
                        msg.send()
                        
                        response_={
                            'status':'success',
                            'msg':'Link send successfully.',
                            'data': []
                        }
                        if encryped_header == "1":
                            data_to_serialize = convert_decimals_to_float(response_)
                            encdata = encrypt_data(json.dumps(data_to_serialize))
                            return Response(encdata,status=200)
                        else:
                            return Response(response_,status=200)
                        
                    else:
                        print('error',fser.errors)
                        # response_={
                        #     "status": 'error',
                        #     'msg':"Enrollments not added.",
                        #     'data':{}
                        # }    
                        # if encryped_header == "1" :
                        #     data_to_serialize = convert_decimals_to_float(response_)
                        #     encdata = encrypt_data(json.dumps(data_to_serialize))
                        #     return Response(encdata,status=200)
                        # else:
                        #     return Response(response_,status=200)
                else:
                    response_={
                        "status": 'error',
                        'msg':"Enrollments not added.",
                        'data':{}
                    }    
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            response_={
                "status": 1,
                'msg':"Enrollments added successfully.",
                'data':{}
            }    
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


            
class EnrollmentsList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        enrollments_status = request_data.get('enrollments_status')
       
        enroll_status =''
        if enrollments_status == 'requests':
            enroll_status = '1'
        elif enrollments_status == 'approved':
            enroll_status = '2'
        elif enrollments_status == 'enrolldeclined':
            enroll_status = '3'
        elif enrollments_status == 'profile_pending':
            enroll_status = '4'
        elif enrollments_status == 'waiting':
            enroll_status = '5'
        
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        
        member_type = adminobj.user_type
        if adminobj.member_of is None :
            member_of = str(adminobj.id)
        else:
            member_of = str(adminobj.member_of)
             
        # obj = Enrollments.objects.filter(isActive=True,candidate__in = list(Candidate.objects.filter(enrollments_status=enroll_status).values_list('id',flat=True)))
        obj = Enrollments.objects.filter(isActive=True,college_id=member_of,enrollments_status=enroll_status,id__in=list(EnrollPayment.objects.filter(isActive=True).values_list('enrollment_id',flat=True)))
        if enroll_status == '3':
            obj = Enrollments.objects.filter(isActive=True,college_id=member_of,enrollments_status=enroll_status).order_by('-updatedAt')
        ser = EnrollmentsSerializer(obj,many=True)
        
        for c in ser.data:
            
                
            course_object = Course.objects.filter(isActive=True,id=c['course']).first()
            if course_object is not None:
                c['course_name'] = course_object.course_name
            else:
                c['course_name'] = ""   
            
            cobj = Candidate.objects.filter(id=c['candidate']).first()
            c_ser = CandidateSerializer(cobj)
            c['candidatedata'] = c_ser.data
            c['createdAt'] = c['createdAt'].split('T')[0].split('-')[0]+"-"+c['createdAt'].split('T')[0].split('-')[1]+"-"+c['createdAt'].split('T')[0].split('-')[2]
            c['createdAt'] = datefilterchangeformat(c['createdAt'])
        response_={
            "n": 1,
            'msg':'Enrollments found successfully.',
            'data': ser.data
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
    
    
    # def post(self,request):
    #     encryped_header = ""
    #     if 'encrypted' in request.headers.keys():
    #         encryped_header = request.headers.get('encrypted')
            
    #     request_data, error_response = handle_request_body(request)
    #     if error_response:
    #         return error_response
              
    #     id = request_data.get('id')
    #     if id is not None and id != "":
    #         catobj=Enrollments.objects.filter(id=id,isActive=True).first()
    #         if catobj is not None:
    #             serializer = EnrollmentsSerializer(catobj)
                
    #             response_ = {
    #                 "n": 1,
    #                 'msg':'Enrollments Details Found.',
    #                 'data':serializer.data
    #             }
    #             if encryped_header == "1" :
    #                 data_to_serialize = convert_decimals_to_float(response_)
    #                 encdata = encrypt_data(json.dumps(data_to_serialize))
    #                 return Response(encdata,status=200)
    #             else:
    #                 return Response(response_,status=200)
    #         else:
    #             response_={
    #                 "n": 0,
    #                 'msg':'No Data FOund.',
    #                 'data':{}
    #             }
    #             if encryped_header == "1" :
    #                 data_to_serialize = convert_decimals_to_float(response_)
    #                 encdata = encrypt_data(json.dumps(data_to_serialize))
    #                 return Response(encdata,status=200)
    #             else:
    #                 return Response(response_,status=200)
    #     else:
    #         response_={
    #             "n": 0,
    #             'msg':'id is required.',
    #             'data':{}
    #         }
    #         if encryped_header == "1" :
    #             data_to_serialize = convert_decimals_to_float(response_)
    #             encdata = encrypt_data(json.dumps(data_to_serialize))
    #             return Response(encdata,status=200)
    #         else:
    #             return Response(response_,status=200)
        

            
class AdmissionRequestList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        enrollments_status = request_data.get('enrollments_status')
       
        # enroll_status =''
        # if enrollments_status == 'requests':
        #     enroll_status = '1'
        # elif enrollments_status == 'approved':
        #     enroll_status = '2'
        # elif enrollments_status == 'enrolldeclined':
        #     enroll_status = '3'
        # elif enrollments_status == 'profile_pending':
        #     enroll_status = '4'
        # elif enrollments_status == 'waiting':
        #     enroll_status = '5'
            
        # obj = Enrollments.objects.filter(isActive=True,candidate__in = list(Candidate.objects.filter(enrollments_status=enroll_status).values_list('id',flat=True)))
        
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        
        member_type = adminobj.user_type
        if adminobj.member_of is None :
            member_of = str(adminobj.id)
        else:
            member_of = str(adminobj.member_of)
        
        obj = Enrollments.objects.filter(isActive=True,college_id=member_of,enrollments_status='1')
        
        ser = EnrollmentsSerializer(obj,many=True)
        for c in ser.data:
            course_object = Course.objects.filter(isActive=True,id=c['course']).first()
            if course_object is not None:
                c['course_name'] = course_object.course_name
            else:
                c['course_name'] = ""   
            
            cobj = Candidate.objects.filter(id=c['candidate']).first()
            c_ser = CandidateSerializer(cobj)
            c['candidatedata'] = c_ser.data
            c['createdAt'] = c['createdAt'].split('T')[0].split('-')[0]+"-"+c['createdAt'].split('T')[0].split('-')[1]+"-"+c['createdAt'].split('T')[0].split('-')[2]
            c['createdAt'] = datefilterchangeformat(c['createdAt'])
        response_={
            "n": 1,
            'msg':'Enrollments found successfully.',
            'data': ser.data
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
      
        
class ApprovedEnrollmentStatus(GenericAPIView):
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
        if id is not None:
            candiobj = Enrollments.objects.filter(id=id,isActive=True).first()
            if candiobj is not None:
           
                candiobj.enrollments_status = 2
                candiobj.updatedAt = timezone.now()
                candiobj.save()
                response_={
                    'n':1,
                    'msg':'Application approved successfully',
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
                    'msg':'Data not found.',
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
                'msg':'ID is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 

class DeclinedEnrollments(GenericAPIView):
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
        declined_rsn = request_data.get('declined_rsn')
        
        if id is not None:
            enroll_obj = Enrollments.objects.filter(id=id,isActive=True).first()
            if enroll_obj is not None:
                enroll_obj.declined_rsn = declined_rsn
                enroll_obj.enrollments_status = 3
                enroll_obj.updatedAt = timezone.now()
                enroll_obj.updatedBy = str(request.user.id)
                enroll_obj.save()
                response_={
                    'n':1,
                    'msg':'Application declined successfully.',
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
                    'msg':'Data not found.',
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
                'msg':'ID is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 
 

class ProfilePendingEnrollments(GenericAPIView):
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
        if id is not None:
            enroll_obj = Enrollments.objects.filter(id=id,isActive=True).first()
            if enroll_obj is not None:
                enroll_obj.enrollments_status = 4
                enroll_obj.updatedAt = timezone.now()
                enroll_obj.save()
                response_={
                    'n':1,
                    'msg':'Status changed successfully.',
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
                    'msg':'Data not found.',
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
                'msg':'ID is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 
# Payment

class PaymentEnrollments(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication,CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data={}
        data['course_id'] = request_data.get('course_id')
        data['schedule'] = request_data.get('schedule')
        data['college_id'] = request_data.get('college_id')
        data['billing_address'] = request_data.get('billing_address')
        data['city'] = request_data.get('city')
        data['state'] = request_data.get('schedule')
        data['country'] = request_data.get('country')
        data['transaction_id'] = request_data.get('transaction_id')
        data['subtotal_amount'] = request_data.get('subtotal_amount')
        data['discount_amount'] = request_data.get('discount_amount')
        data['final_amount'] = request_data.get('final_amount')
        data['currency_type'] = request_data.get('currency_type')
        data['pincode'] = request_data.get('pincode')
        data['source'] = request_data.get('source')
        data['enrollments_status'] = 1
        data['email'] = request_data.get('email')
        
        if request_data.get('candidate') is not None and request_data.get('candidate') !="":
            fser = EnrollmentsSerializer(data=data)
            if fser.is_valid():
                fser.save()
                EnrollPayment.objects.create(
                    course_id = data['course_id'],
                    schedule = data['schedule'],
                    college_id = data['college_id'],
                    billing_address = data['billing_address'],
                    city = data['city'],
                    state = data['state'],
                    country = data['country'],
                    transaction_id = data['transaction_id'],
                    subtotal_amount = data['subtotal_amount'],
                    discount_amount = data['discount_amount'],
                    final_amount = data['final_amount'],
                    currency_type = data['currency_type'],
                    pincode = data['pincode'],
                    source = data['source'],
                    enrollment_id = fser.data['id']
                )
                
                response_={
                    "n": 1,
                    'msg':"Payment added successfully.",
                    'data':fser.data
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
                    'msg':"Payment not added.",
                    'data':{}
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
                'msg':"Candidate id is required.",
                'data':{}
            }    
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

        
class SendPaymentLink(GenericAPIView):
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
        data['email'] = request_data.get('email')
        data['course_id'] = request_data.get('course_id')
        data['college_id'] = request_data.get('college_id')
        
        canobj = Candidate.objects.filter(email=data['email'],isActive=True).first()
        if not canobj:
            response_={
                "n": 0,
                'msg':"Candidate not found with given email.",
                'data':{}
            }
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        subject = "Course payment link"
        data2 = {"subject": subject,"template": 'https://navis-candidate.onerooftechnologiesllp.com/enroll-now.html',
                'email':canobj.email}
    
        # message = get_template(
        #     data2['template'], data2)
        template = get_template(data2['template'])
        message = template.render(data2)
        sendmailtouser = EmailMessage(data2, message)
        # sendmailtouser.content_subtype = "html"  # To send as HTML
        sendmailtouser.send()
        response_={
            "n": 1,
            'msg':"Payment link send in email successfully",
            'data':{}
        }    
        if encryped_header == "1":
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
 


class SavePayment(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data={}
        data['course'] = request_data.get('courseid')
        data['schedule'] = request_data.get('scheduleid')
        data['college_id'] = request_data.get('college_id')
        data['candidate'] = request_data.get('candidateid')
        data['enrollments_status'] = '2'
        data['source'] = 'Candidate website'
        data['isActive'] = True
        data['createdBy'] = str(request.user.id)

        countryid = request_data.get('countryid')
        stateid = request_data.get('stateid')
        payment_method = request_data.get('payment_method')
        transaction_id = request_data.get('transaction_id')
        card_number = request_data.get('card_number')
        expiry_date = request_data.get('expiry_date') or None
        cvc = request_data.get('cvc')
        name_on_card = request_data.get('name_on_card')
        amount = request_data.get('amount')
        

        if request_data.get('candidateid') is not None and request_data.get('candidateid') !="":
            enrollser = Enrollments.objects.filter(candidate=data['candidate'],isActive=True,schedule=data['schedule'],college_id = data['college_id'],course=data['course'],enrollments_status='2').first()
            if enrollser is not None:
                response_={
                    "n": 0,
                    'msg':"You already enrolled for this course.",
                    'data':{}
                }    
                if encryped_header == "1":
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                
            Schobj = Schedule.objects.filter(id=data['schedule'],action_status='Approved').first()
            if Schobj is not None:

                schstartdate = Schobj.start_date
                schenddate =  Schobj.end_date

                enrollanothercourseobj = Enrollments.objects.filter(candidate=data['candidate'],isActive=True,enrollments_status='2',schedule__in=list(Schedule.objects.filter(start_date__lte=schenddate,end_date__gte=schstartdate,action_status="Approved").values_list('id',flat=True)),)

                if enrollanothercourseobj.exists():
                    response_={
                        "n": 0,
                        'msg':"Candidate already Enrolled for another course.",
                        'data':{}
                    }    
                    if encryped_header == "1":
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)



            fser = EnrollmentsSerializer(data=data)
            if fser.is_valid():
                fser.save()

                EnrollPayment.objects.create(
                    course_id = data['course'],
                    schedule_id = data['schedule'],
                    college_id = data['college_id'],
                    billing_address = '',
                    city = None,
                    state = stateid,
                    country = countryid,
                    transaction_id = transaction_id,
                    subtotal_amount =amount,
                    discount_amount = 0,
                    final_amount =amount,
                    currency_type = 'Dollars',
                    pincode ='',
                    enrollment_id = fser.data['id'],
                    payment_method = payment_method,
                    card_number = card_number,
                    expiry_date=expiry_date,
                    cvc=cvc,
                    name_on_card =name_on_card

                )
                
                response_={
                    "n": 1,
                    'msg':"Payment added successfully.",
                    'data':fser.data
                }    
                if encryped_header == "1":
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                print("error",fser.errors)
                response_={
                    "n": 0,
                    'msg':"Payment not added.",
                    'data':{}
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
                'msg':"Candidate id is required.",
                'data':{}
            }    
            if encryped_header == "1":
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
  