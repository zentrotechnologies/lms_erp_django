from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from .serializers import *
from exam.models import *
from exam.serializers import *
from master.serializers import *
from lms.settings import *
from usermanagement.serializers import *
from django.contrib.auth.hashers import make_password,check_password
from .jwt import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.jwt import *
from urllib.parse import unquote
from django.core.files.storage import default_storage
from django.db.models import Q
from random import randint
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from course.models import *
from adminauth.common import convertcreationdate
from adminauth.models import *
from adminauth.serializers import *
from course.serializers import *
from adminauth.views import save_file,sanitize_filename
from rules.models import *
from rules.serializers import *
from datetime import date  # Make sure this import is at the top of your views.py
from enrollments.models import *
from enrollments.serializers import *
def calculate_age(dob):
    """
    Calculate the current age based on date of birth.
    
    Args:
        dob (datetime.date or str): Date of birth
        
    Returns:
        int: Current age in years
    """
    if isinstance(dob, str):
        # If dob is a string, parse it first
        from datetime import datetime
        dob = datetime.strptime(dob, "%Y-%m-%d").date()
    
    today = date.today()
    age = today.year - dob.year
    
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    
    return age



def save_file(folder_path,uploaded_file,request):            
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, uploaded_file.name)
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
    file_url=request.build_absolute_uri(settings.MEDIA_URL + relative_file_path.replace("\\", "/"))
    return file_url



