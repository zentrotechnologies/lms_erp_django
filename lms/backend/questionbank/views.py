from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from master.models import *
from .serializers import *
from master.serializers import *
from lms.settings import *
from django.contrib.auth.hashers import make_password,check_password
from adminauth.jwt import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.views import save_file
from course.models import *
from course.serializers import *
from adminauth.common import convertcreationdate,convertcreationtime
from django.db.models import Q
from tablib import Dataset


class AddQuestion(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        option_list = []
        i = 0
        option_number = 1
        while f"option_list[{i}][td_option]" in request.POST:
            option = {
                "option":option_number,
                "option_answer": request.POST.get(f"option_list[{i}][td_option]"),
                "option_image": request.FILES.get(f"option_list[{i}][td_option_image]"),
            }
            option_list.append(option)
            i += 1
            option_number +=1
        

        


     
        file_list = request.FILES.getlist('file_list')
        # course = models.BigIntegerField(null=True)
        # topic = models.CharField(max_length=255,null=True)
        # type_of_question = models.CharField(max_length=255,null=True)
        # question_text = models.TextField(null=True)
        # correct_option = models.BigIntegerField(null=True)
        # time_to_solve = models.CharField(max_length=255,null=True)
        # marks = models.CharField(max_length=255,null=True)
        # difficulty_level = models.CharField(max_length=255,null=True)
        # tags = models.TextField(null=True)
        # note = models.TextField(null=True)
        
        data = {}
        data['course'] = request.data.get('course')
        data['module'] = request.data.get('module')
        data['type_of_question'] = request.POST.get('type_of_question')
        data['question_text'] = request.POST.get('question_text')
        data['correct_option'] = request.POST.get('correct_option')
        data['time_to_solve'] = request.POST.get('time_to_solve')
        data['marks'] = request.POST.get('marks')
        data['difficulty_level'] = request.POST.get('difficulty_level') or None
        data['tags'] = request.POST.get('tags') or None
        data['note'] = request.POST.get('note') or None
        data['createdBy'] = str(request.user.id)

        if request.user.user_type != 5:
            if request.user.member_of != '' and request.user.member_of is not None :
                data['tc_id']=str(request.user.member_of)
            else:
                data['tc_id']=str(request.user.id)
        else:
            data['tc_id']=str(request.user.parent_college)

     
        q_serializer = QuestionSerializer(data=data)
        
        folder_path = os.path.join(settings.MEDIA_ROOT,'media','Question Images')
        option_folder_path = os.path.join(settings.MEDIA_ROOT,'media','Question Option Images')
        
        if q_serializer.is_valid():
            q_serializer.save()
            if file_list != "":
                for f in file_list:
                    if f is not None and f != '':
                        file_url=save_file(folder_path,f,request)
                        QuestionImages.objects.create(
                            question_id = q_serializer.data['id'],
                            image = file_url
                        )
                    
            if option_list != "":
                for o in option_list:
                    if o['option_image'] is not None and o['option_image'] != '':
                        file_url=save_file(option_folder_path,o['option_image'],request)
                    else:
                        file_url = ''
                    QuestionOption.objects.create(
                        question_id = q_serializer.data['id'],
                        option_image = file_url,
                        option = o['option'],
                        option_answer = o['option_answer'] 
                    )
                
            response_={
                        "n": 1,
                        "msg": 'Question added successfully',
                        "data":q_serializer.data                        
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
                        "msg": 'Question not added',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class BulkUploadQuestion(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        dataset = Dataset()
        fileerrorlist=[]
        questions = request.FILES['excel_file']
        if not questions.name.endswith('xlsx'):
            response_={
                        "n": 0,
                        "msg": 'File format not supported',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)    
        imported_data = dataset.load(questions.read(), format='xlsx')

        counter=0
        for i in imported_data:
            counter+=1
            data={}
            data['isActive']=True

            if request.user.user_type != 5:
                if request.user.member_of != '' and request.user.member_of is not None :
                    data['tc_id']=str(request.user.member_of)
                else:
                    data['tc_id']=str(request.user.id)
            else:
                data['tc_id']=str(request.user.parent_college)

            course_name=i[0]
            if course_name is not None and course_name !='':
                course_name=str(course_name)
                mapped_course_ids=list(CollegeCourses.objects.filter(college_id=data['tc_id'],isActive=True).values_list('course_id',flat=True))
                course_obj=Course.objects.filter(course_name__in=[course_name.strip().capitalize(),course_name.strip(),course_name.title(),course_name.upper(),course_name.lower(),course_name],id__in=mapped_course_ids,isActive=True).first()
                if course_obj is not None:
                    data['course']=str(course_obj.id)

                else:
                    reason = 'Course not found'
                    error = i + tuple([reason])
                    fileerrorlist.append(error)
                    continue 
            else:
                reason = 'Please provide course name'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 


            module_name=i[1]
            if module_name is not None and module_name !='':
                module_name=str(module_name)

                module_obj=CourseModules.objects.filter(module_name__in=[module_name.strip().capitalize(),module_name.strip(),module_name.title(),module_name.upper(),module_name.lower(),module_name],course_id=int(data['course']),isActive=True).first()
                if module_obj is not None:
                    data['module']=str(module_obj.id)
                else:
                    reason = 'module not found'
                    error = i + tuple([reason])
                    fileerrorlist.append(error)
                    continue 
            else:
                reason = 'Please provide module name'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 
            

            data['type_of_question']='Objective'

        
            question_text=i[2]
            if question_text is not None and question_text !='':
                data['question_text']=str(question_text)
            else:
                reason = 'Please provide question text'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 
            

            option_list = []
            option1=i[3]
            if option1 is not None and option1 !='':
                data['option1']=str(option1)
            else:
                reason = 'Please provide option 1'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 
            option_list.append({"option":1,"option_answer":option1})
            
            option2=i[4]
            if option2 is not None and option2 !='':
                data['option2']=str(option2)
            else:
                reason = 'Please provide option 2'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 
            option_list.append({"option":2,"option_answer":option2})


            option3=i[5]
            if option3 is not None and option3 !='':
                data['option3']=str(option3)
            else:
                reason = 'Please provide option 3'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 
            
            option_list.append({"option":3,"option_answer":option3})


            option4=i[6]
            if option4 is not None and option4 !='':
                data['option4']=str(option4)
            else:
                reason = 'Please provide option 4'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 

            option_list.append({"option":4,"option_answer":option4})

            correct_option=i[7]
            if correct_option is not None and correct_option !='':
                if str(correct_option) in ['1','2','3','4']:
                    data['correct_option']=str(correct_option)
                else:
                    reason = 'Please add correct option form (1,2,3,4)'
                    error = i + tuple([reason])
                    fileerrorlist.append(error)
                    continue 
            else:
                reason = 'Please provide correct option'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 



            time_to_solve=i[8]
            if time_to_solve is not None and time_to_solve !='':
                try:
                    # Convert the input to a float for validation
                    number = float(time_to_solve)
                    # Check if the number is between 0 and 100 and non-negative
                    if 0 <= number:
                        data['time_to_solve']=round(number)
                    else:
                    
                        reason = 'Please provide valid time to solve'
                        error = i + tuple([reason])
                        fileerrorlist.append(error)
                        continue 
                except ValueError:
                    # If conversion to float fails, it's either alphabetic or invalid
                    reason = 'Please provide valid time to solve'
                    error = i + tuple([reason])
                    fileerrorlist.append(error)
                    continue 
            else:
                reason = 'Please provide time to solve'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 


            marks=i[9]
            if marks is not None and marks !='':
                try:
                    # Convert the input to a float for validation
                    number = float(marks)
                    # Check if the number is between 0 and 100 and non-negative
                    if 0 < number:
                        data['marks']=round(number)
                    else:
                        reason = 'Please provide valid marks'
                        error = i + tuple([reason])
                        fileerrorlist.append(error)
                        continue 
                except ValueError:
                    # If conversion to float fails, it's either alphabetic or invalid
                    reason = 'Please provide valid marks'
                    error = i + tuple([reason])
                    fileerrorlist.append(error)
                    continue 
            else:
                reason = 'Please provide marks'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 



            difficulty_level=i[10]
            if difficulty_level is not None and difficulty_level !='':
                if difficulty_level in ['Easy','Medium','Hard']:
                    data['difficulty_level']=str(difficulty_level)
                else:
                    reason = 'Please provide valid difficulty level from Easy ,Medium ,Hard'
                    error = i + tuple([reason])
                    fileerrorlist.append(error)
                    continue 
            else:
                reason = 'Please provide difficulty level'
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 


            # tags [{"value":"1"},{"value":"2"},{"value":"3"},{"value":"4"}]
            tags=i[11]
            if tags is not None and tags !='':
                tags_list=str(tags).split(',')
                data['tags']=[]
                for t in tags_list :
                    data['tags'].append({"value":str(t)})



                data['tags'] = json.dumps(data['tags'])
                
            note=i[12]
            data['note']=note
            data['createdBy'] = str(request.user.id)



            update_obj = Question.objects.filter(course__icontains=data['course'],module__icontains=data['module'],type_of_question=data['type_of_question'],question_text=data['question_text'],isActive=True).first()
            
            if update_obj is not None:
                q_serializer = QuestionSerializer(update_obj,data=data,partial=True)       
            else:
                q_serializer = QuestionSerializer(data=data)        
 
            if q_serializer.is_valid():
                q_serializer.save()
                if option_list != []:
                    QuestionOption.objects.filter(question_id=q_serializer.data['id'],isActive=True).update(isActive=False)
                    for o in option_list:
                        QuestionOption.objects.create(
                            question_id = q_serializer.data['id'],
                            # option_image = file_url,
                            option = o['option'],
                            option_answer = o['option_answer'] 
                        )

            else:
                first_key, first_value = next(iter(q_serializer.errors.items()))
                reason = first_key+' : '+ first_value[0]
                error = i + tuple([reason])
                fileerrorlist.append(error)
                continue 






        if len(fileerrorlist) == 0:

            response_={
                        "n": 1,
                        "msg": 'Question uploaded successfully',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            headers=["Course Name","Module Name","Question","Option 1","Option 2","	Option 3","Option 4","Correct Option","Time To Solve","Marks","Difficulty Level","Tags","Note",]
            response_={
                        "n": 0,
                        "msg": 'Question not uploaded',
                        "data":fileerrorlist,   
                        "headers":headers,                  
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class UpdateQuestion(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        option_list = []
        i = 0
        option_number = 1
        while f"option_list[{i}][td_option]" in request.POST:
            option = {
                "option":option_number,
                "option_answer": request.POST.get(f"option_list[{i}][td_option]"),
                "uploaded_image":request.POST.get(f"option_list[{i}][td_uploaded_image]"),
                "option_image": request.FILES.get(f"option_list[{i}][td_option_image]"),
            }
            option_list.append(option)
            i += 1
            option_number +=1
        

        
     
        file_list = request.FILES.getlist('file_list')
        existing_file_id_list = json.loads(request.data.get('existing_file_id_list'))
        data = {}
        questionid =  request.data.get('question_id')
        data['course'] = request.data.get('course')
        data['module'] = request.data.get('module')
        data['type_of_question'] = request.POST.get('type_of_question')
        data['question_text'] = request.POST.get('question_text')
        data['correct_option'] = request.POST.get('correct_option')
        data['time_to_solve'] = request.POST.get('time_to_solve')
        data['marks'] = request.POST.get('marks')
        data['difficulty_level'] = request.POST.get('difficulty_level') or None
        data['tags'] = request.POST.get('tags') or None
        data['note'] = request.POST.get('note') or None
        data['updatedBy'] = str(request.user.id)
     
        questionobj = Question.objects.filter(id=questionid,isActive=True).first()
        if questionobj is not None:
            q_serializer = QuestionSerializer(questionobj,data=data,partial=True)
            
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Question Images')
            option_folder_path = os.path.join(settings.MEDIA_ROOT,'media','Question Option Images')
            
            if q_serializer.is_valid():
                q_serializer.save()

                existing_file_list = list(QuestionImages.objects.filter(question_id=questionid,isActive=True).values_list('id', flat=True))


                difference_file_list = [item for item in existing_file_list if item not in existing_file_id_list]
                
                if file_list != []:
                    QuestionImages.objects.filter(id__in = difference_file_list).delete()
                    for f in file_list:
                        if f is not None and f != '':
                            file_url=save_file(folder_path,f,request)
                            QuestionImages.objects.create(
                                question_id = q_serializer.data['id'],
                                image = file_url
                            )
                        
                if option_list != []:
                    QuestionOption.objects.filter(question_id=questionid,isActive=True).update(isActive=False)
                    for o in option_list:
                        if o['option_image'] is not None and o['option_image'] != '':
                            file_url=save_file(option_folder_path,o['option_image'],request)
                        elif o['uploaded_image'] is not None and o['uploaded_image'] != '':
                            file_url = o['uploaded_image']
                        else:
                            file_url = ''
                        QuestionOption.objects.create(
                            question_id = q_serializer.data['id'],
                            option_image = file_url,
                            option = o['option'],
                            option_answer = o['option_answer'] 
                        )
                    
                response_={
                            "n": 1,
                            "msg": 'Question updated successfully',
                            "data":q_serializer.data                        
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
                        "msg": 'Question not updated',
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
                        "msg": 'Question not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)





import os
from urllib.parse import urlparse, unquote
class QuestionDetail(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
            
        question_id = request_data.get("question_id")  
        if question_id is None and question_id == "":
            
            response_={
                        "n": 0,
                        "msg": 'Please provide question Id',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        question_object = Question.objects.filter(isActive=True,id = question_id).first()
        if question_object is not None:
            question_serializer = QuestionSerializer(question_object)
            
            question_serializer_data = question_serializer.data

            course_list = question_serializer_data['course']
            module_list = question_serializer_data['module']

            course_list = [int(x) for x in question_serializer_data['course'].split(",")]
            module_list = [int(x) for x in question_serializer_data['module'].split(",")]
            
            question_serializer_data.update({
                "course" : course_list,
                "module":  module_list
            })
            
            question_image_object = QuestionImages.objects.filter(isActive=True,question_id=question_id)
            question_image_ser = customised_QuestionImagesSerializer(question_image_object,many=True)
            for q in question_image_ser.data:
                path = unquote(urlparse(q['image']).path)
                filename = os.path.basename(path)
                q['file_name'] = filename
            question_serializer_data.update({
                "question_images_data" : question_image_ser.data
            })
            
            question_option_object = QuestionOption.objects.filter(isActive=True,question_id=question_id,option__in=[1,2,3,4]).order_by('option')
            question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
            question_serializer_data.update({
                "question_option_data" : question_option_ser.data
            })
            
            response_={
                        "n": 1,
                        "msg": 'Question data fetched successfully',
                        "data":question_serializer_data                    
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
                        "msg": 'Question data not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            



class QuestionList(GenericAPIView):
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
        
       
        if request.user.member_of != '' and request.user.member_of is not None :
            tc_id =str(request.user.member_of)
        else:
            tc_id=str(request.user.id)


        tc_course_ids=list(CollegeCourses.objects.filter(college_id=tc_id).order_by('course_id').distinct('course_id').values_list('course_id',flat=True))
        
        if request.user.user_type == 2:
            question_object = Question.objects.filter(isActive=True).order_by('-id')
        else:

    
            tc_course_ids=list(map(str,tc_course_ids))
            
            question_object = Question.objects.filter(isActive=True,course__in=tc_course_ids).order_by('-id')

        course=request_data.get('course')
        if course is not None and course !='':    
            question_object = question_object.filter(course__in=[course]).order_by('-id')
           

           
        difficulty=request_data.get('difficulty')
        if difficulty is not None and difficulty !='':    
            question_object = question_object.filter(difficulty_level__in=[difficulty]).order_by('-id')


        if question_object.exists():            
            paginate_object = self.paginate_queryset(question_object)
            serializer = QuestionSerializer(paginate_object,many=True)
            for i in serializer.data:
                course_list = [int(x) for x in i['course'].split(",")]
   
                course_object = Course.objects.filter(isActive=True,id__in =course_list).values_list('course_name')
                i['course_name'] = course_object

                if i['module'] != '':
                    modules_list = [int(x) for x in i['module'].split(",")]
                    course_module_object = CourseModules.objects.filter(isActive=True,id__in = modules_list).values_list('module_name')
                    if course_module_object != []:
                        i['module_name'] = course_module_object
                    else:
                        i['module_name'] = ''
                else:
                    i['module_name'] = ''
                
                question_image_object = QuestionImages.objects.filter(isActive=True,question_id=i['id'])
                question_image_ser = QuestionImagesSerializer(question_image_object,many=True)
              
                i["question_images_data"] = question_image_ser.data              
                
                question_option_object = QuestionOption.objects.filter(isActive=True,question_id=i['id'])
                question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
               
                i["question_option_data"] = question_option_ser.data

                if i['tags'] != "" and i['tags'] is not None:
                    i['tags_list'] = json.loads(i['tags'])
                else:
                    i['tags_list'] = []

                crtby = i['createdBy']
                userobj = UserAdmin.objects.filter(id=crtby).first()
                if userobj is not None and userobj != '':
                    if userobj.user_type == 5:
                        i['added_by'] = userobj.first_name +" "+userobj.last_name
                    else:
                        i['added_by'] = userobj.name
                else:
                    i['added_by'] = ''


                i['added_on']= convertcreationdate(i['createdAt'])

                queslikeobj = QuestionLike.objects.filter(question_id=i['id'],isActive=True).first()
                if queslikeobj is not None:
                    i['is_like'] = queslikeobj.is_like
                    i['is_dislike'] = queslikeobj.is_dislike
                else:
                    i['is_like'] = False
                    i['is_dislike'] = False

                i['total_reviews'] = QuestionLike.objects.filter(Q(question_id=i['id']),Q(isActive=True),(Q(is_like=True)|Q(is_dislike=True))).count()


                    
                
            if encryped_header == "1" :
                paigna=self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                paigna=self.get_paginated_response(serializer.data)
        else:
            response_={
                        "n": 0,
                        "msg": 'Question not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            



class GetDislikeReviews(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
            
        question_id = request_data.get("id")
        if question_id is not None and question_id != '':
            Questionobj = Question.objects.filter(id=question_id).first()
            quesser = QuestionSerializer(Questionobj)
            ser_data = quesser.data

            crtby = ser_data['createdBy']
            userobj = UserAdmin.objects.filter(id=crtby).first()
            if userobj is not None and userobj != '':
                if userobj.user_type == 5:
                    added_by = userobj.first_name +" "+userobj.last_name
                else:
                   added_by = userobj.name
            else:
                added_by = ''

            added_on= convertcreationdate(ser_data['createdAt'])

            totallikes = QuestionLike.objects.filter(question_id=ser_data['id'],isActive=True,is_like=True).count()
            totaldislikes =  QuestionLike.objects.filter(question_id=ser_data['id'],isActive=True,is_dislike=True).count()

            ser_data.update({
                'added_by':added_by,
                'added_on':added_on,
                'totallikes':totallikes,
                'totaldislikes':totaldislikes
            })
                        

            questlikes = QuestionLike.objects.filter(question_id=question_id,is_dislike=True,isActive=True)
            questlikeser = QuestionLikeSerializer(questlikes,many=True)
            for i in questlikeser.data:
                crtby = i['actionby']
                userobj = UserAdmin.objects.filter(id=crtby).first()
                if userobj is not None and userobj != '':
                    if userobj.user_type == 5:
                        i['actionby'] = userobj.first_name +" "+userobj.last_name
                    else:
                        i['actionby'] = userobj.name
                else:
                    i['actionby'] = ''


                i['action_at']= convertcreationdate(i['createdAt'])
                i['actionat_time'] = convertcreationtime(i['createdAt'])


            
            context = {
                'quedata':ser_data,
                'comments':questlikeser.data
            }

            response_={
                        "n": 1,
                        "msg": 'Question data fetched successfully',
                        "data":context                    
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
                        "msg": 'Question id not provided',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)












class ValidateQuestionList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        
        question_object = Question.objects.filter(isActive=True,is_archive=False)
        if question_object.exists():            
            paginate_object = self.paginate_queryset(question_object)
            serializer = QuestionSerializer(paginate_object,many=True)
            for i in serializer.data:
                # course_list = [int(x) for x in i['course'].split(",")]
   
                course_object = Course.objects.filter(isActive=True,id__in =i['course']).values_list('course_name')
                i['course_name'] = course_object

                if i['module'] != '':
                    # modules_list = [int(x) for x in i['module'].split(",")]
                    course_module_object = CourseModules.objects.filter(isActive=True,id__in = i['module']).values_list('module_name')
                    if course_module_object != []:
                        i['module_name'] = course_module_object
                    else:
                        i['module_name'] = ''
                else:
                    i['module_name'] = ''
                
                question_image_object = QuestionImages.objects.filter(isActive=True,question_id=i['id'])
                question_image_ser = QuestionImagesSerializer(question_image_object,many=True)
              
                i["question_images_data"] = question_image_ser.data              
                
                question_option_object = QuestionOption.objects.filter(isActive=True,question_id=i['id'])
                question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
               
                i["question_option_data"] = question_option_ser.data

                if i['tags'] != "" and i['tags'] is not None:
                    i['tags_list'] = json.loads(i['tags'])
                else:
                    i['tags_list'] = []

                crtby = i['createdBy']
                userobj = UserAdmin.objects.filter(id=crtby).first()
                if userobj is not None and userobj != '':
                    if userobj.user_type == 5:
                        i['added_by'] = userobj.first_name +" "+userobj.last_name
                    else:
                        i['added_by'] = userobj.name
                else:
                    i['added_by'] = ''


                i['added_on']= convertcreationdate(i['createdAt'])

                queslikeobj = QuestionLike.objects.filter(question_id=i['id'],isActive=True).first()
                if queslikeobj is not None:
                    i['is_like'] = queslikeobj.is_like
                    i['is_dislike'] = queslikeobj.is_dislike
                else:
                    i['is_like'] = False
                    i['is_dislike'] = False

                i['totallikes'] = QuestionLike.objects.filter(question_id=i['id'],isActive=True,is_like=True).count()
                i['totaldislikes'] =  QuestionLike.objects.filter(question_id=i['id'],isActive=True,is_dislike=True).count()
                    
                
            if encryped_header == "1" :
                paigna=self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                paigna=self.get_paginated_response(serializer.data)
        else:
            response_={
                        "n": 0,
                        "msg": 'Question not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

class ArchiveQuestion(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
            
        question_id = request_data.get("questionid")  
        archive_reason = request_data.get("archivereason")  

        if question_id is None and question_id == "":
            response_={
                        "n": 0,
                        "msg": 'Please provide question Id',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200) 
        else:
            quesobj = Question.objects.filter(id=question_id,isActive=True).first()
            if quesobj is not None and quesobj != '':
                if quesobj.is_archive is False:
                    quesobj.is_archive = True
                    quesobj.archive_reason = archive_reason
                    quesobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Question Archived successfully',
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
                        "msg": 'question already archived',
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
                        "msg": 'question not found',
                        "data":[]                     
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200) 



 
        
class GetDuplicateQuestions(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
            

        questionid = request_data.get("questionid")  
        course = request_data.get("course")  
        module = request_data.get("module")  
        severity_level = request_data.get("severity_level") 
        type = request_data.get("type")  

        if course is not None and course != '':
            if module is not None and module != '':
                Questionobj = Question.objects.filter(course__icontains=course,module__icontains=module,isActive=True).exclude(id=questionid)
            else:
                Questionobj = Question.objects.filter(course__icontains=course,isActive=True).exclude(id=questionid)
            
            sev_levelobj = ''
            if severity_level is not None and severity_level != '':
                if severity_level != 'All':
                    sev_levelobj = Questionobj.filter(difficulty_level=severity_level)
                else:
                    sev_levelobj = Questionobj
            else:
                sev_levelobj = Questionobj

            typeobj = ''
            if type is not None and type != '':
                if type != 'All':
                    typeobj = sev_levelobj.filter(type_of_question=type)
                else:
                    typeobj = sev_levelobj
            else:
                typeobj = sev_levelobj


            finalobject = typeobj
            queser = QuestionSerializer(finalobject,many=True)
            response_={
                        "n": 1,
                        "msg": 'Questions found successfully',
                        "data":queser.data                        
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
                    "msg": 'Please Provide Course',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200) 


class SaveDuplicates(GenericAPIView):
    
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
        data['question_id'] = request_data.get("questionid")  
        data['course_id'] = request_data.get("course") 
        data['module_id'] = request_data.get("module")  
        data['severity_level'] = request_data.get("severity_level") 
        data['type_of_question'] = request_data.get("type") 
        data['duplicate_of'] = request_data.get("duplicatequestions") 
        if  data['duplicate_of'] is not None and  data['duplicate_of'] != '':
            if data['module_id'] == '':
                data['module_id'] = None
            if data['question_id'] is not None and data['question_id'] != '':
                Questionobj = Question.objects.filter(id=data['question_id']).first()
                if Questionobj is not None :
                    dupser = DuplicateQuestionSerializer(data=data)
                    if dupser.is_valid():
                        dupser.save()

                        Questionobj.is_duplicate=True
                        Questionobj.save()

                        response_={
                        "n": 1,
                        "msg": 'Duplicate Questions saved successfully',
                        "data":''                      
                        }
                        if encryped_header == "1" :
                            data_to_serialize = convert_decimals_to_float(response_)
                            encdata = encrypt_data(json.dumps(data_to_serialize))
                            return Response(encdata,status=200)
                        else:
                            return Response(response_,status=200)
                    else:
                        print("error",dupser.errors)
                else:
                    response_={
                    "n": 0,
                    "msg": 'Cound not find Question',
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
                    "msg": 'Please Provide Question Id',
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
                    "msg": 'Please Provide Duplicates',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200) 
            

class LikeQuestions(GenericAPIView):
    
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
        data['question_id'] = request_data.get("questionid") 
        data['is_like'] = True
        data['actionby'] = str(request.user.id)
        data['createdBy'] = str(request.user.id)
        if data['question_id'] is not None and  data['question_id'] != '':
            queslikeexist = QuestionLike.objects.filter(question_id=data['question_id'],actionby=data['actionby'],isActive=True).first()
            if queslikeexist is not None :
                likestatus = queslikeexist.is_like
                if likestatus == True:
                    response_={
                    "n": 0,
                    "msg": 'Question already liked',
                    "data":[]                     
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    queslikeexist.is_like = data['is_like']
                    queslikeexist.is_dislike = False
                    queslikeexist.dislike_reason = ''
                    queslikeexist.actionby = data['actionby']
                    queslikeexist.createdBy = data['actionby']
                    queslikeexist.save()

                    response_={
                    "n": 1,
                    "msg": 'Question liked successfully',
                    "data":''                      
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                likeser = QuestionLikeSerializer(data=data)
                if likeser.is_valid():
                    likeser.save()

                    response_={
                    "n": 1,
                    "msg": 'Question liked successfully',
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
                "msg": 'Please Provide Question Id',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class DislikeQuestions(GenericAPIView):
    
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
        data['question_id'] = request_data.get("questionid") 
        data['dislike_reason'] = request_data.get("dislike_reason") 
        data['is_dislike'] = True
        data['createdBy'] = str(request.user.id)
        data['actionby'] = str(request.user.id)
        if data['question_id'] is not None and  data['question_id'] != '':
            queslikeexist = QuestionLike.objects.filter(question_id=data['question_id'],actionby=data['actionby'],isActive=True).first()
            if queslikeexist is not None :
                likestatus = queslikeexist.is_dislike
                if likestatus == True:
                    response_={
                    "n": 0,
                    "msg": 'Question already disliked',
                    "data":[]                     
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    queslikeexist.is_dislike = data['is_dislike']
                    queslikeexist.is_like = False
                    queslikeexist.dislike_reason = data['dislike_reason']
                    queslikeexist.actionby = data['actionby']
                    queslikeexist.createdBy = data['actionby']
                    queslikeexist.save()

                    response_={
                    "n": 1,
                    "msg": 'Question disliked successfully',
                    "data":''                      
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                dislikeser = QuestionLikeSerializer(data=data)
                if dislikeser.is_valid():
                    dislikeser.save()

                    response_={
                    "n": 1,
                    "msg": 'Question disliked successfully',
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
                "msg": 'Please Provide Question Id',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)



class ArchiveQuestionList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        
        question_object = Question.objects.filter(isActive=True,is_archive=True)
        if question_object.exists():            
            paginate_object = self.paginate_queryset(question_object)
            serializer = QuestionSerializer(paginate_object,many=True)
            for i in serializer.data:
                # course_list = [int(x) for x in i['course'].split(",")]
   
                course_object = Course.objects.filter(isActive=True,id__in =i['course']).values_list('course_name')
                i['course_name'] = course_object

                if i['module'] != '':
                    # modules_list = [int(x) for x in i['module'].split(",")]
                    course_module_object = CourseModules.objects.filter(isActive=True,id__in = i['module']).values_list('module_name')
                    if course_module_object != []:
                        i['module_name'] = course_module_object
                    else:
                        i['module_name'] = ''
                else:
                    i['module_name'] = ''
                
                question_image_object = QuestionImages.objects.filter(isActive=True,question_id=i['id'])
                question_image_ser = QuestionImagesSerializer(question_image_object,many=True)
              
                i["question_images_data"] = question_image_ser.data              
                
                question_option_object = QuestionOption.objects.filter(isActive=True,question_id=i['id'])
                question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
               
                i["question_option_data"] = question_option_ser.data

                if i['tags'] != "":
                    i['tags_list'] = json.loads(i['tags'])
                else:
                    i['tags_list'] = []

                crtby = i['createdBy']
                userobj = UserAdmin.objects.filter(id=crtby).first()
                if userobj is not None and userobj != '':
                    if userobj.user_type == 5:
                        i['added_by'] = userobj.first_name +" "+userobj.last_name
                    else:
                        i['added_by'] = userobj.name
                else:
                    i['added_by'] = ''


                i['added_on']= convertcreationdate(i['createdAt'])
                    
                
            if encryped_header == "1" :
                paigna=self.get_paginated_response(serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                paigna=self.get_paginated_response(serializer.data)
        else:
            response_={
                        "n": 0,
                        "msg": 'Question not found',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
      

class RemoveArchiveQuestion(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
            
        question_id = request_data.get("questionid")  
        if question_id is None and question_id == "":
            response_={
                        "n": 0,
                        "msg": 'Please provide question Id',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200) 
        else:
            quesobj = Question.objects.filter(id=question_id,isActive=True).first()
            if quesobj is not None and quesobj != '':
                if quesobj.is_archive is True:
                    quesobj.is_archive = False
                    quesobj.archive_reason = ''
                    quesobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Question removed from Archive successfully',
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
                        "msg": 'question already unarchived',
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
                        "msg": 'question not found',
                        "data":[]                     
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200) 




class DeleteQuestion(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')  
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
            
        question_id = request_data.get("questionid")  

        if question_id is None and question_id == "":
            response_={
                        "n": 0,
                        "msg": 'Please provide question Id',
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200) 
        else:
            quesobj = Question.objects.filter(id=question_id,isActive=True).first()
            if quesobj is not None and quesobj != '':
                if quesobj.isActive is True:
                    quesobj.isActive = False
                    quesobj.save()

                    response_={
                            "n": 1,
                            "msg": 'Question deleted successfully',
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
                        "msg": 'question already inactive',
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
                        "msg": 'question not found',
                        "data":[]                     
                    }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200) 