class CandidateLogin(GenericAPIView):
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request_data.get('email')
        password = request_data.get('password')
        
        if email is None or email == "":
            response_={
                "n": 0,                    
                "msg": 'Email is required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        if password is None or password == "":
            response_={
                "n": 0,                    
                "msg": 'Password is required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        cd_object = Candidate.objects.filter(isActive=True,email=email).first()
        if cd_object is None:
            response_={
                        "n": 0,                    
                        "msg": 'candidate not found',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            cd_ser = CandidateSerializer(cd_object)

            if str(password) == str(cd_object.password):
                deactive_cd_token = CandidateToken.objects.filter(user_id=cd_object.id).update(isActive=False)           
                cd_token= CandidateToken.objects.create(user_id=cd_object.id,authToken=cd_object.token)
                response_={
                        "n": 1,                    
                        "msg": 'Candidate logged in successfully',
                        "token":cd_token.authToken,
                        "data":cd_ser.data,      
                                 
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
                        "msg": 'Incorrect password',
                        "data":[],                  
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)


class CandidateExamPortalLogin(GenericAPIView):
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request_data.get('email')
        password = request_data.get('password')
        
        if email is None or email == "":
            response_={
                "n": 0,                    
                "msg": 'Email is required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        if password is None or password == "":
            response_={
                "n": 0,                    
                "msg": 'Password is required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        cd_object = Candidate.objects.filter(isActive=True,email=email).first()
        if cd_object is None:
            response_={
                        "n": 0,                    
                        "msg": 'candidate not found',
                        "data":[],                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            cd_ser = CandidateSerializer(cd_object)

            if str(password) == str(cd_object.password):
                deactive_cd_token = CandidateToken.objects.filter(user_id=cd_object.id).update(isActive=False)           
                cd_token= CandidateToken.objects.create(user_id=cd_object.id,authToken=cd_object.token)
                
                today_date = date.today()
                current_time = datetime.now().strftime("%H:%M")
                one_hour_before = (datetime.now() - timedelta(hours=1)).strftime("%H:%M")
                one_hour_after = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
               
                
                todays_exam_schedule_ids= list(ScheduleExam.objects.filter(
                    isActive=True,
                    schedule_exam_date=str(today_date),
                    # start_time__gte=one_hour_after,
                    # end_time__lte=current_time,

                ).order_by('id').values_list('id', flat=True))


                exam_link_object = ExamCandidateSetRelation.objects.filter(
                    isActive=True,
                    exam_schedule_id__in=todays_exam_schedule_ids,
                    candidate_id=cd_object.id
                    ).first()

                exam_expired = False

                encrypt_base_test_examination_link1=''
                finally_submit = False
                if exam_link_object is not None:
                    schedule_obj= ScheduleExam.objects.filter(id=exam_link_object.exam_schedule_id,isActive=True).first()
                    if schedule_obj is not None:
                        finally_submit_obj=ExamCandidateResult.objects.filter(candidate_id=cd_object.id, exam_schedule_id=exam_link_object.exam_schedule_id).first()
                        if finally_submit_obj is not None:
                            finally_submit = finally_submit_obj.final_submit
                        else:
                            finally_submit = False


                        # Combine date and time strings and parse into datetime object
                        exam_date_str = f"{schedule_obj.schedule_exam_date} {schedule_obj.end_time}"
                        if len(exam_date_str.split(':')) == 2:
                            exam_date_str += ':00'

                        end_date_time = datetime.strptime(exam_date_str, '%Y-%m-%d %H:%M:%S')  # Adjust format to match your data

                        current_date_time = datetime.now()

                        if end_date_time < current_date_time:
                            exam_expired = True

                        exam_array = {
                            "exam_schedule_id" : exam_link_object.exam_schedule_id,
                            "exam_id" : exam_link_object.exam_id,
                            "exam_set" : exam_link_object.exam_set,
                            "candidate_id" : exam_link_object.candidate_id,
                            "candidate_exam_id":exam_link_object.id,
                            "exam_start_time": str(schedule_obj.start_time),
                            "exam_end_time": str(schedule_obj.end_time),
                            "exam_start_date": str(schedule_obj.schedule_exam_date),
                            "exam_duration": str(schedule_obj.exam_duration),
                        }
                        base_data_to_serialize = convert_decimals_to_float(exam_array)
                        encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))




                    encrypt_base_test_examination_link1 = trainingcenterURL+'/exam/candidate-exam-instructions/'+encrypt_base_test_examination_link




                response_={
                        "n": 1,                    
                        "msg": 'Candidate logged in successfully',
                        "token":cd_token.authToken,
                        "data":cd_ser.data,
                        "encrypt_base_test_examination_link": encrypt_base_test_examination_link1,
                        "finally_submit":finally_submit,
                        "exam_expired":exam_expired

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
                        "msg": 'Incorrect password',
                        "data":[],                  
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)



class CandidateLogout(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        token = request_data.get('token')
        if token is not None and token !="":
            cd_tokenobj = CandidateToken.objects.filter(authToken=token,isActive=True).first()
            if cd_tokenobj is not None:
                cd_tokenobj.isActive = False
                cd_tokenobj.save()
                response_={
                    "n": 1,
                    "msg": 'Logout Successful!',
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
                    "msg": 'token not found',
                    "data":[],                  
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
                "msg": 'token required',
                "data":[],                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class AddCandidate(GenericAPIView):
    
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
        data['profile_pic'] = request.FILES.get('profile_pic')
        data['first_name'] = request_data.get('first_name')
        data['middle_name'] = request_data.get('middle_name')
        data['last_name'] = request_data.get('last_name')
        data['email'] = request_data.get('email')
        data['mobilenumber'] = request_data.get('mobilenumber')
        data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber')
        data['highest_qualification'] = request_data.get('highest_qualification')
        data['qualification_year'] = request_data.get('qualification_year')
        data['dob'] = request_data.get('dob')
        data['passport_expiry_date'] = request_data.get('passport_expiry_date')
        data['passport_number'] = request_data.get('passport_number')
        data['nationality'] = request_data.get('nationality')
        # 
        data['city'] = request_data.get('city')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['pincode'] = request_data.get('pincode')
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        # 
        data['vessel_name'] = request_data.get('vessel_name')
        data['next_vessel'] = request_data.get('next_vessel')
        data['sign_on_date'] = request_data.get('sign_on_date')
        data['sign_of_date'] = request_data.get('sign_of_date')
        data['seaman_book_number'] = request_data.get('seaman_book_number')
        data['department'] = request_data.get('department')
        data['rank'] = request_data.get('rank')

        
        if request.user.member_of != '' and request.user.member_of is not None :
            data['walkin_by']=str(request.user.member_of)
        else:
            data['walkin_by']=str(request.user.id)
    
        data['createdBy']=str(request.user.id)

        
        email_object = Candidate.objects.filter(isActive=True,email=data['email']).first()
        number_object = Candidate.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
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

        crby = str(request.user.id)
        userobj = UserAdmin.objects.filter(id=crby).first()
        if userobj is not None:
            usertype = userobj.user_type
            if usertype is not None and usertype != '':
                roleobj = MainRoles.objects.filter(id=usertype).first()
                source = roleobj.name
            else:
                source = ''
        else:
            source = ''

        if request.FILES.get('profile_pic') is not None and request.FILES.get('profile_pic') !='':
            fileInput=request.FILES.get('profile_pic')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Candidate Profile Pictures')
            file_url=save_file(folder_path,fileInput,request)

            data['profile_pic'] = file_url
        else:
            data['profile_pic'] = ''

        data['source'] = source
        data['createdBy'] = crby
            
        serializer = CandidateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # if any(not value for value in form.cleaned_data.values()):
            #     candidate.status = Candidate.PENDING
            # else:
            #     candidate.status = Candidate.SUBMITTED

            response_={
                "n": 1,
                "msg": 'Candidate registered successfully',
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
            
            
class CandidateList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        exclude_fields = ['last_login', 'updatedAt' ,'createdBy','updatedBy']  # List the fields you want to exclude

        # Get all field names for the model
        fields = Candidate._meta.get_fields()

        # Create a Q object to filter all fields
        query = Q()

        # Loop through each field and check if it's a CharField (string) or nullable field
        for field in fields:
            if field.is_relation:  # Skip related fields (ForeignKey, OneToOne, etc.)
                continue
            if field.name in exclude_fields:  # Skip excluded fields
                continue
            if field.blank or field.null:  # Check if the field allows nulls or blanks
                query |= Q(**{f'{field.name}__isnull': True})  # Check for NULL
                if isinstance(field, models.CharField):  # Check for empty string on CharFields
                    query |= Q(**{f'{field.name}__exact': ""})

        # obj = Candidate.objects.filter(Q(isActive=True,customer_id__icontains=search_keyword),candidate_status=candidate_status)
        cand = request.GET.get('id')
        candidateobj = Candidate.objects.filter(id=cand).first()
        if candidateobj is not None:
            cand_ser =CandidateSerializer(candidateobj)
            country_id=cand_ser.data['country']
            department_id=cand_ser.data['department']
            if cand_ser.data['rank'] !='' and cand_ser.data['rank'] is not None and cand_ser.data['rank'] !='Select rank':
                rank_id=cand_ser.data['rank']
            else:
                rank_id=''
            qualid = cand_ser.data['highest_qualification']
            document_ids=[]


            country_rules_ids=list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))
            if rank_id !='' and rank_id is not None and rank_id !='Select rank':

                find_combination_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=country_rules_ids,departments=department_id,ranks=rank_id,isActive=True).first()
            

                if find_combination_obj is not None:

                    combination_rule_id=find_combination_obj.general_eligibility_rule_id
                
                    min_age_required=find_combination_obj.minimum_age
                    age = calculate_age(cand_ser.data['dob'])

                    qualification_ids=list(GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('educational_qualification_id',flat=True))

                    if age > int(min_age_required) and  int(qualid) in qualification_ids:
                        document_ids=list(GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('document_id',flat=True))
                        if len(document_ids) != 0:
                            documents_required_object = Documents.objects.filter(id__in=document_ids,isActive=True,role=6)
                        else:
                            documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                    else:
                        documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                    
                else:
                    documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
            else:
                documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)


            documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
            
            for d in documents_required_ser.data:
                doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=cand,document_id=d['id']).first()
                if doc_object is not None:
                    d['uploaded_proof'] = doc_object.document_url
                else:
                    d['uploaded_proof'] = ""
               
                   
            country_name = ""
            if cand_ser.data['country'] is not None and cand_ser.data['country'] != "":
                country_object = Country.objects.filter(id=cand_ser.data['country']).first()
                if country_object is not None:
                    country_name = country_object.name
                else:
                    country_name = ""
            else:
                country_name = ""

            city_name = cand_ser.data['city']



            state_name = ""

            if cand_ser.data['state'] is not None and cand_ser.data['state'] != "":
                state_object = State.objects.filter(id=cand_ser.data['state']).first()
                if state_object is not None:
                    state_name = state_object.name
                else:
                    state_name = ""
            else:
                state_name = ""

            if cand_ser.data['department'] is not None and cand_ser.data['department'] != "":
                department_object = Department.objects.filter(id=cand_ser.data['department']).first()
                if department_object is not None:
                    department_name = department_object.department_name
                else:
                    department_name = ""
            else:
                department_name = ""
            if cand_ser.data['rank'] is not None and cand_ser.data['rank'] != "" and cand_ser.data['rank'] !='Select rank':
                rank_object = Rank.objects.filter(id=cand_ser.data['rank']).first()
                if rank_object is not None:
                    rank_name = rank_object.rank
                else:
                    rank_name = ""
            else:
                rank_name = ""

            proof_data = documents_required_ser.data
            state_name = state_name
            country_name = country_name
            serializer_data = cand_ser.data


            serializer_data.update({
                "proof_data":documents_required_ser.data,
                "state_name":state_name,
                "country_name":country_name,
                "department_name":department_name,
                "rank_name":rank_name,
                "city_name":city_name,
                "state_name":state_name,
                # "createdAt":date
            })


            if qualid is not None and qualid !='' and qualid !='Select Qualification':
                EducationalQualificationsobj = EducationalQualifications.objects.filter(id=int(qualid)).first()
                educatser = EducationalQualificationsSerializer(EducationalQualificationsobj)
                educatser_data = educatser.data
                educatser_data.update({
                    'uploaded_certificate' : cand_ser.data['educational_certificate'],
                    'certificate_name' : cand_ser.data['certificate_name']
                })
                # datestring = serializer_data['createdAt']
                # date = datetime.strptime(datestring, "%d %b %Y")
                # createdAt = convertcreationdate(datestring) 

                serializer_data.update({
                    "education_document_data":educatser_data,
                })
                
            response_={
                "n": 1,
                'msg':'Candidate found Successfully.',
                'data':serializer_data
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
        
        exclude_fields = ['last_login', 'updatedAt' ,'createdBy','updatedBy','candidate_status','profile_pic']  # List the fields you want to exclude

        # Get all field names for the model
        fields = Candidate._meta.get_fields()

        # Create a Q object to filter all fields
        query = Q()

        # Loop through each field and check if it's a CharField (string) or nullable field
        for field in fields:
            if field.is_relation:  # Skip related fields (ForeignKey, OneToOne, etc.)
                continue
            if field.name in exclude_fields:  # Skip excluded fields
                continue
            if field.blank or field.null:  # Check if the field allows nulls or blanks
                query |= Q(**{f'{field.name}__isnull': True})  # Check for NULL
                if isinstance(field, models.CharField):  # Check for empty string on CharFields
                    query |= Q(**{f'{field.name}__exact': ""})
        
        
       
        # id = request_data.get('id')
        candidate_status = request_data.get('status')
        if candidate_status == 'profile_pending':
            candidate_status = None
        elif candidate_status == 'pending':
            candidate_status = '2'
        elif candidate_status == 'approved':
            candidate_status = '3'
        elif candidate_status == 'declined':
            candidate_status = '4'
            
        # if candidate_status is not None and candidate_status != "":
        userobj=Candidate.objects.filter(candidate_status=candidate_status,isActive=True,)
        

        if userobj.exists():
            serializer = CandidateSerializer(userobj,many=True)
            for c in serializer.data:
                
                documents_required_object = Documents.objects.filter(isActive=True,role=6)
                documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
                
                for d in documents_required_ser.data:
                    doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=id,document_id=d['id']).first()
                    if doc_object is not None:
                        d['uploaded_proof'] = doc_object.document_url
                    else:
                        d['uploaded_proof'] = ""
                        
                country_name = ""
                state_name = ""
                if c['country'] is not None and c['country'] != "":
                    country_object = Country.objects.filter(id=c['country']).first()
                    if country_object is not None:
                        c['country'] = country_object.name
                    else:
                        c['country'] = ""
                else:
                    c['country'] = ""

                if c['department'] is not None and c['department'] != "":
                    department_object = Department.objects.filter(id=c['department']).first()
                    if department_object is not None:
                        c['department_name'] = department_object.department_name
                    else:
                        c['department_name'] = ""
                else:
                    c['department_name'] = ""
                if c['rank'] is not None and c['rank'] != "":
                    rank_object = Rank.objects.filter(id=c['rank']).first()
                    if rank_object is not None:
                        c['rank_name'] = rank_object.rank
                    else:
                        c['rank_name'] = ""
                else:
                    c['rank_name'] = ""

                if c['state'] is not None and c['state'] != "":
                    state_object = State.objects.filter(id=c['state']).first()
                    if state_object is not None:
                        c['state'] = state_object.name
                    else:
                        c['state'] = ""
                else:
                    c['state'] = ""
                    
                c['proof_data'] = documents_required_ser.data
                c['state_name'] = state_name
                c['country_name'] = country_name

                datestring = c['createdAt']
                dt = datetime.fromisoformat(datestring[:26])  # Remove the timezone offset
                c['createdAt'] = dt.strftime("%d %b, %Y")

                if c['source'] is None or c['source'] == '':
                    c['source'] = ''
                
                # c['createdAt'] = convertcreationdate(datestring) 
                
                # serializer_data.update({
                #     "proof_data":documents_required_ser.data,
                #     "state_name":state_name,
                #     "country_name":country_name,
                # })
                
            response_={
                "n": 1,
                'msg':'Candidate Details Found.',
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
                'msg':'No Data Found.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    # else:
    #     response_={
    #         "n": 0,
    #         'msg':'id is required.',
    #         'data':{}
    #     }
    #     if encryped_header == "1" :
    #         data_to_serialize = convert_decimals_to_float(response_)
    #         encdata = encrypt_data(json.dumps(data_to_serialize))
    #         return Response(encdata,status=200)
    #     else:
    #         return Response(response_,status=200)
      



            
class PaginationCandidateList(GenericAPIView):
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
        
        exclude_fields = ['last_login', 'updatedAt' ,'createdBy','updatedBy','candidate_status','profile_pic']  # List the fields you want to exclude

        # Get all field names for the model
        fields = Candidate._meta.get_fields()

        # Create a Q object to filter all fields
        query = Q()

        # Loop through each field and check if it's a CharField (string) or nullable field
        for field in fields:
            if field.is_relation:  # Skip related fields (ForeignKey, OneToOne, etc.)
                continue
            if field.name in exclude_fields:  # Skip excluded fields
                continue
            if field.blank or field.null:  # Check if the field allows nulls or blanks
                query |= Q(**{f'{field.name}__isnull': True})  # Check for NULL
                if isinstance(field, models.CharField):  # Check for empty string on CharFields
                    query |= Q(**{f'{field.name}__exact': ""})
        
        
       
        # id = request_data.get('id')
        candidate_status = request_data.get('status')
        if candidate_status == 'profile_pending':
            candidate_status = None
        elif candidate_status == 'pending':
            candidate_status = '2'
        elif candidate_status == 'approved':
            candidate_status = '3'
        elif candidate_status == 'declined':
            candidate_status = '4'
            
        # if candidate_status is not None and candidate_status != "":
        userobj=Candidate.objects.filter(candidate_status=candidate_status,isActive=True).order_by('-createdAt')
        if request.user.user_type == 2:
            userobj=userobj
        else:
            if request.user.member_of != '' and request.user.member_of is not None :
                tc_id=str(request.user.member_of)
            else:
                tc_id=str(request.user.id)
            
            userobj=userobj.filter(Q(walkin_by=str(tc_id))|Q(id__in=list(Enrollments.objects.filter(trainingcenter_id=tc_id,isActive=True,enrollments_status='2').values_list('candidate',flat=True)))).order_by('id').distinct('id')




        if userobj.exists():
            page4 = self.paginate_queryset(userobj)
            serializer =  CandidateSerializer(page4,many=True)

            usertype =request.user.user_type
            
            for c in serializer.data:

                c['login_usertype'] = usertype
                c['allow_action']=True
                if c['action_takenby_user_type'] is not None and c['action_takenby_user_type']:
                    if int(c['action_takenby_user_type']) < int(c['login_usertype']):
                        c['allow_action']=False
                    else:
                        c['allow_action']=True



                documents_required_object = Documents.objects.filter(isActive=True,role=6)
                documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
                
                for d in documents_required_ser.data:
                    doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=id,document_id=d['id']).first()
                    if doc_object is not None:
                        d['uploaded_proof'] = doc_object.document_url
                    else:
                        d['uploaded_proof'] = ""
                        
                country_name = ""
                state_name = ""
                if c['country'] is not None and c['country'] != "":
                    country_object = Country.objects.filter(id=c['country']).first()
                    if country_object is not None:
                        c['country'] = country_object.name
                    else:
                        c['country'] = ""
                else:
                    c['country'] = ""


                if c['state'] is not None and c['state'] != "":
                    state_object = State.objects.filter(id=c['state']).first()
                    if state_object is not None:
                        c['state'] = state_object.name
                    else:
                        c['state'] = ""
                else:
                    c['state'] = ""
                    
                c['proof_data'] = documents_required_ser.data
                c['state_name'] = state_name
                c['country_name'] = country_name

                datestring = c['createdAt']
                dt = datetime.fromisoformat(datestring[:26])  # Remove the timezone offset
                c['createdAt'] = dt.strftime("%d %b, %Y")

                if c['source'] is None or c['source'] == '':
                    c['source'] = ''
                
                # c['createdAt'] = convertcreationdate(datestring) 
                
                # serializer_data.update({
                #     "proof_data":documents_required_ser.data,
                #     "state_name":state_name,
                #     "country_name":country_name,
                # })
                
            response_={
                "n": 1,
                'msg':'Candidate Details Found.',
                'data':serializer.data
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
                'msg':'No Data Found.',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    # else:
    #     response_={
    #         "n": 0,
    #         'msg':'id is required.',
    #         'data':{}
    #     }
    #     if encryped_header == "1" :
    #         data_to_serialize = convert_decimals_to_float(response_)
    #         encdata = encrypt_data(json.dumps(data_to_serialize))
    #         return Response(encdata,status=200)
    #     else:
    #         return Response(response_,status=200)
      


class DeleteCandidate(GenericAPIView):
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
            cobj=Candidate.objects.filter(id=id,isActive=True).first()
            if cobj is not None:
                cobj.isActive = False
                cobj.deleted_by = str(request.user.id)
                cobj.save()
                response_={
                    "n": 1,
                    'msg':'Candidate Deteled Successfully.',
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
                    'msg':'Candidate id not found.',
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
            

        
class UpdateCandidate(GenericAPIView):
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
        id = request_data.get('id')
        
        if id is not None:
            data['profile_pic'] = request.FILES.get('profile_pic')
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['email'] = request_data.get('email')
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber') or None
    
            data['highest_qualification'] = request_data.get('highest_qualification')
            data['qualification_year'] = request_data.get('qualification_year')
            data['dob'] = request_data.get('dob')
            data['passport_expiry_date'] = request_data.get('passport_expiry_date')
            data['passport_number'] = request_data.get('passport_number')
            data['nationality'] = request_data.get('nationality')
            # 
            data['city'] = request_data.get('city')
            data['country'] = request_data.get('country')
            data['state'] = request_data.get('state') or None
            data['pincode'] = request_data.get('pincode')
            data['address_line_one'] = request_data.get('address_line_one')
            data['address_line_two'] = request_data.get('address_line_two')
            data['updatedBy'] = str(request.user.id)
            
            obj = Candidate.objects.filter(isActive=True).exclude(id=id)
            ser = CandidateSerializer(obj,many=True)
            # for p in ser.data:
            #     if str(p['first_name']).lower() == str(data['first_name']).lower():
            #         response_={
            #             "n": 0,
            #             'msg':'First name already exits.',
            #             'data':{}
            #         }
            #         if encryped_header == "1" :
            #             data_to_serialize = convert_decimals_to_float(response_)
            #             encdata = encrypt_data(json.dumps(data_to_serialize))
            #             return Response(encdata,status=200)
            #         else:
            #             return Response(response_,status=200)
            
            peobj=Candidate.objects.filter(id=id,isActive=True).first()
            if request.FILES.get('profile_pic') is not None and request.FILES.get('profile_pic') !='':
                fileInput=request.FILES.get('profile_pic')
                folder_path = os.path.join(settings.MEDIA_ROOT,'media','Candidate Profile Pictures')
                file_url=save_file(folder_path,fileInput,request)
                data['profile_pic'] = file_url
            else:
                data['profile_pic'] = peobj.profile_pic

            
            if peobj is not None:

                serializer = CandidateSerializer(peobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Candidate Updated Successfully.',
                        'data':serializer.data
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
 
 
 
class UpdateDetailsCandidatePage(GenericAPIView):
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
        id = request_data.get('id')
        if id is not None:
            # 
            data['vessel_name'] = request_data.get('vessel_name')
            data['next_vessel'] = request_data.get('next_vessel')
            data['sign_on_date'] = request_data.get('sign_on_date')
            data['sign_of_date'] = request_data.get('sign_of_date')
            data['seaman_book_number'] = request_data.get('seaman_book_number')
            data['department'] = request_data.get('department')
            data['rank'] = request_data.get('rank')
            
            # obj = Candidate.objects.filter(isActive=True).exclude(id=id)
           
            # ser = CandidateSerializer(obj,many=True)

            peobj=Candidate.objects.filter(id=id,isActive=True).first()
            if peobj is not None:
                serializer = CandidateSerializer(peobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Candidate Updated Successfully.',
                        'data':serializer.data
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    print('error',serializer.errors)
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
            
            

class UploadCandidateDocumentFormData(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
      
        candidate_id = request_data.get('candidate_id')
        user_ids = request_data.getlist('user_id')
        doc_ids = request_data.getlist('doc_id')
        doc_names = request_data.getlist('doc_name')
        file_uploads = request.FILES.getlist('document_file_upload')

        educational_certificate_upload = request.FILES.get('educational_certificate_upload')
        certificate_name = request_data.get('certificate_name')
        cdobj = Candidate.objects.filter(id=candidate_id).first()

        department = request_data.get('department')
        rank = request_data.get('rank')

        if department is not None and department !='' :
            cdobj.department=department
            cdobj.save()
        if rank is not None and rank !='' :
            cdobj.rank=rank
            cdobj.save()

        if cdobj.department is None or cdobj.department =='':
            response_={
                'n':0,
                'msg':'Please select department first',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        if cdobj.rank is None or cdobj.rank =='':
            response_={
                'n':0,
                'msg':'Please select rank first',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

        # Creating the list of dictionaries
        result = [
            {
                'user_id': user_id,
                'doc_id': doc_id,
                'doc_name': doc_name,
                'document_file_upload': file_upload,
            }
            for user_id, doc_id, doc_name, file_upload in zip(user_ids, doc_ids, doc_names, file_uploads)
        ]
          
        docsUpload = request.FILES.getlist('document_file_upload')
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Documents','candidate')

        file_url_list = []
        if result != []:
            for i in result:
                file_url=save_file(folder_path,i['document_file_upload'],request)
                user_doc = CandidateDocuments.objects.filter(isActive=True,user_id = i['user_id'],document_id=i['doc_id']).update(isActive=False)
                
                # if user_doc is None:
                CandidateDocuments.objects.create(
                    document_id = i['doc_id'],
                    document_name = i['doc_name'],
                    user_id = i['user_id'],
                    document_url =file_url
                )





        if educational_certificate_upload is not None:
            cer_file_url=save_file(folder_path,educational_certificate_upload,request)
            cdobj.certificate_name = certificate_name
            cdobj.educational_certificate = cer_file_url
            cdobj.save()

        if 'candidate_status' in request_data.keys():
            cdobj.candidate_status = request_data.get('candidate_status')
            cdobj.save()

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
        # else:
        #     response_={
        #         'n':0,
        #         'msg':'Documents updated successfully',
        #         'data':{}
        #     }
        #     if encryped_header == "1" :
        #         data_to_serialize = convert_decimals_to_float(response_)
        #         encdata = encrypt_data(json.dumps(data_to_serialize))
        #         return Response(encdata,status=200)
        #     else:
        #         return Response(response_,status=200)
 
        
class ApprovedCandidateStatus(GenericAPIView):
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

        userid = str(request.user.id)
        userobj = UserAdmin.objects.filter(id=userid).first()
        if userobj is not None:
            usertype = userobj.user_type
        else:
            usertype = ''

        if id is not None:
            candiobj = Candidate.objects.filter(id=id,isActive=True).first()
            if candiobj is not None:
                candiobj.candidate_status = 3
                candiobj.updatedAt = timezone.now()
                candiobj.action_takenby = userid
                candiobj.action_takenby_user_type = usertype
                candiobj.save()

                candidatelog.objects.create(candidate_id=str(id),action_takenbyid=userid,action_usertype=usertype,action='Approved',decline_reason='')
                response_={
                    'n':1,
                    'msg':'Candidate Approved successfully',
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
                    'msg':'Candidate not found.',
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
 


class DeclinedCandidateStatus(GenericAPIView):
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
        userid = str(request.user.id)
        userobj = UserAdmin.objects.filter(id=userid).first()
        if userobj is not None:
            usertype = userobj.user_type
        else:
            usertype = ''

        decline_reason = request_data.get('decline_reason')
        if id is not None:
            candiobj = Candidate.objects.filter(id=id,isActive=True).first()
            if candiobj is not None:
                candiobj.decline_reason = decline_reason
                candiobj.candidate_status = 4
                candiobj.action_takenby = userid
                candiobj.action_takenby_user_type = usertype
                candiobj.updatedAt = timezone.now()
                candiobj.save()

                candidatelog.objects.create(candidate_id=str(id),action_takenbyid=userid,action_usertype=usertype,action='Declined',decline_reason=decline_reason)

                response_={
                    'n':1,
                    'msg':'Candidate Declined Successfully',
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
                    'msg':'Candidate not found.',
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
                'msg':'Candidate ID is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 

class SendMailOTP(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request_data.get('email')
        if email is not None and email != '':
            cand_object = Candidate.objects.filter(isActive=True,email=email).first()
            if cand_object is not None:
                response_={
                'n':0,
                'msg':'Candidate with this Email id already exists.',
                'data':{}
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                
            otpnumber = randint(1000, 9999)
            checkexist = candidateOtp.objects.filter(email = email,isActive=True)
            if checkexist is not None:
                otpupdateobj = candidateOtp.objects.filter(email = email,isActive=True).update(isActive=False)
                createotp = candidateOtp.objects.create(email = email,isActive=True,emailotp = otpnumber)
            else:
                createotp = candidateOtp.objects.create(email = email,isActive=True,emailotp = otpnumber)
            
            dicti = {'otp': otpnumber,'email': email}

            message = get_template(
                'otpmail.html').render(dicti)
            msg = EmailMessage(
                'Candidate Verification- OTP!',
                message,
                EMAIL_HOST_USER,
                [email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            response_={
                'n':1,
                'msg':'Verification OTP Sent on email successfully',
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
                'msg':'email is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 



class VerifyOTP(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request_data.get('email')
        otp = request_data.get('otp')
        if email is not None and email != '':
            if otp is not None and otp != '':
                checkotpexist = candidateOtp.objects.filter(email = email,isActive=True,emailotp=str(otp)).first()
                if checkotpexist is not None:
                    response_={
                        'n':1,
                        'msg':'OTP Verified successfully',
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
                    'msg':'Invalid OTP !',
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
                    'msg':'otp is required',
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
                'msg':'email is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 

class RegisterCandidate (GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
        data['first_name'] = request_data.get('first_name')
        data['middle_name'] = request_data.get('middle_name')
        data['last_name'] = request_data.get('last_name')
        data['email'] = request_data.get('email')
        data['country_code'] = request_data.get('country_code')
        data['mobilenumber'] = request_data.get('mobilenumber')
        data['password'] = request_data.get('password')
        data['source'] = 'Website'


        email_object = Candidate.objects.filter(isActive=True,email=data['email']).first()
        number_object = Candidate.objects.filter(isActive=True,mobilenumber=data['mobilenumber']).first()
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
            
        serializer = CandidateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_={
                "n": 1,
                "msg": 'Candidate registered successfully',
                "data":serializer.data                        
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
            

class CandidateDetails (GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
    
        candidate_id = request_data.get('id')
        if candidate_id is not None:
            data['seaman_book_number'] = request_data.get('seafearers_number')
            data['passport_number'] = request_data.get('passport_number')
            data['department'] = request_data.get('department')
            data['rank'] = request_data.get('rank')
            data['dob'] = request_data.get('dob')
            data['country'] = request_data.get('country')
            data['pincode'] = request_data.get('pincode')
            data['highest_qualification']=request_data.get('highest_qualification')
          
            peobj=Candidate.objects.filter(id=candidate_id,isActive=True).first()
            if peobj is not None:
                serializer = CandidateSerializer(peobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Candidate details added Successfully.',
                        'data':serializer.data
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    print('error',serializer.errors)
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
            

# class CandidateDocsList(GenericAPIView):
#     def get(self,request):
#         encryped_header = ""
#         if 'encrypted' in request.headers.keys():
#             encryped_header = request.headers.get('encrypted')

#         documents_required_object = Documents.objects.filter(isActive=True,role=6)
#         if documents_required_object is not None:
#             documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
            
#             response_={
#                 "n": 1,
#                 'msg':'documents list found Successfully.',
#                 'data':documents_required_ser.data
#             }
#             if encryped_header == "1" :
#                 data_to_serialize = convert_decimals_to_float(response_)
#                 encdata = encrypt_data(json.dumps(data_to_serialize))
#                 return Response(encdata,status=200)
#             else:
#                 return Response(response_,status=200)
#         else:
#             response_={
#                             "n": 0,
#                             "msg": 'documents list not found',
#                             "data":[]                     
#                         }
#             if encryped_header == "1" :
#                 data_to_serialize = convert_decimals_to_float(response_)
#                 encdata = encrypt_data(json.dumps(data_to_serialize))
#                 return Response(encdata,status=200)
#             else:
#                 return Response(response_,status=200)
import ast
class candidatedocumentssubmit(GenericAPIView):
     def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response

        user_ids = request.data.getlist('user_id')
        if len(user_ids) == 1 and user_ids[0].startswith('['):
            try:
                user_ids = ast.literal_eval(user_ids[0])
            except Exception as e:
                return Response({"error": f"Invalid user_id format: {str(e)}"}, status=400)
        else:
            user_ids = user_ids
      
        doc_ids = request.data.getlist('doc_id')
        if len(doc_ids) == 1 and doc_ids[0].startswith('['):
            try:
                doc_ids = list(map(int,ast.literal_eval(doc_ids[0])))
            except Exception as e:
                return Response({"error": f"Invalid doc_id format: {str(e)}"}, status=400)
        else:
            doc_ids = list(map(int, doc_ids))
     
        doc_names = request.data.getlist('doc_name')
        if len(doc_names) == 1 and doc_names[0].startswith('['):
            try:
                doc_names = ast.literal_eval(doc_names[0])
            except Exception as e:
                return Response({"error": f"Invalid user_id format: {str(e)}"}, status=400)
        else:
            doc_names = doc_names


        file_uploads = request.FILES.getlist('document_file_upload')
        educational_certificate_upload = request.FILES.get('educational_certificate_upload')
        certificate_name = request.data.get('certificate_name')


        # Creating the list of dictionaries
        result = [
            {
                'user_id': user_id,
                'doc_id': doc_id,
                'doc_name': doc_name,
                'document_file_upload': file_upload,
            }
            for user_id, doc_id, doc_name, file_upload in zip(user_ids, doc_ids, doc_names, file_uploads)
        ]

        docsUpload = request.FILES.getlist('document_file_upload')
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Documents','candidate')

        
        file_url_list = []
        for i in result:
            userid = i['user_id']
            file_url=save_file(folder_path,i['document_file_upload'],request)
            user_doc = CandidateDocuments.objects.filter(isActive=True,user_id = i['user_id'],document_url =file_url).update(isActive=False)
            
            # if user_doc is None:
            CandidateDocuments.objects.create(
                document_id = i['doc_id'],
                document_name = i['doc_name'],
                user_id = i['user_id'],
                document_url =file_url
            )
        cduserid = user_ids[0]
        cdobj = Candidate.objects.filter(id=cduserid).first()
        if educational_certificate_upload is not None:
            cer_file_url=save_file(folder_path,educational_certificate_upload,request)
            cdobj.certificate_name = certificate_name
            cdobj.educational_certificate = cer_file_url
            cdobj.save()

       
        cdobj.candidate_status = '2'
        cdobj.save()


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
        




class getenrollmentdocuments (GenericAPIView):
   
     def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        cand = request.data.get('candidateid')
        candidateobj = Candidate.objects.filter(id=cand).first()
        if candidateobj is not None:
            cand_ser =CandidateSerializer(candidateobj)
            country_id=cand_ser.data['country']
            department_id=cand_ser.data['department']
            rank_id=cand_ser.data['rank']
            qualid = cand_ser.data['highest_qualification']
            document_ids=[]


            country_rules_ids=list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))

            find_combination_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=country_rules_ids,departments=department_id,ranks=rank_id,isActive=True).first()
            

            if find_combination_obj is not None:

                combination_rule_id=find_combination_obj.general_eligibility_rule_id
               
                min_age_required=find_combination_obj.minimum_age
                age = calculate_age(cand_ser.data['dob'])

                qualification_ids=list(GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('educational_qualification_id',flat=True))

                if age > int(min_age_required) and  int(qualid) in qualification_ids:
                    document_ids=list(GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('document_id',flat=True))
                    if len(document_ids) != 0:
                        documents_required_object = Documents.objects.filter(id__in=document_ids,isActive=True,role=6)
                    else:
                        documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                else:
                    documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                
            else:
                documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)


            documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
            
            for d in documents_required_ser.data:
                doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=cand,document_id=d['id']).first()
                if doc_object is not None:
                    d['uploaded_proof'] = doc_object.document_url
                else:
                    d['uploaded_proof'] = ""
               
                   
            country_name = ""
            state_name = ""
            if cand_ser.data['country'] is not None and cand_ser.data['country'] != "":
                country_object = Country.objects.filter(id=cand_ser.data['country']).first()
                if country_object is not None:
                    country_name = country_object.name
                else:
                    country_name = ""
            else:
                country_name = ""


            if cand_ser.data['state'] is not None and cand_ser.data['state'] != "":
                state_object = State.objects.filter(id=cand_ser.data['state']).first()
                if state_object is not None:
                    state_name = state_object.name
                else:
                    state_name = ""
            else:
                state_name = ""
                
            proof_data = documents_required_ser.data
            state_name = state_name
            country_name = country_name
            serializer_data = cand_ser.data
            if qualid is not None:
                EducationalQualificationsobj = EducationalQualifications.objects.filter(id=int(qualid)).first()
                educatser = EducationalQualificationsSerializer(EducationalQualificationsobj)
                educatser_data = educatser.data
                educatser_data.update({
                    'uploaded_certificate' : cand_ser.data['educational_certificate'],
                    'certificate_name' : cand_ser.data['certificate_name']
                })
                # datestring = serializer_data['createdAt']
                # date = datetime.strptime(datestring, "%d %b %Y")
                # createdAt = convertcreationdate(datestring) 

                serializer_data.update({
                    "education_document_data":educatser_data,
                    "proof_data":documents_required_ser.data,
                    "state_name":state_name,
                    "country_name":country_name,
                    # "createdAt":date
                })
                
            response_={
                "n": 1,
                'msg':'Candidate found Successfully.',
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
                'msg':'Candidate not found.',
                'data':serializer_data
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


from itertools import chain

class candidatecoursecategories(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)        
    def get(self,request):
       
        cadid = str(request.user.id)
        enrollobjs = Enrollments.objects.filter(candidate=cadid,isActive=True,enrollments_status='2').values_list('course',flat=True)
        enroll_list = list(map(int,enrollobjs))
        if enroll_list != []:
            courseobj =  CourseEligibility.objects.filter(course_id__in=enroll_list).order_by('id')
            category_lists = courseobj.values_list('category', flat=True)
            # Flatten and remove duplicates using set
            unique_categories = set(chain.from_iterable(filter(None, category_lists)))
            category_list = list(map(int,unique_categories))
            categobj =  Category.objects.filter(id__in=category_list).order_by('category_name')
            catser = CategorySerializer(categobj,many=True)

            response_={
            "n": 1,
            'msg':'category list found Successfully.',
            'data':catser.data
            }
            return Response(response_,status=200)
        else:
            response_={
                        "n": 0,
                        "msg": 'course list not found',
                        "data":[]                     
                    }
           
            return Response(response_,status=200)


class getcertificates(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)        
    def get(self,request):
        cadid = str(request.user.id)
        examschedilelist = ExamCandidateResult.objects.filter(candidate_id=cadid,isActive=True,is_passed=True).values_list('exam_schedule_id',flat=True)
        if examschedilelist.exists():
            examsclist = list(map(int,examschedilelist))
            courselistobj = ScheduleExam.objects.filter(id__in=examsclist,isActive=True).values_list('course',flat=True)
            if courselistobj.exists():
                newcourselist =list(set(courselistobj))
                courseobj = Course.objects.filter(id__in=newcourselist).order_by('id')
                courseser = CourseSerializer(courseobj,many=True)
                for c in courseser.data:
                    expiry_date_str = c['expiry']
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                    today = date.today()
                    if expiry_date < today:
                       c['getdays'] = 'Expired'
                    else:
                       c['getdays'] = getdays(str(expiry_date))


                    
                    ScheduleExamids = ScheduleExam.objects.filter(course = c['id'],isActive=True).values_list('id',flat=True)
                    ExamCandidateResultids = ExamCandidateResult.objects.filter(exam_schedule_id__in=ScheduleExamids,candidate_id = cadid).order_by('start_created_time').last()
                    modeschobj = ScheduleExam.objects.filter(id=ExamCandidateResultids.exam_schedule_id).first()
                    mode = modeschobj.exam_mode
                    if mode == 1:
                        c['mode'] = 'Virtual'
                    else:
                        c['mode'] = 'Offline'

                    adminobj = UserAdmin.objects.filter(id=modeschobj.training_center).first()
                    if adminobj is not None:
                        c['inst_name'] = adminobj.name
                    else:
                        c['inst_name'] = ''

                    c['certificate_link'] = ExamCandidateResultids.certificate_link

                response_={
                    "n": 1,
                    'msg':'result list found Successfully.',
                    'data':courseser.data
                }
                return Response(response_,status=200)
            else:
                response_={
                    "n": 0,
                    "msg": 'courses not found',
                    "data":[]                     
                }
                return Response(response_,status=200)
        else:
            response_={
                "n": 0,
                "msg": 'Exams not found',
                "data":[]                     
            }
            return Response(response_,status=200)









class getresults(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)        
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        data = {}
    
        categoryid = request_data.get('category_id')
        cadid = str(request.user.id)


        examschedilelist = ExamCandidateResult.objects.filter(candidate_id=cadid,isActive=True).values_list('exam_schedule_id',flat=True)
        if examschedilelist.exists():
            examsclist = list(map(int,examschedilelist))
            courselistobj = ScheduleExam.objects.filter(id__in=examsclist,isActive=True).values_list('course',flat=True)
            if courselistobj.exists():
                if categoryid != 'all':
                    category_id = str(categoryid)
                    coursecatobj = CourseEligibility.objects.filter(course_id__in=courselistobj,category__contains=category_id).values_list('course_id',flat=True)
                    newcourselist = list(set(coursecatobj))
                else:
                    newcourselist =list(set(courselistobj))

                if newcourselist != []:
                    courseobj = Course.objects.filter(id__in=newcourselist).order_by('id')
                    courseser = CourseSerializer(courseobj,many=True)
                    for c in courseser.data:
                        ScheduleExamids = ScheduleExam.objects.filter(course = c['id'],isActive=True).values_list('id',flat=True)
                        ExamCandidateResultids = ExamCandidateResult.objects.filter(exam_schedule_id__in=ScheduleExamids,candidate_id = cadid).order_by('start_created_time')
                        Examser = ExamCandidateResultSerializer(ExamCandidateResultids,many=True)
                        for e in Examser.data:
                            e['start_created_time'] = getdatewithtime(str(e['start_created_time']))
                            if e['is_passed'] is True:
                                e['pass_status'] = 'Competent'
                            else:
                                e['pass_status'] = 'Not Yet Competent'

                            eemodeschobj = ScheduleExam.objects.filter(id=e['exam_schedule_id']).first()
                            eemode = eemodeschobj.exam_mode
                            if eemode == 1:
                                e['mode'] = 'Virtual'
                            else:
                                e['mode'] = 'Offline'
                        c['attemptsdata'] = Examser.data

                        attemptsgiven = ExamCandidateResultids.count()
                        if attemptsgiven > 3:
                            attempts_left = 0
                        else:
                            attempts_left = 3-attemptsgiven
                        c['attempts_left'] =attempts_left

                        ExamCandidateResultids = ExamCandidateResult.objects.filter(exam_schedule_id__in=ScheduleExamids,candidate_id = cadid).order_by('start_created_time').last()
                        modeschobj = ScheduleExam.objects.filter(id=ExamCandidateResultids.exam_schedule_id).first()
                        mode = modeschobj.exam_mode
                        if mode == 1:
                            c['mode'] = 'Virtual'
                        else:
                            c['mode'] = 'Offline'

                        adminobj = UserAdmin.objects.filter(id=modeschobj.training_center).first()
                        if adminobj is not None:
                            c['inst_name'] = adminobj.name
                        else:
                            c['inst_name'] = ''

                        c['time_taken'] = gettimediff(str(ExamCandidateResultids.start_created_time),str(ExamCandidateResultids.end_created_time))
                        c['total_marks'] = ExamCandidateResultids.marks_obtained
                        pass_status =  ExamCandidateResultids.is_passed
                        if pass_status is True:
                            c['cad_status'] = 'Competent'
                        else:
                            c['cad_status']='Not Yet Competent'

                        


                    response_={
                    "n": 1,
                    'msg':'result list found Successfully.',
                    'data':courseser.data
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
                            "msg": 'results not found',
                            "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)




class CountryList(GenericAPIView):
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        countryobj = Country.objects.filter(isActive=True,)
        if countryobj is not None:
            country_ser =CountrySerializer(countryobj,many=True)
            
            response_={
                "n": 1,
                'msg':'country list found Successfully.',
                'data':country_ser.data
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
                            "msg": 'country list not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class NonEligibleCountryList(GenericAPIView):
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        countryobj = Country.objects.filter(isActive=True,is_eligibile=False)
        if countryobj is not None:
            country_ser =CountrySerializer(countryobj,many=True)
            
            response_={
                "n": 1,
                'msg':'country list found Successfully.',
                'data':country_ser.data
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
                            "msg": 'country list not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class EligibleCountryList(GenericAPIView):
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        countryobj = Country.objects.filter(isActive=True,is_eligibile=True)
        if countryobj is not None:
            country_ser =CountrySerializer(countryobj,many=True)
            
            response_={
                "n": 1,
                'msg':'country list found Successfully.',
                'data':country_ser.data
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
                            "msg": 'country list not found',
                            "data":[]                     
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class ForgotPassword(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request.data.get('email')
        if email is not None and email != '':
            checkexist = Candidate.objects.filter(email = email,isActive=True).first()
            if checkexist is not None:
                curruser = checkexist.first_name +" "+checkexist.last_name
                dicti = {'email': email,'Name':curruser,'frontUrl':frontURL,'userid':checkexist.id}

                message = get_template('forgot-password-email-template.html').render(dicti)
                msg = EmailMessage(
                    'Forgot Password?',
                    message,
                    EMAIL_HOST_USER,
                    [email],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                    

                response_={
                'n':1,
                'msg':'email sent successfully',
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
                'msg':'email id not found',
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
                'msg':'email is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 
class ResetPassword(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
    
        newpassword = request.data.get('newpassword')
        userid = request.data.get('userid')
        if newpassword is not None and newpassword != '':
            if userid is not None and userid != '':
                checkexistuser = Candidate.objects.filter(id = userid,isActive=True).first()
                if checkexistuser is not None:
                    checkexistuser.password = newpassword
                    checkexistuser.save()
                    response_={
                        'n':1,
                        'msg':'Password updated successfully',
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
                    'msg':'candidate not found',
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
                    'msg':'id is required',
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
                    'msg':'new password is required',
                    'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

        
      
class SendPasswordVerificationOTP(GenericAPIView):
    # authentication_classes=[CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)     
    

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        email = request_data.get('email')
        if email is not None and email != '':
            cand_object = Candidate.objects.filter(isActive=True,email=email).first()
            if cand_object is None:
                response_={
                'n':0,
                'msg':'Account not found. Please register first.',
                'data':{}
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                
            otpnumber = randint(1000, 9999)
            checkexist = candidateOtp.objects.filter(email = email,isActive=True)
            if checkexist is not None:
                otpupdateobj = candidateOtp.objects.filter(email = email,isActive=True).update(isActive=False)
                createotp = candidateOtp.objects.create(email = email,isActive=True,emailotp = otpnumber)
            else:
                createotp = candidateOtp.objects.create(email = email,isActive=True,emailotp = otpnumber)
            
            dicti = {'otp': otpnumber,'email': email}

            message = get_template(
                'otpmail.html').render(dicti)
            msg = EmailMessage(
                'Candidate Verification- OTP!',
                message,
                EMAIL_HOST_USER,
                [email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            response_={
                'n':1,
                'msg':'Verification OTP Sent on email successfully',
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
                'msg':'email is required',
                'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
 

    
class SetPassword(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)        

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
    
        newpassword = request.data.get('password')
        email = request.data.get('email')
        if newpassword is not None and newpassword != '':
            if email is not None and email != '':
                checkexistuser = Candidate.objects.filter(email=email, isActive=True).first()
                if checkexistuser is not None:
                    checkexistuser.password = newpassword
                    checkexistuser.save()
                    response_={
                        'n':1,
                        'msg':'Password updated successfully',
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
                    'msg':'candidate not found',
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
                    'msg':'id is required',
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
                    'msg':'new password is required',
                    'data':{}
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

        



class GetGeneralDetails(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        cand = request.user.id
        candidateobj = Candidate.objects.filter(id=cand).first()
        if candidateobj is not None:
            cand_ser =CandidateSerializer(candidateobj)


            # department_id=cand_ser.data['department']
            # if cand_ser.data['rank'] !='' and cand_ser.data['rank'] is not None and cand_ser.data['rank'] !='Select rank':
            #     rank_id=cand_ser.data['rank']
            # else:
            #     rank_id=''
            # qualid = cand_ser.data['highest_qualification']
            # document_ids=[]

            # country_id=cand_ser.data['country']
            # country_rules_ids=list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))
            # if rank_id !='' and rank_id is not None and rank_id !='Select rank':

            #     find_combination_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=country_rules_ids,departments=department_id,ranks=rank_id,isActive=True).first()
            

            #     if find_combination_obj is not None:

            #         combination_rule_id=find_combination_obj.general_eligibility_rule_id
                
            #         min_age_required=find_combination_obj.minimum_age
            #         age = calculate_age(cand_ser.data['dob'])

            #         qualification_ids=list(GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('educational_qualification_id',flat=True))

            #         if age > int(min_age_required) and  int(qualid) in qualification_ids:
            #             document_ids=list(GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('document_id',flat=True))
            #             if len(document_ids) != 0:
            #                 documents_required_object = Documents.objects.filter(id__in=document_ids,isActive=True,role=6)
            #             else:
            #                 documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
            #         else:
            #             documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                    
            #     else:
            #         documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
            # else:
            #     documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)


            # documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
            
            # for d in documents_required_ser.data:
            #     doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=cand,document_id=d['id']).first()
            #     if doc_object is not None:
            #         d['uploaded_proof'] = doc_object.document_url
            #     else:
            #         d['uploaded_proof'] = ""
               
                   
            # country_name = ""
            # if cand_ser.data['country'] is not None and cand_ser.data['country'] != "":
            #     country_object = Country.objects.filter(id=cand_ser.data['country']).first()
            #     if country_object is not None:
            #         country_name = country_object.name
            #     else:
            #         country_name = ""
            # else:
            #     country_name = ""

            # city_name = cand_ser.data['city']



            # state_name = ""

            # if cand_ser.data['state'] is not None and cand_ser.data['state'] != "":
            #     state_object = State.objects.filter(id=cand_ser.data['state']).first()
            #     if state_object is not None:
            #         state_name = state_object.name
            #     else:
            #         state_name = ""
            # else:
            #     state_name = ""

            # if cand_ser.data['department'] is not None and cand_ser.data['department'] != "":
            #     department_object = Department.objects.filter(id=cand_ser.data['department']).first()
            #     if department_object is not None:
            #         department_name = department_object.department_name
            #     else:
            #         department_name = ""
            # else:
            #     department_name = ""
            # if cand_ser.data['rank'] is not None and cand_ser.data['rank'] != "" and cand_ser.data['rank'] !='Select rank':
            #     rank_object = Rank.objects.filter(id=cand_ser.data['rank']).first()
            #     if rank_object is not None:
            #         rank_name = rank_object.rank
            #     else:
            #         rank_name = ""
            # else:
            #     rank_name = ""

            # proof_data = documents_required_ser.data
            # state_name = state_name
            # country_name = country_name
            serializer_data = cand_ser.data


            # serializer_data.update({
            #     "proof_data":documents_required_ser.data,
            #     "state_name":state_name,
            #     "country_name":country_name,
            #     "department_name":department_name,
            #     "rank_name":rank_name,
            #     "city_name":city_name,
            #     "state_name":state_name,
            #     # "createdAt":date
            # })


            # if qualid is not None and qualid !='' and qualid !='Select Qualification':
            #     EducationalQualificationsobj = EducationalQualifications.objects.filter(id=int(qualid)).first()
            #     educatser = EducationalQualificationsSerializer(EducationalQualificationsobj)
            #     educatser_data = educatser.data
            #     educatser_data.update({
            #         'uploaded_certificate' : cand_ser.data['educational_certificate'],
            #         'certificate_name' : cand_ser.data['certificate_name']
            #     })
            #     # datestring = serializer_data['createdAt']
            #     # date = datetime.strptime(datestring, "%d %b %Y")
            #     # createdAt = convertcreationdate(datestring) 

            #     serializer_data.update({
            #         "education_document_data":educatser_data,
            #     })
                
            response_={
                "n": 1,
                'msg':'Candidate found Successfully.',
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class UpdateGeneralDetails(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}
        first_name = request_data.get('first_name')
        if first_name is not None and first_name != '':

            data['first_name']=request_data.get('first_name')

        middle_name = request_data.get('middle_name')
        if middle_name is not None and middle_name != '':
            data['middle_name']=request_data.get('middle_name')
        last_name = request_data.get('last_name')
        if last_name is not None and last_name != '':
            data['last_name']=request_data.get('last_name')

        dob = request_data.get('dob')
        if dob is not None and dob != '':
            data['dob']=request_data.get('dob')








            
        if request.FILES.get('profile_pic') is not None and request.FILES.get('profile_pic') !='':
            fileInput=request.FILES.get('profile_pic')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Candidate Profile Pictures')
            file_url=save_file(folder_path,fileInput,request)
            data['profile_pic'] = file_url



        
        cand = request.user.id
        candidateobj = Candidate.objects.filter(id=cand,isActive=True).first()
        if candidateobj is not None:

            email = request_data.get('email')
            if email is not None and email != '':
                data['email']=request_data.get('email')
                check_email = Candidate.objects.filter(email=data['email'],isActive=True).exclude(id=cand).first()
                if check_email is not None:
                    response_={
                        "n": 0,
                        "msg": 'Email already exists',
                        "data":[]                     
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            mobilenumber = request_data.get('mobilenumber')
            if mobilenumber is not None and mobilenumber != '':
                data['mobilenumber']=request_data.get('mobilenumber')

                check_mobile = Candidate.objects.filter(mobilenumber=data['mobilenumber'],isActive=True).exclude(id=cand).first()
                if check_mobile is not None:
                    response_={
                        "n": 0,
                        "msg": 'Mobile number already exists',
                        "data":[]                     
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                

            cand_ser =CandidateSerializer(candidateobj,data=data,partial=True)
            if cand_ser.is_valid():
                cand_ser.save()
                serializer_data = cand_ser.data
                response_={
                    "n": 1,
                    'msg':'Candidate general details updated successfully.',
                    'data':serializer_data
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                
            else:
                first_key, first_value = next(iter(cand_ser.errors.items()))
                response_={
                            "n": 0,
                            "msg": first_key+' : '+ first_value[0],
                            "data":cand_ser.errors                    
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class UpdateCandidatePassword(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}

        cand = request.user.id
        newpassword = request_data.get('newpassword')
        checkexistuser = Candidate.objects.filter(id = cand,isActive=True).first()
        if checkexistuser is not None:
            checkexistuser.password = newpassword
            checkexistuser.save()
            response_={
                "n": 1,
                'msg':'Candidate password updated successfully.',
                'data':[]
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class UpdateCandidateProfilePicture(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}


        if request.FILES.get('profile_pic') is not None and request.FILES.get('profile_pic') !='':
            fileInput=request.FILES.get('profile_pic')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Candidate Profile Pictures')
            file_url=save_file(folder_path,fileInput,request)
            data['profile_pic'] = file_url

            cand = request.user.id
            candidateobj = Candidate.objects.filter(id=cand,isActive=True).first()
            if candidateobj is not None:
                cand_ser =CandidateSerializer(candidateobj,data=data,partial=True)
                if cand_ser.is_valid():
                    cand_ser.save()
                    serializer_data = cand_ser.data
                    response_={
                        "n": 1,
                        'msg':'Candidate profile picture updated successfully.',
                        'data':serializer_data
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                    
                else:
                    first_key, first_value = next(iter(cand_ser.errors.items()))
                    response_={
                                "n": 0,
                                "msg": first_key+' : '+ first_value[0],
                                "data":cand_ser.errors                    
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
                    "msg": 'Candidate not found',
                    "data":[]                     
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        else:
            data['profile_pic'] = ''
            response_={
                "n": 0,
                "msg": 'New Profile picture is required',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)







class GetSeafarersDetails(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        cand = request.user.id
        candidateobj = Candidate.objects.filter(id=cand).first()
        if candidateobj is not None:
            cand_ser =CandidateSerializer(candidateobj)
            
            
            if cand_ser.data['rank'] !='' and cand_ser.data['rank'] is not None and cand_ser.data['rank'] !='Select rank':
                rank_id=cand_ser.data['rank']
            else:
                rank_id=''
            # qualid = cand_ser.data['highest_qualification']
            # document_ids=[]

            # country_id=cand_ser.data['country']
            # country_rules_ids=list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))
           
            # documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
            
            # for d in documents_required_ser.data:
            #     doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=cand,document_id=d['id']).first()
            #     if doc_object is not None:
            #         d['uploaded_proof'] = doc_object.document_url
            #     else:
            #         d['uploaded_proof'] = ""
               
                   
            country_name = ""
            if cand_ser.data['country'] is not None and cand_ser.data['country'] != "":
                country_object = Country.objects.filter(id=cand_ser.data['country']).first()
                if country_object is not None:
                    country_name = country_object.name
                else:
                    country_name = ""
            else:
                country_name = ""




            state_name = ""

            if cand_ser.data['state'] is not None and cand_ser.data['state'] != "":
                state_object = State.objects.filter(id=cand_ser.data['state']).first()
                if state_object is not None:
                    state_name = state_object.name
                else:
                    state_name = ""
            else:
                state_name = ""

            if cand_ser.data['department'] is not None and cand_ser.data['department'] != "":
                department_object = Department.objects.filter(id=cand_ser.data['department']).first()
                if department_object is not None:
                    department_name = department_object.department_name
                else:
                    department_name = ""
            else:
                department_name = ""

            if cand_ser.data['rank'] is not None and cand_ser.data['rank'] != "" and cand_ser.data['rank'] !='Select rank':
                rank_object = Rank.objects.filter(id=cand_ser.data['rank']).first()
                if rank_object is not None:
                    rank_name = rank_object.rank
                else:
                    rank_name = ""
            else:
                rank_name = ""


            city_name = cand_ser.data['city']


            # proof_data = documents_required_ser.data

            serializer_data = cand_ser.data


            serializer_data.update({
                # "proof_data":documents_required_ser.data,
                "state_name":state_name,
                "country_name":country_name,
                "department_name":department_name,
                "rank_name":rank_name,
                "city_name":city_name,

            })


            # if qualid is not None and qualid !='' and qualid !='Select Qualification':
            #     EducationalQualificationsobj = EducationalQualifications.objects.filter(id=int(qualid)).first()
            #     educatser = EducationalQualificationsSerializer(EducationalQualificationsobj)
            #     educatser_data = educatser.data
            #     educatser_data.update({
            #         'uploaded_certificate' : cand_ser.data['educational_certificate'],
            #         'certificate_name' : cand_ser.data['certificate_name']
            #     })
            #     # datestring = serializer_data['createdAt']
            #     # date = datetime.strptime(datestring, "%d %b %Y")
            #     # createdAt = convertcreationdate(datestring) 

            #     serializer_data.update({
            #         "education_document_data":educatser_data,
            #     })
                
            response_={
                "n": 1,
                'msg':'Candidate seafarers details found Successfully.',
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class UpdateSeafarersDetails(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        request_data, error_response = handle_request_body(request)
        if error_response:
            return Response(error_response,status=400)
        data = {}
        seaman_book_number = request_data.get('seaman_book_number')
        if seaman_book_number is not None and seaman_book_number != '':
            data['seaman_book_number']=request_data.get('seaman_book_number')
        passport_number = request_data.get('passport_number')
        if passport_number is not None and passport_number != '':
            data['passport_number']=request_data.get('passport_number')
        department= request_data.get('department')
        if department is not None and department != '' and department != 'Select Department':
            data['department']=request_data.get('department')
        rank = request_data.get('rank')
        if rank is not None and rank != '' and rank != 'Select rank':
            data['rank']=request_data.get('rank')
        pincode= request_data.get('pincode')
        if pincode is not None and pincode != '':
            data['pincode']=request_data.get('pincode')

        country= request_data.get('country')
        if country is not None and country != '' and country != 'Select Country':
            data['country']=request_data.get('country')
        state= request_data.get('state')
        if state is not None and state != '' and state != 'Select State':
            data['state']=request_data.get('state')
        city= request_data.get('city')
        if city is not None and city != '':
            data['city']=request_data.get('city')
        
        coc= request_data.get('coc')
        if coc is not None and coc != '':
            data['coc']=request_data.get('coc')


        cand = request.user.id

        candidateobj = Candidate.objects.filter(id=cand,isActive=True).first()
        if candidateobj is not None:
            cand_ser = CandidateSerializer(candidateobj,data=data,partial=True)
            if cand_ser.is_valid():
                cand_ser.save()

                serializer_data = cand_ser.data 

                response_={
                    "n": 1,
                    'msg':'Candidate seafarers details updated successfully.',
                    'data':serializer_data
                }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                first_key, first_value = next(iter(cand_ser.errors.items()))
                response_={
                            "n": 0,
                            "msg": first_key+' : '+ first_value[0],
                            "data":cand_ser.errors                    
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class GetCandidateMandatoryDocument(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        cand = request.user.id
        candidateobj = Candidate.objects.filter(id=cand).first()
        if candidateobj is not None:
            cand_ser =CandidateSerializer(candidateobj)
            
            department_id=cand_ser.data['department']
            if cand_ser.data['rank'] !='' and cand_ser.data['rank'] is not None and cand_ser.data['rank'] !='Select rank':
                rank_id=cand_ser.data['rank']
            else:
                rank_id=''
            qualid = cand_ser.data['highest_qualification']
            document_ids=[]

            country_id=cand_ser.data['country']
            country_rules_ids=list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))
            if rank_id !='' and rank_id is not None and rank_id !='Select rank':

                find_combination_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=country_rules_ids,departments=department_id,ranks=rank_id,isActive=True).first()
            

                if find_combination_obj is not None:

                    combination_rule_id=find_combination_obj.general_eligibility_rule_id
                
                    min_age_required=find_combination_obj.minimum_age
                    age = calculate_age(cand_ser.data['dob'])

                    qualification_ids=list(GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('educational_qualification_id',flat=True))

                    if age > int(min_age_required) and  int(qualid) in qualification_ids:
                        document_ids=list(GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=combination_rule_id,isActive=True).values_list('document_id',flat=True))
                        if len(document_ids) != 0:
                            documents_required_object = Documents.objects.filter(id__in=document_ids,isActive=True,role=6)
                        else:
                            documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                    else:
                        documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
                    
                else:
                    documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)
            else:
                documents_required_object = Documents.objects.filter(document_name__in=['Passport','Birth Certificate'],isActive=True,role=6)


            documents_required_ser = DocumentsSerializer(documents_required_object,many=True)
            










            for d in documents_required_ser.data:
                doc_object = CandidateDocuments.objects.filter(isActive=True,user_id=cand,document_id=d['id']).first()
                if doc_object is not None:
                    d['uploaded_proof'] = doc_object.document_url
                else:
                    d['uploaded_proof'] = ""


            proof_data = documents_required_ser.data

            serializer_data = {
                "eligibility_documents": proof_data
            }




            if qualid is not None and qualid !='' and qualid !='Select Qualification':
                EducationalQualificationsobj = EducationalQualifications.objects.filter(id=int(qualid)).first()
                educatser = EducationalQualificationsSerializer(EducationalQualificationsobj)
                educatser_data = educatser.data
                educatser_data.update({
                    'uploaded_certificate' : cand_ser.data['educational_certificate'],
                    'certificate_name' : cand_ser.data['certificate_name']
                })


                serializer_data["educational_documents"] = educatser_data


            response_={
                "n": 1,
                'msg':'Candidate seafarers details found Successfully.',
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class UploadCandidateDocuments(GenericAPIView):
     def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response

        user_ids = request.data.getlist('user_id')
        if len(user_ids) == 1 and user_ids[0].startswith('['):
            try:
                user_ids = ast.literal_eval(user_ids[0])
            except Exception as e:
                return Response({"error": f"Invalid user_id format: {str(e)}"}, status=400)
        else:
            user_ids = user_ids
      
        doc_ids = request.data.getlist('doc_id')
        if len(doc_ids) == 1 and doc_ids[0].startswith('['):
            try:
                doc_ids = list(map(int,ast.literal_eval(doc_ids[0])))
            except Exception as e:
                return Response({"error": f"Invalid doc_id format: {str(e)}"}, status=400)
        else:
            doc_ids = list(map(int, doc_ids))
     
        doc_names = request.data.getlist('doc_name')
        if len(doc_names) == 1 and doc_names[0].startswith('['):
            try:
                doc_names = ast.literal_eval(doc_names[0])
            except Exception as e:
                return Response({"error": f"Invalid user_id format: {str(e)}"}, status=400)
        else:
            doc_names = doc_names


        file_uploads = request.FILES.getlist('document_file_upload')
        educational_certificate_upload = request.FILES.get('educational_certificate_upload')
        certificate_name = request.data.get('certificate_name')


        # Creating the list of dictionaries
        result = [
            {
                'user_id': user_id,
                'doc_id': doc_id,
                'doc_name': doc_name,
                'document_file_upload': file_upload,
            }
            for user_id, doc_id, doc_name, file_upload in zip(user_ids, doc_ids, doc_names, file_uploads)
        ]

        docsUpload = request.FILES.getlist('document_file_upload')
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Documents','candidate')

        
        file_url_list = []
        for i in result:
            userid = i['user_id']
            file_url=save_file(folder_path,i['document_file_upload'],request)
            user_doc = CandidateDocuments.objects.filter(isActive=True,user_id = i['user_id'],document_url =file_url).update(isActive=False)
            
            # if user_doc is None:
            CandidateDocuments.objects.create(
                document_id = i['doc_id'],
                document_name = i['doc_name'],
                user_id = i['user_id'],
                document_url =file_url
            )
        cduserid = user_ids[0]
        cdobj = Candidate.objects.filter(id=cduserid).first()
        if educational_certificate_upload is not None:
            cer_file_url=save_file(folder_path,educational_certificate_upload,request)
            cdobj.certificate_name = certificate_name
            cdobj.educational_certificate = cer_file_url
            cdobj.save()

       
        # cdobj.candidate_status = '2'
        # cdobj.save()


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
        

class GetCandidateInstitutesCourseDetails(GenericAPIView):
    authentication_classes=[CandidateJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        cand = request.user.id
        candidateobj = Candidate.objects.filter(id=cand).first()
        if candidateobj is not None:
            # cand_ser =CandidateSerializer(candidateobj)
            institutes_ids = list(Enrollments.objects.filter(isActive=True,candidate=cand,enrollments_status='2').order_by('trainingcenter_id').distinct('trainingcenter_id').values_list('trainingcenter_id',flat=True))

            institutes_obj=UserAdmin.objects.filter(id__in=institutes_ids,isActive=True)
            institutes_ser = UserAdminSerializer(institutes_obj,many=True)
            for institute in institutes_ser.data:
                institute['courses'] = []
                candidate_enrolled_courses = list(Enrollments.objects.filter(isActive=True,trainingcenter_id=institute['id'],candidate=cand,enrollments_status='2').order_by('course').distinct('course').values_list('course',flat=True))
                course_obj=Course.objects.filter(id__in=candidate_enrolled_courses,isActive=True)
                course_ser = CourseSerializer(course_obj,many=True)
                institute['courses']=course_ser.data

            response_={
                "n": 1,
                'msg':'Candidate Institutes details found Successfully.',
                'data':institutes_ser.data
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
                "msg": 'Candidate not found',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)








