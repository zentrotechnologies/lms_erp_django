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
from adminauth.common import convertcreationdate
from questionbank.models import * 
from questionbank.serializers import *
import random
import itertools
from course.models import *
from course.serializers import *
from schedule.models import *
from schedule.serializers import *
from enrollments.models import *
from candidate.jwt import CandidateJWTAuthentication
import ast
from candidate.models import *
from candidate.serializers import *
from candidate.jwt import *
import threading
import requests
import  pdfkit
from django.template import Template, Context
from django.template.loader import get_template, render_to_string
from django.db.models import Q
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage



pdf_conv_template = get_template(os.path.join(BASE_DIR, "templates/candidate-certificate.html"))
candidate_exam_set_question_url = hostURL + '/api/exam/view-candidate-exam-questioin-set'

def find_combinations(questions, target_marks, target_time):
    n = len(questions)
    
    # DP table to store combinations of (marks, time)
    dp = [[None] * (target_time + 1) for _ in range(target_marks + 1)]
    dp[0][0] = []  # Starting condition: no marks, no time, no questions

    for i in range(n):
        question = questions[i]
        mark, time, q_id = int(question['marks']), int(question['time_to_solve']), question['id']
        
        # Traverse the dp table in reverse to avoid reusing the same question
        for m in range(target_marks, mark - 1, -1):
            for t in range(target_time, time - 1, -1):
                if dp[m - mark][t - time] is not None:
                    dp[m][t] = dp[m - mark][t - time] + [{'id': q_id, 'marks': mark, 'time_to_solve': time}]
    
    # Return the combination of questions that match the exact total marks and time
    return dp[target_marks][target_time]

class FindNumberOfExamQuestion(GenericAPIView):
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
        data['name'] =  request_data.get('name')
        data['course'] =  request_data.get('course')
        data['time_to_solve'] =  request_data.get('time_to_solve')
        data['difficulty_level'] =  request_data.get('difficulty_level')
        data['question_type'] =  request_data.get('question_type')
        data['exam_mode'] =  request_data.get('exam_mode')
        data['total_marks'] =  request_data.get('total_marks')
        
        question_object = Question.objects.filter(isActive=True,course__icontains=data['course'],difficulty_level=data['difficulty_level'])
        question_ser = QuestionSerializer(question_object,many=True)
        
        
        questions_list = question_ser.data
        
        random.shuffle(questions_list)
        combination = find_combinations(questions_list, int(data['total_marks']), int(data['time_to_solve']))
        if combination:
            for i in combination:
                deactivate_exam_set = TemporaryQuestionExamSet.objects.filter(name=data['name'],course=data['course']).update(isActive=True)
            
            shortlist_combination = combination[:4]
            response_={
                "n": 1,
                "msg": 'Exam Set created successfully',
                "data":combination,
                "length":len(combination)          
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
                "msg": 'No combinations found of the questions',
                "data":[]                
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
def generate_question_sets(filtered_questions, module_list, total_marks, total_time, no_of_sets, no_of_questions):
    """
    Generates exam sets either by module-specific requirements or by overall constraints.
    
    Parameters:
      filtered_questions: List[dict]
          List of question dictionaries.
      module_list: List[dict]
          List of module specifications. Each dict should have:
            - 'module_id': identifier.
            - 'module_no_of_question': number of questions required from that module.
          If empty, the function will generate sets based solely on overall constraints.
      total_marks: int
          Overall total marks required.
      total_time: int
          Overall total time required.
      no_of_sets: int
          Number of exam sets to generate.
      no_of_questions: int
          Total number of questions to pick when module_list is empty.
    
    Returns:
      List[List[dict]]: A list of exam sets, each being a list of question dictionaries.
    """
    # --- Case 1: When module_list is provided (module-based selection) ---
    if module_list:
        # Group questions by module_id.
        module_questions = {}
        # module_questions = {}
        for q in filtered_questions:
            module_field = q.get('module')
            if module_field:
                module_ids = [m.strip() for m in module_field.split(',')]
                for mod_id in module_ids:
                    module_questions.setdefault(mod_id, []).append(q)
        

        for mod_id in module_questions:
            random.shuffle(module_questions[mod_id])
      

        module_combinations = {}
        for module in module_list:
            mod_id = module['module_id']
            required_count = int(module.get('module_no_of_question', 0))
            available = module_questions.get(mod_id, [])
       
            if len(available) < required_count:
                raise ValueError(
                    f"Not enough questions in module {mod_id} "
                    f"(needed: {required_count}, available: {len(available)})"
                )
            # module_combinations[mod_id] = list(itertools.combinations(available, required_count))
            
            combos = list(itertools.combinations(available, required_count))
            random.shuffle(combos)
            module_combinations[mod_id] = combos
        
        # Maintain the module order as specified in module_list.
   
        ordered_combos = [module_combinations[module['module_id']] for module in module_list]

        valid_sets = []
        # Generate full exam sets using the Cartesian product across module combinations.
        for combo_tuple in itertools.product(*ordered_combos):
            # Flatten the tuple of tuples into a single list of questions.
            full_set = [q for module_combo in combo_tuple for q in module_combo]
            # Check that there are no duplicate questions in the set.
            unique_ids = set(q['id'] for q in full_set)
            if len(unique_ids) != len(full_set):
                # Duplicate question detected; skip this combination.
                continue
            
            random.shuffle(full_set)
            # Validate overall constraints: total marks and total time.
            sum_marks = sum(int(q['marks']) for q in full_set)
            sum_time = sum(int(q['time_to_solve']) for q in full_set)
            if sum_marks == int(total_marks) and sum_time == int(total_time):
                valid_sets.append(full_set)
                if len(valid_sets) >= int(no_of_sets):
                    break
                
        random.shuffle(valid_sets)
        return valid_sets

    # --- Case 2: When module_list is empty (overall constraints only) ---
    else:
        valid_sets = []
        required_count = int(no_of_questions)
        
        random.shuffle(filtered_questions)
        # Generate all combinations of questions of length equal to no_of_questions.
        for comb in itertools.combinations(filtered_questions, required_count):

            if len(set(q['id'] for q in comb)) != len(comb):
                continue
            
            sum_marks = sum(int(q['marks']) for q in comb)
            sum_time = sum(int(q['time_to_solve']) for q in comb)
            if sum_marks == int(total_marks) and sum_time == int(total_time):
                valid_sets.append(list(comb))
                if len(valid_sets) >= int(no_of_sets):
                    break
        random.shuffle(valid_sets)
        return valid_sets 



def generate_unique_question_sets(filtered_questions, module_list, total_marks, total_time, no_of_sets, no_of_questions):
    print("filtered_questions",filtered_questions)
    # --- Track used questions globally ---
    used_question_ids = set()
    valid_sets = []

    # --- Case 1: When module_list is provided (module-based selection) ---
    if module_list:
        # Group questions by module_id.
        module_questions = {}
        for q in filtered_questions:
            module_field = q.get('module')
            if module_field:
                module_ids = [m.strip() for m in module_field.split(',')]
                for mod_id in module_ids:
                    module_questions.setdefault(mod_id, []).append(q)

        # Shuffle questions within each module
        for mod_id in module_questions:
            random.shuffle(module_questions[mod_id])

        # Generate sets one by one to ensure no question reuse
        while len(valid_sets) < int(no_of_sets):
            current_set = []
            current_set_question_ids = set()
            valid = True
            
            # Try to build a valid set
            for module in module_list:
                mod_id = module['module_id']
                required_count = int(module.get('module_no_of_question', 0))
                available = [q for q in module_questions.get(mod_id, []) 
                            if q['id'] not in used_question_ids 
                            and q['id'] not in current_set_question_ids]
                
                if len(available) < required_count:
                    valid = False
                    break  # Can't build this set
                
                # Select required questions randomly
                selected = random.sample(available, required_count)
                current_set.extend(selected)
                current_set_question_ids.update(q['id'] for q in selected)
            
            if not valid:
                break  # No more valid sets can be created
            
            # Check total marks and time
            sum_marks = sum(int(q['marks']) for q in current_set)
            sum_time = sum(int(q['time_to_solve']) for q in current_set)
            
            if sum_marks == int(total_marks) and sum_time == int(total_time):
                # Add to used questions and valid sets
                used_question_ids.update(current_set_question_ids)
                random.shuffle(current_set)
                valid_sets.append(current_set)

    # --- Case 2: When module_list is empty (overall constraints only) ---
    else:
        required_count = int(no_of_questions)
        available_questions = [q for q in filtered_questions if q['id'] not in used_question_ids]
        
        # Generate combinations without reusing questions
        for comb in itertools.combinations(available_questions, required_count):
            # Skip if duplicates (though unlikely since we filtered)
            if len(set(q['id'] for q in comb)) != len(comb):
                continue
            
            sum_marks = sum(int(q['marks']) for q in comb)
            sum_time = sum(int(q['time_to_solve']) for q in comb)
            
            if sum_marks == int(total_marks) and sum_time == int(total_time):
                valid_sets.append(list(comb))
                used_question_ids.update(q['id'] for q in comb)
                
                if len(valid_sets) >= int(no_of_sets):
                    break

    random.shuffle(valid_sets)
    return valid_sets


from collections import defaultdict

import math

# def generate_unique_question_sets(filtered_questions, module_list, total_marks, total_time, no_of_sets, no_of_questions):
#     # Track used questions globally
#     used_question_ids = set()
#     valid_sets = []
    
#     # Helper function to count difficulties
#     def count_difficulties(questions):
#         counts = {'Hard': 0, 'Medium': 0, 'Easy': 0}
#         for q in questions:
#             if q['difficulty_level'] == 'Hard':
#                 counts['Hard'] += 1
#             elif q['difficulty_level'] == 'Medium':
#                 counts['Medium'] += 1
#             elif q['difficulty_level'] == 'Easy':
#                 counts['Easy'] += 1
#         return counts

#     # --- Case 1: Module-based selection ---
#     if module_list:
#         # Calculate total questions needed
#         total_questions = sum(int(module['module_no_of_question']) for module in module_list)
        
#         # Calculate required difficulty counts
#         hard_count = math.floor(0.4 * total_questions + 0.5)
#         medium_count = math.floor(0.4 * total_questions + 0.5)
#         easy_count = total_questions - hard_count - medium_count
        
#         # Group questions by module
#         module_questions = {}
#         for q in filtered_questions:
#             module_field = q.get('module')
#             if module_field:
#                 module_ids = [m.strip() for m in module_field.split(',')]
#                 for mod_id in module_ids:
#                     module_questions.setdefault(mod_id, []).append(q)

#         # Shuffle questions within each module
#         for mod_id in module_questions:
#             random.shuffle(module_questions[mod_id])

#         # Generate sets sequentially
#         print("Generating sets...", no_of_sets)
#         while len(valid_sets) < int(no_of_sets):
#             print("Current valid sets:", len(valid_sets), "of", no_of_sets)
#             current_set = []
#             current_set_question_ids = set()
#             valid = True
            
#             # Build the set module by module
#             for module in module_list:
#                 mod_id = module['module_id']
#                 required_count = int(module.get('module_no_of_question', 0))
#                 available = [
#                     q for q in module_questions.get(mod_id, []) 
#                     if q['id'] not in used_question_ids 
#                     and q['id'] not in current_set_question_ids
#                 ]
                
#                 if len(available) < required_count:
#                     valid = False
#                     break
                
#                 selected = random.sample(available, required_count)
#                 current_set.extend(selected)
#                 current_set_question_ids.update(q['id'] for q in selected)
            
#             if not valid:
#                 break
                
#             # Check marks and time
#             sum_marks = sum(int(q['marks']) for q in current_set)
#             sum_time = sum(int(q['time_to_solve']) for q in current_set)
            
#             # Check difficulty distribution
#             diff_counts = count_difficulties(current_set)
            
#             # Validate all constraints
#             print("Checking constraints...", sum_marks,total_marks, sum_time,total_time, diff_counts)
#             print("Required counts:", hard_count, medium_count, easy_count)
#             if (sum_marks == int(total_marks) and \
#                (sum_time == int(total_time)) and \
#                (diff_counts['Hard'] == hard_count) and \
#                (diff_counts['Medium'] == medium_count) and \
#                (diff_counts['Easy'] == easy_count)):
                
#                 used_question_ids.update(current_set_question_ids)
#                 random.shuffle(current_set)
#                 valid_sets.append(current_set)

#     # --- Case 2: Overall constraints only ---
#     else:
#         # Calculate required difficulty counts
#         total_questions = int(no_of_questions)
#         hard_count = math.floor(0.4 * total_questions + 0.5)
#         medium_count = math.floor(0.4 * total_questions + 0.5)
#         easy_count = total_questions - hard_count - medium_count
        
#         # Categorize questions by difficulty
#         hard_questions = []
#         medium_questions = []
#         easy_questions = []
        
#         for q in filtered_questions:
#             if q['difficulty_level'] == 'Hard':
#                 hard_questions.append(q)
#             elif q['difficulty_level'] == 'Medium':
#                 medium_questions.append(q)
#             elif q['difficulty_level'] == 'Easy':
#                 easy_questions.append(q)
        
#         # Generate sets sequentially
#         while len(valid_sets) < int(no_of_sets):
#             # Check if we have enough questions
#             if (len(hard_questions) < hard_count or
#                 len(medium_questions) < medium_count or
#                 len(easy_questions) < easy_count):
#                 break
                
#             # Select questions by difficulty
#             selected_hard = random.sample(
#                 [q for q in hard_questions if q['id'] not in used_question_ids],
#                 hard_count
#             )
#             selected_medium = random.sample(
#                 [q for q in medium_questions if q['id'] not in used_question_ids],
#                 medium_count
#             )
#             selected_easy = random.sample(
#                 [q for q in easy_questions if q['id'] not in used_question_ids],
#                 easy_count
#             )
            
#             candidate_set = selected_hard + selected_medium + selected_easy
#             candidate_ids = [q['id'] for q in candidate_set]
            
#             # Check for duplicates
#             if len(set(candidate_ids)) != len(candidate_ids):
#                 continue
                
#             # Check marks and time
#             sum_marks = sum(int(q['marks']) for q in candidate_set)
#             sum_time = sum(int(q['time_to_solve']) for q in candidate_set)
            
#             if sum_marks == int(total_marks) and sum_time == int(total_time):
#                 valid_sets.append(candidate_set)
#                 used_question_ids.update(candidate_ids)
#                 # Remove used questions from pools
#                 for q in selected_hard:
#                     hard_questions.remove(q)
#                 for q in selected_medium:
#                     medium_questions.remove(q)
#                 for q in selected_easy:
#                     easy_questions.remove(q)

#     # Add difficulty_level to each question in each set (without modifying originals)
#     transformed_sets = []
#     for question_set in valid_sets:
#         transformed_set = []
#         for question in question_set:
#             # Create shallow copy and add new key
#             transformed_question = {**question, 'difficulty_level': question['difficulty_level']}
#             transformed_set.append(transformed_question)
#         transformed_sets.append(transformed_set)
    
#     return transformed_sets

# def generate_unique_question_sets(filtered_questions, module_list, total_marks, total_time, no_of_sets, no_of_questions):
#     # Pre-filter questions by difficulty level at the start
#     hard_questions = [q for q in filtered_questions if q['difficulty_level'] == 'Hard']
#     medium_questions = [q for q in filtered_questions if q['difficulty_level'] == 'Medium']
#     easy_questions = [q for q in filtered_questions if q['difficulty_level'] == 'Easy']
    
#     # Track used questions globally
#     used_question_ids = set()
#     valid_sets = []
    
#     # Helper function to count difficulties
#     def count_difficulties(questions):
#         counts = {'Hard': 0, 'Medium': 0, 'Easy': 0}
#         for q in questions:
#             counts[q['difficulty_level']] += 1
#         return counts
#     print("diff_counts:", count_difficulties(filtered_questions))
#     # --- Case 1: Module-based selection ---
#     if module_list:
#         # Calculate total questions needed
#         total_questions = sum(int(module['module_no_of_question']) for module in module_list)
        
#         # Calculate required difficulty counts
#         hard_count = math.floor(0.4 * total_questions + 0.5)
#         medium_count = math.floor(0.4 * total_questions + 0.5)
#         easy_count = total_questions - hard_count - medium_count
        
#         # Group pre-filtered questions by module
#         module_questions = {}
#         for mod_id in {m['module_id'] for m in module_list}:
#             mod_questions = []
#             mod_questions.extend([q for q in hard_questions if mod_id in [m.strip() for m in q['module'].split(',')]])
#             mod_questions.extend([q for q in medium_questions if mod_id in [m.strip() for m in q['module'].split(',')]])
#             mod_questions.extend([q for q in easy_questions if mod_id in [m.strip() for m in q['module'].split(',')]])
#             module_questions[mod_id] = mod_questions

#         # Generate sets sequentially
#         while len(valid_sets) < int(no_of_sets):
#             current_set = []
#             current_set_question_ids = set()
#             valid = True
            
#             # Build the set module by module
#             for module in module_list:
#                 mod_id = module['module_id']
#                 required_count = int(module.get('module_no_of_question', 0))
#                 available = [
#                     q for q in module_questions.get(mod_id, []) 
#                     if q['id'] not in used_question_ids 
#                     and q['id'] not in current_set_question_ids
#                 ]
                
#                 if len(available) < required_count:
#                     valid = False
#                     break
                
#                 selected = random.sample(available, required_count)
#                 current_set.extend(selected)
#                 current_set_question_ids.update(q['id'] for q in selected)
            
#             if not valid:
#                 break
                
#             # Check marks and time
#             sum_marks = sum(int(q['marks']) for q in current_set)
#             sum_time = sum(int(q['time_to_solve']) for q in current_set)
            
#             # Check difficulty distribution
#             diff_counts = count_difficulties(current_set)
            
#             # Validate all constraints
#             if (sum_marks == int(total_marks) and 
#                 sum_time == int(total_time) and
#                 diff_counts['Hard'] == hard_count and
#                 diff_counts['Medium'] == medium_count and
#                 diff_counts['Easy'] == easy_count):
                
#                 used_question_ids.update(current_set_question_ids)
#                 random.shuffle(current_set)
#                 valid_sets.append(current_set)

#     # --- Case 2: Overall constraints only ---
#     else:
#         # Calculate required difficulty counts
#         total_questions = int(no_of_questions)
#         hard_count = math.floor(0.4 * total_questions + 0.5)
#         medium_count = math.floor(0.4 * total_questions + 0.5)
#         easy_count = total_questions - hard_count - medium_count
        
#         # Generate sets using pre-filtered lists
#         while len(valid_sets) < int(no_of_sets):
#             # Check if we have enough questions
#             if (len(hard_questions) < hard_count or
#                 len(medium_questions) < medium_count or
#                 len(easy_questions) < easy_count):
#                 break
                
#             # Select questions by difficulty from pre-filtered lists
#             selected_hard = random.sample(
#                 [q for q in hard_questions if q['id'] not in used_question_ids],
#                 hard_count
#             )
#             selected_medium = random.sample(
#                 [q for q in medium_questions if q['id'] not in used_question_ids],
#                 medium_count
#             )
#             selected_easy = random.sample(
#                 [q for q in easy_questions if q['id'] not in used_question_ids],
#                 easy_count
#             )
            
#             candidate_set = selected_hard + selected_medium + selected_easy
#             candidate_ids = [q['id'] for q in candidate_set]
            
#             # Check for duplicates
#             if len(set(candidate_ids)) != len(candidate_ids):
#                 continue
                
#             # Check marks and time
#             sum_marks = sum(int(q['marks']) for q in candidate_set)
#             sum_time = sum(int(q['time_to_solve']) for q in candidate_set)
            
#             if sum_marks == int(total_marks) and sum_time == int(total_time):
#                 valid_sets.append(candidate_set)
#                 used_question_ids.update(candidate_ids)
#                 # Remove used questions from pre-filtered lists
#                 for q in selected_hard:
#                     hard_questions.remove(q)
#                 for q in selected_medium:
#                     medium_questions.remove(q)
#                 for q in selected_easy:
#                     easy_questions.remove(q)

#     return valid_sets

def increment_mock_exam_set_code(exam_schedule_id):

    exam_question_set_object = MockExamQuestionSet.objects.filter(exam_schedule_id=exam_schedule_id).order_by('-id').first()
    if exam_question_set_object is not None:
        value = exam_question_set_object.set_number
    else:
        value = ''
    
    value = value.upper()  # Ensure uppercase
    result = []
    carry = True  # Carry flag for incrementing

    for char in reversed(value):
        if carry:
            if char == 'Z':
                result.append('A')
            else:
                result.append(chr(ord(char) + 1))
                carry = False  # Stop incrementing if no carry needed
        else:
            result.append(char)

    if carry:
        result.append('A')  # Add a new letter if overflow (e.g., Z → AA)

    return ''.join(reversed(result))

def increment_exam_set_code(exam_id):
    
    exam_question_set_object = QuestionExamSet.objects.filter(exam_id =exam_id).order_by('-id').first()
    if exam_question_set_object is not None:
        value = exam_question_set_object.set_number
    else:
        value = ''
    
    value = value.upper()  # Ensure uppercase
    result = []
    carry = True  # Carry flag for incrementing

    for char in reversed(value):
        if carry:
            if char == 'Z':
                result.append('A')
            else:
                result.append(chr(ord(char) + 1))
                carry = False  # Stop incrementing if no carry needed
        else:
            result.append(char)

    if carry:
        result.append('A')  # Add a new letter if overflow (e.g., Z → AA)

    return ''.join(reversed(result))


class AddExamSet(GenericAPIView):
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

        data['name'] =  request_data.get('name')
        data['course'] =  request_data.get('course')
        data['time_to_solve'] =  request_data.get('time_to_solve')
        
        data['easy_questions_percentage'] =  request_data.get('easy_questions_percentage')
        data['medium_questions_percentage'] =  request_data.get('medium_questions_percentage')
        data['hard_questions_percentage'] =  request_data.get('hard_questions_percentage')
        
        data['question_type'] =  request_data.get('question_type')
        data['exam_mode'] =  request_data.get('exam_mode')
        data['total_marks'] =  request_data.get('total_marks')
        data['passing_marks'] =  request_data.get('passing_marks')
        data['description'] =  request_data.get('description')
        data['no_of_questions'] =  request_data.get('no_of_questions')
        data['no_of_sets'] =  request_data.get('no_of_sets')
        module_list = request_data.get('module_list')
        data['module_list'] = str(request_data.get('module_list'))

        # print("request.user.member_of",request.user.member_of)
        
        if request.user.member_of is not None and request.user.member_of != '' :
            college =str(request.user.member_of)
        else:
            college=str(request.user.id)

        data['college'] = college
        data['createdBy'] = str(request.user.id)
        
        check_exam_existence_object = ExamSet.objects.filter(isActive=True,name__iexact = data['name']).first()
        if check_exam_existence_object is not None:
            response_={
                "n": 0,
                "msg": 'Exam Set already existed',
                "data":[]                
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

        try:
            
            question_object = Question.objects.filter(isActive=True,course__icontains=data['course'],)
            question_ser = QuestionSerializer(question_object,many=True)            
            
            questions_list = question_ser.data
    
            # exam_sets = generate_question_sets(
            #     questions_list,
            #     module_list,
            #     data['total_marks'],
            #     data['time_to_solve'],
            #     data['no_of_sets'],
            #     data['no_of_questions']
            # )
            # In your API view:

            data['difficulty_level'] =  request_data.get('difficulty_level')
            l1=int(request_data.get('easy_questions_percentage', 0))
            l2=int(request_data.get('medium_questions_percentage', 0))
            l3=int(request_data.get('hard_questions_percentage', 0))

            data['easy_questions_percentage']=l1
            data['medium_questions_percentage']=l2
            data['hard_questions_percentage']=l3

            print("l1",l1,l2,l3)
            
            if l1 >= l2 and l1 >= l3:
                print("1")
                data['difficulty_level'] = 'Easy'
            elif l2 >= l1 and l2 >= l3:
                print("2")
                data['difficulty_level'] = 'Medium'
            elif l3 >= l1 and l3 >= l2:
                print("3")
                data['difficulty_level'] = 'Hard'
            else:
                # Default case if all are equal or other unexpected scenario
                print("Default")
                data['difficulty_level'] = 'Medium'  # or whatever default you prefer
            

            try:
                difficulty_dist = {
                    'easy': int(request_data.get('easy_questions_percentage', 0)),
                    'medium': int(request_data.get('medium_questions_percentage', 0)),
                    'hard': int(request_data.get('hard_questions_percentage', 0))
                }
                exam_sets = generate_unique_question_sets_by_difficulty_levels_percentage(
                    all_questions=question_ser.data,
                    course_id=data['course'],
                    target_time=data['time_to_solve'],
                    question_type=data['question_type'],
                    total_marks=data['total_marks'],
                    num_questions=data['no_of_questions'],
                    num_sets=data['no_of_sets'],
                    difficulty_distribution=difficulty_dist
                )
                # print("exam_sets",exam_sets)

                if not exam_sets:
                    print("Could not generate sets with current parameters")
                    raise ValueError("Could not generate sets with current parameters")
                    
            except ValueError as e:
                print("error",e)
                # return error_response(str(e))













            if exam_sets:
                
                exam_serializer = ExamSetSerializer(data=data)
                if exam_serializer.is_valid():
                    exam_serializer.save()
                    # "exam_sets",exam_sets)

                    
                    for i in exam_sets:
                        # question_list = []
                        # question_list.append()
                        # print("i",i)
                        question_list = [item['id'] for item in i]
                        set_series_number = increment_exam_set_code(exam_serializer.data['id'])
                        # print("set_series_number",set_series_number)
                        QuestionExamSet.objects.create(
                            exam_id = exam_serializer.data['id'],
                            question_id = question_list,
                            set_number = set_series_number
                        )
                    
        
                    response_={
                                "n": 1,
                                "msg": 'Exam Set created successfully',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    # print("error",exam_serializer.errors)
                    response_={
                                "n": 0,
                                "msg": 'Exam Set not created',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            
        except ValueError as e:
            response_={
                "n": 0,
                "msg": str(e),
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
                    "msg": 'No combinations found of the questions',
                    "data":[]                
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            



from math import isclose

def generate_unique_question_sets_by_difficulty_levels_percentage(
        all_questions,
        course_id,
        target_time,
        question_type,
        total_marks,
        num_questions,
        num_sets,
        difficulty_distribution

    ):

    try:
        target_time = float(target_time)
        num_questions = int(num_questions)
        total_marks = float(total_marks)
    except (ValueError, TypeError) as e:
        print(f"Error converting input values: {e}")
        return False

    # Convert course_id to string for comparison since questions store it as string
    course_id_str = str(course_id)
    
    # Validate difficulty distribution
    if sum(difficulty_distribution.values()) != 100:
        print("Difficulty percentages must sum to 100%")
        return False
    
    # Filter questions by all criteria except difficulty
    filtered_questions = [
        q for q in all_questions
        if (course_id_str in q.get('course', []) and  # Compare with string
           str(q.get('type_of_question')).lower() == str(question_type).lower() and
           q.get('is_archive', False) is False)
    ]
    

    # if not filtered_questions:
    #     print(f"No questions match the specified criteria (Course: {course_id}, Type: {question_type})")
    #     print(f"Available questions have course: {set(q.get('course') for q in all_questions)}")
    #     print(f"Available question types: {set(str(q.get('type_of_question')).lower() for q in all_questions)}")
    #     return False
    
    # Rest of your function remains the same...
    # Calculate time per question (average)


    avg_time_per_question = target_time / num_questions
    
    # Further filter by time tolerance (±20%)
    time_filtered = [
        q for q in all_questions
        if isclose(float(q.get('time_to_solve', 0)), 
                  avg_time_per_question, 
                  rel_tol=0.2)
    ]
    
    # Group by difficulty level
    difficulty_groups = defaultdict(list)
    for q in time_filtered:
        difficulty = q.get('difficulty_level', '').lower()
        if difficulty in difficulty_distribution:
            difficulty_groups[difficulty].append(q)
    
    # Calculate number of questions needed per difficulty level
    difficulty_counts = {
        level: int(num_questions * percentage / 100)
        for level, percentage in difficulty_distribution.items()
    }

    # print("difficulty_counts",difficulty_counts)
    # Verify we have enough questions of each type
    for level, count in difficulty_counts.items():
        # print("level count",level, count)

        available = len(difficulty_groups.get(level, []))
        # print("available",available)
        # print("int(count) * int(num_sets)",int(count) , int(num_sets))

        needed = int(count) * int(num_sets)
        # print("needed",needed)

        if int(available) < int(needed):
            print(
                f"Not enough {level} questions. Needed {needed}, available {available}"
            )
            return False
    
    # Generate sets ensuring uniqueness across sets
    question_sets = []
    used_question_ids = set()
    
    for _ in range(int(num_sets)):
        current_set = []
        current_marks = 0
        remaining_questions = num_questions
        
        # Build set maintaining difficulty distribution
        for level, count in difficulty_counts.items():
            candidates = [
                q for q in difficulty_groups[level]
                if q['id'] not in used_question_ids
            ]
            
            # Select questions that help reach target marks
            selected = []
            remaining = count
            
            while remaining > 0 and candidates:
                # Try to find questions that get us closest to target marks
                best_fit = None
                best_diff = float('inf')
                
                for q in candidates:
                    new_marks = current_marks + float(q.get('marks', 0))
                    new_diff = abs(total_marks - new_marks)
                    
                    if new_diff < best_diff:
                        best_diff = new_diff
                        best_fit = q
                
                if best_fit:
                    selected.append(best_fit)
                    current_marks += float(best_fit.get('marks', 0))
                    candidates.remove(best_fit)
                    remaining -= 1
                else:
                    break
            
            current_set.extend(selected)
            remaining_questions -= count
        
        # Verify set meets requirements
        if (len(current_set) == num_questions and
            isclose(current_marks, total_marks, rel_tol=0.1)):
            question_sets.append(current_set)
            used_question_ids.update(q['id'] for q in current_set)
    
    return question_sets




            
class ViewExamDetail(GenericAPIView):
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        exam_set_id = request_data.get('exam_set_id')
        
        if exam_set_id is None or exam_set_id == "":
            response_={
                "n": 0,
                "msg": 'Exam Id is required',
                "data":[]          
            }
    
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
            
        
        exam_set_object = ExamSet.objects.filter(id=exam_set_id,isActive=True).first()
        
        if exam_set_object is not None:
            exam_set_ser = ExamSetSerializer(exam_set_object)
            exam_set_ser_data = exam_set_ser.data
            
            question_set_object = QuestionExamSet.objects.filter(isActive=True,exam_id=exam_set_ser.data['id']).order_by('id')
            question_set_ser = QuestionExamSetSerializer(question_set_object,many=True)
            
            # for i in question_set_ser.data:
            #     question_object = Question.objects.filter(isActive=True,id__in = i['question_id']).order_by('id')
            #     question_ser = QuestionSerializer(question_object,many=True)
            #     for q in question_ser.data:
            #         question_all_image_object = QuestionImages.objects.filter(isActive=True,question_id=q['id']).order_by('id')
            #         question_all_image_ser = QuestionImagesSerializer(question_all_image_object,many=True)
                    
            #         question_option_object = QuestionOption.objects.filter(isActive=True,question_id=q['id'])
            #         question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
                    
            #         q['question_all_image_data'] = question_all_image_ser.data
            #         q['question_option_data'] = question_option_ser.data
                    
                
            #     i['question_data'] = question_ser.data
            
            
            exam_set_ser_data.update({
                "question_set_data": question_set_ser.data
            })            
            
            response_={
                        "n": 1,
                        "msg": 'Details fetched successfully',
                        "data":exam_set_ser_data  
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
                        "msg": 'Data not available',
                        "data":[]          
                    }
            
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class ViewExamQuestionSet(GenericAPIView):
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        exam_set_id = request_data.get('exam_set_id')
        
        if exam_set_id is None or exam_set_id == "":
            response_={
                        "n": 0,
                        "msg": 'Exam Id is required',
                        "data":[]          
                    }
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        exam_set_question_objects = QuestionExamSet.objects.filter(isActive=True,id=exam_set_id).first()
        if exam_set_question_objects is not None:
            question_set_ser = QuestionExamSetSerializer(exam_set_question_objects)
            
            question_set_ser_data = question_set_ser.data
            question_data = ""
            exam_detail_data = ""
            exam_detail_object = ExamSet.objects.filter(isActive=True,id=question_set_ser.data['exam_id']).first()
            if exam_detail_object is not None:
                exam_detail_ser = ExamSetSerializer(exam_detail_object)
                exam_detail_data = exam_detail_ser.data
                course_object = Course.objects.filter(isActive=True,id=exam_detail_ser.data['course']).first()
                if course_object is not None:
                    exam_detail_data.update({
                        'course_name':course_object.course_name,
                        'course_code':course_object.course_code
                    })
                else:
                    exam_detail_data.update({
                        'course_name':'',
                        'course_code':''
                    })
                    
                question_object = Question.objects.filter(isActive=True,id__in = question_set_ser.data['question_id']).order_by('id')
                question_ser = QuestionSerializer(question_object,many=True)
                for q in question_ser.data:
                    question_all_image_object = QuestionImages.objects.filter(isActive=True,question_id=q['id']).order_by('id')
                    question_all_image_ser = QuestionImagesSerializer(question_all_image_object,many=True)
                    
                    question_option_object = QuestionOption.objects.filter(isActive=True,question_id=q['id'])
                    question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
                    
                    q['question_all_image_data'] = question_all_image_ser.data
                    q['question_option_data'] = question_option_ser.data
                    
                
                question_data = question_ser.data
            else:
                question_data = ""
                exam_detail_data = ""
                
            
            question_set_ser_data.update({
                'exam_detail_data':exam_detail_data,
                'question_data':question_data
                
            })
            
            
            
            response_={
                        "n": 1,
                        "msg": 'Details fetched successfully',
                        "data":question_set_ser_data  
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
                        "msg": 'Data not available',
                        "data":[]          
                    }
            
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class ExamList(GenericAPIView):
    
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

        if request.user.member_of is not None and request.user.member_of != '' :
            college =str(request.user.member_of)
        else:
            college=str(request.user.id)

        exam_object = ExamSet.objects.filter(isActive=True,college=college).order_by('createdAt')
        examname=request_data.get('examname')
        if examname is not None and examname !='':
            exam_object=exam_object.filter(name__icontains=examname)
        
        difficulty_level=request_data.get('difficulty_level')
        if difficulty_level is not None and difficulty_level !='':
            exam_object=exam_object.filter(difficulty_level=difficulty_level)
        
        
        maxmarks=request_data.get('maxmarks')
        if maxmarks is not None and maxmarks !='':
            exam_object=exam_object.filter(total_marks__lte=maxmarks)
        course=request_data.get('course')
        if course is not None and course !='':
            exam_object=exam_object.filter(course=course)


        paginate_object = self.paginate_queryset(exam_object)
        serializer =  ExamSetSerializer(paginate_object,many=True)
        for i in serializer.data:
            course_object = Course.objects.filter(isActive=True,id = i['course']).first()
            if course_object is not None:
                i['course_name'] = course_object.course_name
                i['course_code'] = course_object.course_code
            else:
                i['course_name'] = ""
                i['course_code'] = ""
                
            question_set_object = QuestionExamSet.objects.filter(isActive=True,exam_id=i['id'])
            question_set_ser = QuestionExamSetSerializer(question_set_object,many=True)
            i['set_list'] = question_set_ser.data
            
        if encryped_header == "1" :
            paigna=self.get_paginated_response(serializer.data)
            data_to_serialize = convert_decimals_to_float(paigna)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            paigna=self.get_paginated_response(serializer.data)
            return Response(paigna,status=200)
        
class GetScheduleandSetonbasisofCourse(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        course_id = request_data.get('course_id')
        
        schedule_object = Schedule.objects.filter(isActive=True,course_ids__in=[course_id],college_ids__in=[str(request.user.id)])
        schedule_ser = ScheduleSerializer(schedule_object,many=True)
        
        exam_set_object = ExamSet.objects.filter(isActive=True,course=course_id,college=str(request.user.id))
        exam_set_ser = ExamSetSerializer(exam_set_object,many=True)
        response_={
                    "n": 1,
                    "msg": 'Data fetched successfully',
                    "schedule_data":schedule_ser.data,           
                    "exam_set_data":exam_set_ser.data           
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class AddScheduleExam(GenericAPIView):
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
        
        data['course'] =  request_data.get('course')
        data['schedule'] =  request_data.get('schedule')
        data['exam_set'] =  request_data.get('exam_set')
        data['exam_mode'] =  request_data.get('exam_mode')
        data['mandatory_questions'] = request_data.get('mandatory_questions')
        data['total_marks'] =  request_data.get('total_marks')
        data['passing_marks'] =  request_data.get('passing_marks')
        data['exam_duration'] =  request_data.get('exam_duration')
        data['schedule_exam_date'] = request_data.get('schedule_exam_date')
        data['start_time'] =  request_data.get('start_time')
        data['end_time'] =  request_data.get('end_time')   
        data['exam_note'] =  request_data.get('exam_note')   
        data['attempt'] =  request_data.get('attempt')
        data['candidates'] =  request_data.get('candidates')
        # print("data['candidates']",data['candidates'])
        if request.user.member_of is not None and request.user.member_of != '' :
            college =str(request.user.member_of)
        else:
            college=str(request.user.id)


        data['college'] =  college
        enrolled_students_objects_list = list(Enrollments.objects.filter(isActive=True,schedule=data['schedule'],candidate__in=data['candidates']).values_list('candidate',flat=True))
        exam_set_object_list = list(QuestionExamSet.objects.filter(isActive=True,exam_id = data['exam_set']).values_list('id',flat=True))
        
        if enrolled_students_objects_list == []:
            response_={
                        "n": 0,
                        "msg": 'No candidates for current batch',
                        "data":[]                
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        

        # already_scheduled_exam = ScheduleExam.objects.filter(isActive=True,exam_set=data['exam_set'],schedule=data['schedule'],college=college,course=data['course'],exam_mode=data['exam_mode'],attempt=data['attempt']).first()

        # if already_scheduled_exam is not None:
        #     response_={
        #                 "n": 0,
        #                 "msg": 'Exam already scheduled for this batch and attempt no',
        #                 "data":[]                
        #             }
        #     if encryped_header == "1" :
        #         data_to_serialize = convert_decimals_to_float(response_)
        #         encdata = encrypt_data(json.dumps(data_to_serialize))
        #         return Response(encdata,status=200)
        #     else:
        #         return Response(response_,status=200)
            
        current_date = datetime.now().date()
        previous_attempt = int(data['attempt']) - 1 if int(data['attempt']) > 1 else 0
        if previous_attempt > 0:
            previous_scheduled_exam = ScheduleExam.objects.filter(isActive=True,exam_set=data['exam_set'],schedule=data['schedule'],college=college,course=data['course'],attempt=previous_attempt).first()
            if previous_scheduled_exam is not None:
                previous_exam_date = previous_scheduled_exam.schedule_exam_date
                # if previous_exam_date > current_date:
                #     response_={
                #         "n": 0,
                #         "msg": 'Unable to schedule exam as previous attempt is not completed',
                #         "data":[]                
                #     }
                #     if encryped_header == "1" :
                #         data_to_serialize = convert_decimals_to_float(response_)
                #         encdata = encrypt_data(json.dumps(data_to_serialize))
                #         return Response(encdata,status=200)
                #     else:
                #         return Response(response_,status=200)


        # print("data['exam_set']",data['course'],data['schedule'],data['exam_set'],college,)
        # validate_attempt_no=ScheduleExam.objects.filter(isActive=True,exam_set=data['exam_set'],schedule=data['schedule'],college=college,course=data['course']).count()
        # if int(int(validate_attempt_no)+1) != int(data['attempt']):
        #     response_={
        #                 "n": 0,
        #                 "msg": 'Attempt no should be in sequence,this attempt must be '+str(int(validate_attempt_no)+1),
        #                 "data":[]                
        #             }
            
        #     if encryped_header == "1" :
        #         data_to_serialize = convert_decimals_to_float(response_)
        #         encdata = encrypt_data(json.dumps(data_to_serialize))
        #         return Response(encdata,status=200)
        #     else:
        #         return Response(response_,status=200)


        try:
            exam_serializer = ScheduleExamSerializer(data=data)
            if exam_serializer.is_valid():                
                question_object = Question.objects.filter(isActive=True,course__icontains=data['course'],
                                                        #   difficulty_level=data['difficulty_level']
                                                          )
                question_ser = QuestionSerializer(question_object,many=True)            
                questions_list = question_ser.data
                exam_obj=ExamSet.objects.filter(isActive=True,id=data['exam_set']).first()
                if exam_obj is not None:    
                    data['no_of_questions'] = exam_obj.no_of_questions
                    module_list = exam_obj.module_list
                    # print("module_list1",module_list)
                    if isinstance(module_list, str):
                        try:
                            # Replace single quotes with double quotes (if needed)
                            module_list = module_list.replace("'", '"')
                            module_list = json.loads(module_list)
                        except json.JSONDecodeError as e:
                            # print("Failed to parse module_list:", repr(module_list))
                            module_list = []

                    # print("module_list2",module_list)


                    mock_exam_sets = generate_unique_question_sets(
                        questions_list,
                        module_list,
                        data['total_marks'],
                        data['exam_duration'],
                        5,#no of sets
                        data['no_of_questions'],
                    )
                    print("mock_exam_sets",mock_exam_sets)
                    # generate_unique_question_sets_by_difficulty_levels_percentage(
                    #         all_questions,
                    #         course_id,
                    #         target_time,
                    #         question_type,
                    #         total_marks,
                    #         num_questions,
                    #         num_sets,
                    #         difficulty_distribution

                    #     )
                    exam_serializer.save()
                    seq_difficulty_level=['Easy','Medium','Medium','Hard','Hard','Easy','Medium','Medium','Hard','Hard']
                    set_counter=0
                    for i in mock_exam_sets:
                        print("i",i)
                        mock_difficulty_level=seq_difficulty_level[set_counter]
                        set_counter+=1
                        question_list = [item['id'] for item in i]
                        set_series_number = increment_mock_exam_set_code(exam_serializer.data['id'])
                        MockExamQuestionSet.objects.create(
                                question_id = question_list,
                                set_number = set_series_number,
                                difficulty_level= mock_difficulty_level,
                                course= exam_obj.course,
                                exam_schedule_id = exam_serializer.data['id'],
                                exam_id = data['exam_set'],
                                college= college,
                                no_of_questions= data['no_of_questions'],
                                exam_duration= data['exam_duration'],
                                mandatory_questions=data['mandatory_questions'],

                        )





                assignments = []
                for idx, candidate in enumerate(enrolled_students_objects_list):

                    assigned_set = exam_set_object_list[idx % len(exam_set_object_list)]
                    assignments.append({
                        'candidate': candidate,
                        'set': assigned_set
                    })
                
                for k in assignments:
                    ExamCandidateSetRelation.objects.create(
                        exam_schedule_id = exam_serializer.data['id'],
                        exam_id = data['exam_set'],
                        exam_set = k['set'],
                        candidate_id = k['candidate']
                    )
                    
                    exam_link_object = ExamCandidateSetRelation.objects.filter(isActive=True,exam_schedule_id=exam_serializer.data['id'],exam_id=data['exam_set'],exam_set=k['set'],candidate_id=k['candidate']).first()
                    if exam_link_object is not None:
                        exam_array = {
                            "exam_schedule_id" : exam_link_object.exam_schedule_id,
                            "exam_id" : exam_link_object.exam_id,
                            "exam_set" : exam_link_object.exam_set,
                            "candidate_id" : exam_link_object.candidate_id,
                            "candidate_exam_id":exam_link_object.id
                        }
                        base_data_to_serialize = convert_decimals_to_float(exam_array)
                        encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))

                        candidate_object = Candidate.objects.filter(isActive=True,id=exam_link_object.candidate_id).first()
                        if candidate_object is not None:
                            
                            # 'exam_link': collegeURL+'/exam/candidate-exam-instructions/'+encrypt_base_test_examination_link,

                            dicti = {
                                'email': candidate_object.email,
                                'exam_link': candidateURL+'/exam-portal-login',
                                'exam_name': exam_serializer.data['exam_set'],
                                'candidate_name': candidate_object.first_name + " " + candidate_object.last_name,
                                'exam_schedule_date': datefilterchangeformat(exam_serializer.data['schedule_exam_date']),
                                'start_time': exam_serializer.data['start_time'],
                                'end_time': exam_serializer.data['end_time'],
                                'exam_note': exam_serializer.data['exam_note'] ,
                                'exam_date_time': exam_serializer.data['schedule_exam_date'] + " " + exam_serializer.data['start_time'],
                                'note': exam_serializer.data['exam_note'],
                                'candidate_email': candidate_object.email,
                                'exam_duration': data['exam_duration'],
                            }
                            # print("dicti",dicti)

                            message = get_template(
                                'mails/exam-link-mail.html').render(dicti)
                            msg = EmailMessage(
                                'Exam Scheduled for ' + exam_serializer.data['schedule_exam_date'] + " " + exam_serializer.data['start_time'],
                                message,
                                EMAIL_HOST_USER,
                                [candidate_object.email],
                            )
                            msg.content_subtype = "html"  # Main content is now text/html
                            msg.send()











                        
                        
                        exam_link_object.exam_link = encrypt_base_test_examination_link
                        exam_link_object.save()
                
                response_={
                            "n": 1,
                            "msg": 'Exam Scheduled successfully',
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
                            "msg": 'Exam not scheduled',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class ScheduleExamList(GenericAPIView):
    
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

        if request.user.member_of is not None and request.user.member_of != '' :
            college =str(request.user.member_of)
        else:
            college=str(request.user.id)
        
        exam_object = ScheduleExam.objects.filter(isActive=True,college=college).order_by('createdAt')
        paginate_object = self.paginate_queryset(exam_object)
        serializer =  ScheduleExamSerializer(paginate_object,many=True)
        for i in serializer.data:
            course_object = Course.objects.filter(isActive=True,id = i['course']).first()
            if course_object is not None:
                i['course_name'] = course_object.course_name
                i['course_code'] = course_object.course_code
            else:
                i['course_name'] = ""
                i['course_code'] = ""
                
            schedule_object = Schedule.objects.filter(isActive=True,id=i['schedule']).first()
            if schedule_object is not None:
                i['schedule_name'] = schedule_object.schedulename
            else:
                i['schedule_name'] = ""
                
            exam_mode_object = TrainingMode.objects.filter(isActive=True,id=i['exam_mode']).first()
            if exam_mode_object is not None:
                i['exam_mode_name'] = exam_mode_object.training_mode
            else:
                i['exam_mode_name'] = ''
            if i['schedule_exam_date'] is not None and i['schedule_exam_date'] != "":
                i['schedule_exam_date'] =  datefilterchangeformat(i['schedule_exam_date'])

                 
            # question_set_object = QuestionExamSet.objects.filter(isActive=True,exam_id=i['id'])
            # question_set_ser = QuestionExamSetSerializer(question_set_object,many=True)
            # i['set_list'] = question_set_ser.data
            
        if encryped_header == "1" :
            paigna=self.get_paginated_response(serializer.data)
            data_to_serialize = convert_decimals_to_float(paigna)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            paigna=self.get_paginated_response(serializer.data)
            return Response(paigna,status=200)

class ViewCandidateExamQuestionSet(GenericAPIView):
    
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        exam_set_id = request_data.get('exam_set')
        exam_schedule_id = request_data.get('exam_schedule_id')
        exam_id = request_data.get('exam_id')
        candidate_id = request_data.get('candidate_id')
        candidate_exam_id = request_data.get('candidate_exam_id')
        final_submit = False
        final_submit_obj=ExamCandidateResult.objects.filter(isActive=True,id=candidate_exam_id,final_submit=True).first()
        if final_submit_obj is not None:
            final_submit=True



        
        if exam_set_id is None or exam_set_id == "":
            response_={
                        "n": 0,
                        "msg": 'Exam Id is required',
                        "data":[]          
                    }
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        exam_set_question_objects = QuestionExamSet.objects.filter(isActive=True,id=exam_set_id).first()
        if exam_set_question_objects is not None:
            question_set_ser = QuestionExamSetSerializer(exam_set_question_objects)
            
            #exam schedule
            exam_schedule_object = ScheduleExam.objects.filter(isActive=True,id=exam_schedule_id).first()
            exam_schedule_ser = ScheduleExamSerializer(exam_schedule_object)
            exam_schedule_ser_data = exam_schedule_ser.data
            
            if exam_schedule_ser.data['schedule_exam_date'] is not None and exam_schedule_ser.data['schedule_exam_date'] != "":
                schedule_exam_date_convert_date =  datefilterchangeformat(exam_schedule_ser.data['schedule_exam_date'])
            exam_schedule_ser_data.update({
                'schedule_exam_date_convert_date':schedule_exam_date_convert_date
            })
            #exam candidate relation
            exam_candidate_relation_object = ExamCandidateSetRelation.objects.filter(isActive=True,exam_schedule_id=exam_schedule_id,exam_id=exam_id,exam_set=exam_set_id,candidate_id=candidate_id).first()
            exam_candidate_relation_ser = ExamCandidateSetRelationSerializer(exam_candidate_relation_object)
            exam_candidate_relation_ser_data = exam_candidate_relation_ser.data
            
            #candidate data
            candidate_object = Candidate.objects.filter(isActive=True,id=candidate_id).first()
            candidate_ser = CandidateSerializer(candidate_object)
            candidate_ser_data = candidate_ser.data
            
            
            question_set_ser_data = question_set_ser.data
            question_data = ""
            exam_detail_data = ""
            exam_detail_object = ExamSet.objects.filter(isActive=True,id=question_set_ser.data['exam_id']).first()
            if exam_detail_object is not None:
                exam_detail_ser = ExamSetSerializer(exam_detail_object)
                exam_detail_data = exam_detail_ser.data
                course_object = Course.objects.filter(isActive=True,id=exam_detail_ser.data['course']).first()
                if course_object is not None:
                    exam_detail_data.update({
                        'course_name':course_object.course_name,
                        'course_code':course_object.course_code
                    })
                else:
                    exam_detail_data.update({
                        'course_name':'',
                        'course_code':''
                    })
                    
                question_object = Question.objects.filter(isActive=True,id__in = question_set_ser.data['question_id']).order_by('id')
                question_ser = QuestionSerializer(question_object,many=True)
                for q in question_ser.data:
                    exam_result_question_object = ExamCandidateResultAnswer.objects.filter(isActive=True,exam_candidate_result_id=candidate_exam_id,question_id =q['id']).first()
                
                    if exam_result_question_object is not None:
                        q['candidate_option_id'] = exam_result_question_object.candidate_option_id
                        q['candidate_option_answer'] = exam_result_question_object.candidate_option_answer
                        q['mark_for_review'] = exam_result_question_object.mark_for_review
                        question_answered_data = exam_result_question_object.question_data
                        try:
                            exam_result_question_ser_data = ast.literal_eval(question_answered_data)
                            if isinstance(exam_result_question_ser_data.get("tags"), str):
                                exam_result_question_ser_data["tags"] = json.loads(exam_result_question_ser_data["tags"])

                        except Exception as e:
                            exam_result_question_ser_data = {}
                    else:
                        q['candidate_option_id'] = None
                        q['candidate_option_answer'] = None
                        q['mark_for_review'] = None
                        exam_result_question_ser_data = {}
                    
                    q['correct_answer_data'] = exam_result_question_ser_data
                    question_all_image_object = QuestionImages.objects.filter(isActive=True,question_id=q['id']).order_by('id')
                    question_all_image_ser = QuestionImagesSerializer(question_all_image_object,many=True)
                    
                    question_option_object = QuestionOption.objects.filter(isActive=True,question_id=q['id'])
                    question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
                    
                    q['question_all_image_data'] = question_all_image_ser.data
                    q['question_option_data'] = question_option_ser.data
                    
                
                question_data = question_ser.data
            else:
                question_data = ""
                exam_detail_data = ""
            
            # data_to_serialize = convert_decimals_to_float(question_data)
            # encrypt_question_data = encrypt_data(json.dumps(data_to_serialize))
            question_set_ser_data.update({
                'exam_detail_data':exam_detail_data,
                'question_data':question_data,
                'exam_schedule_data':exam_schedule_ser_data,
                'exam_candidate_relation_data':exam_candidate_relation_ser_data,
                'candidate_data':candidate_ser_data,
                'final_submit':final_submit,
                # 'encrypt_question_data':encrypt_question_data
                
            })
            
            
            response_={
                        "n": 1,
                        "msg": 'Details fetched successfully',
                        "data":question_set_ser_data,
                        # "cvdata":text_data
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
                        "msg": 'Data not available',
                        "data":[]          
                    }
            
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class StartCandidateExam(GenericAPIView):

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        # print("request_data",request_data)
        # exam_schedule_id = exam_serializer.data['id'],
        # exam_id = data['exam_set'],
        # exam_set = k['set'],
        # candidate_id = k['candidate']
        data = {}
        data['exam_schedule_id'] =  request_data.get('exam_schedule_id')
        data['exam_id'] =  request_data.get('exam_id')
        data['exam_set'] =  request_data.get('exam_set')
        data['candidate_id'] =  request_data.get('candidate_id')
 
        data['start_created_time'] = timezone.now()

        already_exist_object = ExamCandidateResult.objects.filter(isActive=True,exam_schedule_id = data['exam_schedule_id'],exam_id = data['exam_id'],exam_set = data['exam_set'],candidate_id = data['candidate_id']).first()
        if already_exist_object is not None:
            exam_array = {
                "exam_schedule_id" : already_exist_object.exam_schedule_id,
                "exam_id" : already_exist_object.exam_id,
                "exam_set" : already_exist_object.exam_set,
                "candidate_id" : already_exist_object.candidate_id,
                "candidate_exam_id":already_exist_object.id
            }
            base_data_to_serialize = convert_decimals_to_float(exam_array)
            encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
            response_={
                        "n": 1,
                        "msg": 'Exam Scheduled successfully',
                        "data":[],
                        'exam_link':encrypt_base_test_examination_link             
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        
        try:
            
            exam_serializer = ExamCandidateResultSerializer(data=data)
            if exam_serializer.is_valid():                
                exam_serializer.save()
                
                exam_array = {
                    "exam_schedule_id" : exam_serializer.data['exam_schedule_id'],
                    "exam_id" : exam_serializer.data['exam_id'],
                    "exam_set" : exam_serializer.data['exam_set'],
                    "candidate_id" : exam_serializer.data['candidate_id'],
                    "candidate_exam_id":exam_serializer.data['id']
                }
                # exam_array = {
                #     "exam_schedule_id" : 1,
                #     "exam_id" : 3,
                #     "exam_set" : 15,
                #     "candidate_id" : 'a11049db-bb9d-48ad-86e3-5c989f6e39c3',
                #     "candidate_exam_id":exam_serializer.data['id']
                # }
                base_data_to_serialize = convert_decimals_to_float(exam_array)
                encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
                response_={
                            "n": 1,
                            "msg": 'Exam Scheduled successfully',
                            "data":[],
                            'exam_link':encrypt_base_test_examination_link             
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
                            "msg": 'Exam not scheduled',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class CaptureCandidateExamResult(GenericAPIView):

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        # exam_schedule_id = exam_serializer.data['id'],
        # exam_id = data['exam_set'],
        # exam_set = k['set'],
        # candidate_id = k['candidate']
        print("request_data",request_data )


        data = {}
        data['exam_candidate_result_id'] =  request_data.get('exam_candidate_result_id')
        data['question_data'] =  request_data.get('question_data')
        
        if request_data.get('candidate_option_answer') is not None and request_data.get('candidate_option_answer') != "":
            data['candidate_option_answer'] =  request_data.get('candidate_option_answer')
        else:
            data['candidate_option_answer'] =  None
        


        if request_data.get('candidate_option_id') is not None and request_data.get('candidate_option_id') != "":
            data['candidate_option_id'] = request_data.get('candidate_option_id')
        else:
            data['candidate_option_id'] =  None
            
        if request_data.get('markreview') == "1":
            data['mark_for_review'] = True
        else:
            data['mark_for_review'] = False 
        data['question_id'] =  request_data.get('question_id')
        
        if request_data.get('correct_answer_option') is not None and request_data.get('correct_answer_option') != "":
            data['correct_answer_option'] =  request_data.get('correct_answer_option')
      
        else:
            data['correct_answer_option'] =  None
        data['marks'] =  request_data.get('marks')
        schedule_id =  request_data.get('schedule_id')
        
        try:
            final_submit_obj = ExamCandidateResult.objects.filter(id=data['exam_candidate_result_id'],final_submit=True).first()
            if final_submit_obj is not None:
                response_={
                            "n": 0,
                            "msg": 'Exam already submitted,unable to submit answer',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)

            exam_time_out_obj=ScheduleExam.objects.filter(id=schedule_id).first()
            if exam_time_out_obj is not None:
                response_={
                            "n": 0,
                            "msg": 'Exam time out,unable to submit answer',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)




            answer_object = ExamCandidateResultAnswer.objects.filter(isActive=True,exam_candidate_result_id=data['exam_candidate_result_id'],question_id=data['question_id']).first()
            if answer_object is not None:
                exam_serializer = ExamCandidateResultAnswerSerializer(answer_object,data=data,partial=True)
                if exam_serializer.is_valid():                
                    exam_serializer.save()
                    
                    response_={
                                "n": 1,
                                "msg": 'Answer submitted',
                                "data":exam_serializer.data,           
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    # print("error",exam_serializer.errors)
                    response_={
                                "n": 0,
                                "msg": 'Data not captured',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:
                
                exam_serializer = ExamCandidateResultAnswerSerializer(data=data)
                if exam_serializer.is_valid():                
                    exam_serializer.save()
                    
                    response_={
                                "n": 1,
                                "msg": 'Data Captured successfully',
                                "data":[],           
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    # print("exam_serializer",exam_serializer.errors)
                    response_={
                                "n": 0,
                                "msg": 'Data not captured',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

            
class ViewScheduleList(GenericAPIView):
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
        
        id = request_data.get('id')
        
        exam_object = ScheduleExam.objects.filter(id=id,isActive=True).first()
        # paginate_object = self.paginate_queryset(exam_object)
        # serializer =  ScheduleExamSerializer(paginate_object)
        serializer =  ScheduleExamSerializer(exam_object)
        
        details = []
        
        for i in [serializer.data]:
            
            course_object = Course.objects.filter(isActive=True,id = i['course']).first()
            if course_object is not None:
                i['course_name'] = course_object.course_name
                i['course_code'] = course_object.course_code
            else:
                i['course_name'] = ""
                i['course_code'] = ""
                
            schedule_object = Schedule.objects.filter(isActive=True,id=i['schedule']).first()
            if schedule_object is not None:
                i['schedule_name'] = schedule_object.schedulename
            else:
                i['schedule_name'] = ""
                
            exam_mode_object = TrainingMode.objects.filter(isActive=True,id=i['exam_mode']).first()
            if exam_mode_object is not None:
                i['exam_mode_name'] = exam_mode_object.training_mode
            else:
                i['exam_mode_name'] = ''
            if i['schedule_exam_date'] is not None and i['schedule_exam_date'] != "":
                i['schedule_exam_date'] =  datefilterchangeformat(i['schedule_exam_date'])

                 
            # question_set_object = QuestionExamSet.objects.filter(isActive=True,exam_id=i['id'])
            # question_set_ser = QuestionExamSetSerializer(question_set_object,many=True)
            # i['set_list'] = question_set_ser.data
            details.append(i)
        response_={
            "n": 1,
            "msg": 'Data save',
            "data":details[0]          
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
        
class DeleteExamSet(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        id = request_data.get('id')
        if id is not None and id !="":
            dobj=ExamSet.objects.filter(id=id,isActive=True).first()
            if dobj is not None:
                dobj.isActive = False
                # dobj.deleted_by = str(request.user.id)
                dobj.save()
                response_={
                    "n": 1,
                    'msg':'Exam set Deleted Successfully.',
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
                    'msg':'Exam set id not found.',
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
            


class DeleteScheduleExamSet(GenericAPIView):
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        id = request_data.get('id')
        if id is not None and id !="":
            dsobj=ScheduleExam.objects.filter(id=id,isActive=True).first()
            if dsobj is not None:
                dsobj.isActive = False
                # dsobj.deleted_by = str(request.user.id)
                dsobj.save()
                # print("dsobj",dsobj)
                response_={
                    "n": 1,
                    'msg':'Schedule exam set Deleted Successfully.',
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
                    'msg':'Schedule exam set id not found.',
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




class GetCandidatesResults(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)     
    pagination_class=CustomPagination
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}


        candidate_ids=[]
        # print("request.user.user_type",request.user.user_type)
        cand_obj=Candidate.objects.filter(candidate_status='3',isActive=True).order_by('-createdAt')
        if request.user.user_type == 2:
            candidate_ids=list(cand_obj.values_list('id',flat=True))
        else:
            if request.user.member_of != '' and request.user.member_of is not None :
                tc_id=str(request.user.member_of)
            else:
                tc_id=str(request.user.id)

            candidate_ids=list(cand_obj.filter(
                Q(walkin_by=str(tc_id))|Q(id__in=list(Enrollments.objects.filter(college_id=tc_id,isActive=True,enrollments_status='2').values_list('candidate',flat=True)))).order_by('id').distinct('id').values_list('id',flat=True))



        # print("candidate_ids",candidate_ids)



        examschedilelist = ExamCandidateResult.objects.filter(candidate_id__in=candidate_ids,isActive=True).order_by('candidate_id','exam_id').distinct('candidate_id','exam_id')
        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            examschedilelist=examschedilelist.filter(createdAt__gte=start_date)

        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            examschedilelist=examschedilelist.filter(createdAt__lte=cend_date)

        if examschedilelist.exists():
            paginate_object = self.paginate_queryset(examschedilelist)

            exam_serializer=ExamCandidateResultSerializer(paginate_object,many=True)
            for result in exam_serializer.data:
                try:
                    exam_result_question_ser_data = ast.literal_eval(result['all_data'])
                    if exam_result_question_ser_data['exam_schedule_data']['schedule_exam_date'] is not None and exam_result_question_ser_data['exam_schedule_data']['schedule_exam_date'] != "":
                        change_date_format = datefilterchangeformat(exam_result_question_ser_data['exam_schedule_data']['schedule_exam_date'])
                        
                        
                except Exception as e:
                    exam_result_question_ser_data = {}
                result['exam_data']=exam_result_question_ser_data['exam_detail_data']
                result['candidate_data']=exam_result_question_ser_data['candidate_data']
                result['exam_schedule_data']=exam_result_question_ser_data['exam_schedule_data']
                
                if result['is_passed']:
                    result['status']='Passed'
                else:
                    result['status']='Failed'




            if encryped_header == "1" :
                paigna=self.get_paginated_response(exam_serializer.data)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                paigna=self.get_paginated_response(exam_serializer.data)
                return Response(paigna,status=200)
    
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


class GetCandidatesResultsCounts(GenericAPIView):
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


        candidate_ids=[]
        cand_obj=Candidate.objects.filter(candidate_status='3',isActive=True).order_by('-createdAt')
        if request.user.user_type == 2:
            candidate_ids=list(cand_obj.values_list('id',flat=True))
        else:
            if request.user.member_of != '' and request.user.member_of is not None :
                tc_id=str(request.user.member_of)
            else:
                tc_id=str(request.user.id)
            
            candidate_ids=list(cand_obj.filter(Q(walkin_by=str(tc_id))|Q(id__in=list(Enrollments.objects.filter(college_id=tc_id,isActive=True,enrollments_status='2').values_list('candidate',flat=True)))).order_by('id').distinct('id').values_list('id',flat=True))



        
        query_obj = ExamCandidateResult.objects.filter(candidate_id__in=candidate_ids,isActive=True).order_by('candidate_id').distinct('candidate_id')
        start_date=request_data.get('startdate')
        if start_date is not None and start_date !='':
            query_obj=query_obj.filter(createdAt__gte=start_date)

        end_date=request_data.get('enddate')
        if end_date is not None and end_date !='':
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = end_date_obj + timedelta(days=1)
            cend_date =str(new_end_date.strftime("%Y-%m-%d"))
            query_obj=query_obj.filter(createdAt__lte=cend_date)


        total_candidates= query_obj.filter(candidate_id__in=candidate_ids,isActive=True).order_by('candidate_id').distinct('candidate_id').count()
        passed_candidates= query_obj.filter(candidate_id__in=candidate_ids,isActive=True,is_passed=True).order_by('candidate_id').distinct('candidate_id').count()
        failed_candidates= query_obj.filter(candidate_id__in=candidate_ids,isActive=True,is_passed=False).order_by('candidate_id').distinct('candidate_id').count()
        Context={
            'total_candidates':total_candidates,
            'pass_candidates':passed_candidates,
            'failed_candidates':failed_candidates,
        }

        response_={
                        "n": 1,
                        "msg": 'count found ',
                        "data":Context               
                    }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)





class SubmitCandidateExam(GenericAPIView):

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        # exam_schedule_id = exam_serializer.data['id'],
        # exam_id = data['exam_set'],
        # exam_set = k['set'],
        # candidate_id = k['candidate']
        # print("request_data",)
        data = {}
        data['candidate_exam_id'] =  request_data.get('candidate_exam_id')
        data['all_data'] = str(request_data.get('all_data'))
        data['end_created_time'] = timezone.now()  
        data['final_submit']=True
        data['exam_schedule_id'] = request_data['all_data']['exam_candidate_relation_data']['exam_schedule_id']
    
        try:
            exam_object = ExamCandidateResult.objects.filter(id=data['candidate_exam_id'],exam_schedule_id=data['exam_schedule_id']).first()
            if exam_object is None:
                response_={
                            "n": 0,
                            "msg": 'Exam not found',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                

            if exam_object.final_submit == True:
                response_={
                            "n": 0,
                            "msg": 'Exam already submitted',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                



            exam_serializer = ExamCandidateResultSerializer(exam_object,data=data,partial=True)
            if exam_serializer.is_valid():                
                exam_serializer.save()
                
                generate_pdf_task = threading.Thread(target=save_result_async, args=(str(exam_serializer.data['id']), exam_serializer.data))
                generate_pdf_task.start()

                generate_pdf_task = threading.Thread(target=check_generate_certificate_pdf_async, args=(str(exam_serializer.data['id']), exam_serializer.data))
                generate_pdf_task.start()
            
                response_={
                            "n": 1,
                            "msg": 'Exam Submitted successfully',
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
                            "msg": 'Exam not submitted',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        
        
def save_result_async(id,data):
    
    exam_result_object = ExamCandidateResult.objects.filter(isActive=True,id=id).first()
    exam_total_marks = 0
    exam_passing_marks = 0
    try:
        exam_result_question_ser_data = ast.literal_eval(data['all_data'])
        exam_total_marks = exam_result_question_ser_data['exam_detail_data']['total_marks']
        exam_passing_marks = exam_result_question_ser_data['exam_detail_data']['passing_marks']
        # if isinstance(exam_result_question_ser_data.get("tags"), str):
        #     exam_result_question_ser_data["tags"] = json.loads(exam_result_question_ser_data["tags"])

    except Exception as e:
        exam_result_question_ser_data = {}
        exam_total_marks = 0
        exam_passing_marks = 0
    exam_result_answer_object = ExamCandidateResultAnswer.objects.filter(isActive=True,exam_candidate_result_id=data['id'])
    total_marks_obtained = 0
    for i in exam_result_answer_object:
        if i.candidate_option_id is not None and i.candidate_option_id != "":
            if i.candidate_option_id == i.correct_answer_option:
                total_marks_obtained += i.marks
        
    exam_result_object.marks_obtained = total_marks_obtained
    if total_marks_obtained >= exam_passing_marks:
        exam_result_object.is_passed = True
    else:
        exam_result_object.is_passed = False
    exam_result_object.save()
    return True

        
def save_mock_result_async(id,data):
    
    exam_result_object = MockExamCandidateResult.objects.filter(isActive=True,id=id).first()
    exam_total_marks = 0
    exam_passing_marks = 0
    try:
        exam_result_question_ser_data = ast.literal_eval(data['all_data'])
        exam_total_marks = exam_result_question_ser_data['exam_detail_data']['total_marks']
        exam_passing_marks = exam_result_question_ser_data['exam_detail_data']['passing_marks']
        # if isinstance(exam_result_question_ser_data.get("tags"), str):
        #     exam_result_question_ser_data["tags"] = json.loads(exam_result_question_ser_data["tags"])

    except Exception as e:
        exam_result_question_ser_data = {}
        exam_total_marks = 0
        exam_passing_marks = 0
    exam_result_answer_object = MockExamCandidateResultAnswer.objects.filter(isActive=True,mock_exam_candidate_result_id=data['id'])
    total_marks_obtained = 0
    for i in exam_result_answer_object:
        if i.candidate_option_id is not None and i.candidate_option_id != "":
            if i.candidate_option_id == i.correct_answer_option:
                total_marks_obtained += i.marks
        
    exam_result_object.marks_obtained = total_marks_obtained
    if total_marks_obtained >= exam_passing_marks:
        exam_result_object.is_passed = True
    else:
        exam_result_object.is_passed = False
    exam_result_object.save()
    return True


base_today_date = 'media/Candidate/Certificates' 
base_dynamic_folder = os.path.join(BASE_DIR, str(base_today_date))

def check_generate_certificate_pdf_async(id, data):
    
    change_date_format = ""
    try:
        exam_result_question_ser_data = ast.literal_eval(data['all_data'])
        if exam_result_question_ser_data['exam_schedule_data']['schedule_exam_date'] is not None and exam_result_question_ser_data['exam_schedule_data']['schedule_exam_date'] != "":
            change_date_format = datefilterchangeformat(exam_result_question_ser_data['exam_schedule_data']['schedule_exam_date'])
            
            
    except Exception as e:
        exam_result_question_ser_data = {}
    
    exam_result_object = ExamCandidateResult.objects.filter(isActive=True,id=id).first()
    if exam_result_object.is_passed == True:
    
        if not os.path.exists(base_dynamic_folder):
            os.makedirs(base_dynamic_folder)
        output_filename = str(id) + '.pdf'
        output_path = os.path.join(base_dynamic_folder, output_filename)
       
        exam_result_question_ser_data.update({
            'change_date_format':change_date_format
        })
        
        text_content = {
            'data': exam_result_question_ser_data
        }
        
        options = {'page-size': 'A4'}
        
        template = pdf_conv_template
        context = Context({"data": text_content})
        html = template.render(text_content)
        pdfkit.from_string(html, output_path, options=options)
        # print("output_path",output_path)
        return_output = hostURL +"/media" + output_path.split("media")[1]

        exam_result_object.certificate_link = return_output
        exam_result_object.save()
        return output_path

class AddTemplate(GenericAPIView):
    
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
        data['tc_logo'] = request.FILES.get('tc_logo')
        data['auth_sign'] = request.FILES.get('auth_sign')
        data['template_name'] = request_data.get('template_name')
        data['tc_id'] = request_data.get('tc_id')
        data['tc_name'] = request_data.get('tc_name')
        data['email'] = request_data.get('email')
        data['mobilenumber'] = request_data.get('mobilenumber')
        # 
        data['city'] = request_data.get('city')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['pincode'] = request_data.get('pincode')
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        # 
        data['auth_person_name'] = request_data.get('auth_person_name')
        data['auth_sign'] = request_data.get('auth_sign')

    
        data['createdBy']=str(request.user.id)

        if request.FILES.get('tc_logo') is not None and request.FILES.get('tc_logo') !='':
            fileInput=request.FILES.get('tc_logo')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Certificate Templates')
            file_url=save_file(folder_path,fileInput,request)
            data['tc_logo'] = file_url
        else:
            data['tc_logo'] = ''
            
        if request.FILES.get('auth_sign') is not None and request.FILES.get('auth_sign') !='':
            fileInput=request.FILES.get('auth_sign')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Certificate Templates')
            file_url=save_file(folder_path,fileInput,request)
            data['auth_sign'] = file_url
        else:
            data['auth_sign'] = ''

        data['createdBy'] = str(request.user.id)
        
        already_exist = CertificateTemplateMaster.objects.filter(isActive=True,tc_id = data['tc_id']).first()
        if already_exist is not None:
            response_={
                "n": 0,
                "msg": 'Template already exist for this college',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        serializer = CertificateTemplateMasterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # if any(not value for value in form.cleaned_data.values()):
            #     candidate.status = Candidate.PENDING
            # else:
            #     candidate.status = Candidate.SUBMITTED

            response_={
                "n": 1,
                "msg": 'Template added successfully',
                "data":serializer.data                        
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            # print("error",serializer.errors)
            response_={
                "n": 0,
                "msg": 'Template not added',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class UpdateTemplate(GenericAPIView):
    
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
        template_id = request_data.get('template_id')
        data['tc_logo'] = request.FILES.get('tc_logo')
        data['auth_sign'] = request.FILES.get('auth_sign')
        data['template_name'] = request_data.get('template_name')
        data['tc_id'] = request_data.get('tc_id')
        data['tc_name'] = request_data.get('tc_name')
        data['email'] = request_data.get('email')
        data['mobilenumber'] = request_data.get('mobilenumber')
        # 
        data['city'] = request_data.get('city')
        data['country'] = request_data.get('country')
        data['state'] = request_data.get('state')
        data['pincode'] = request_data.get('pincode')
        data['address_line_one'] = request_data.get('address_line_one')
        data['address_line_two'] = request_data.get('address_line_two')
        # 
        data['auth_person_name'] = request_data.get('auth_person_name')
        data['auth_sign'] = request_data.get('auth_sign')

    
        data['createdBy']=str(request.user.id)

        if request.FILES.get('tc_logo') is not None and request.FILES.get('tc_logo') !='':
            fileInput=request.FILES.get('tc_logo')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Certificate Templates')
            file_url=save_file(folder_path,fileInput,request)
            data['tc_logo'] = file_url
        else:
            data['tc_logo'] = ''
            
        if request.FILES.get('auth_sign') is not None and request.FILES.get('auth_sign') !='':
            fileInput=request.FILES.get('auth_sign')
            folder_path = os.path.join(settings.MEDIA_ROOT,'media','Certificate Templates')
            file_url=save_file(folder_path,fileInput,request)
            data['auth_sign'] = file_url
        else:
            data['auth_sign'] = ''
            
        data['updatedBy'] = str(request.user.id)
        data['updatedAt'] = timezone.now()

        tem_object = CertificateTemplateMaster.objects.filter(isActive=True,id=template_id).first()
        
        already_exist_training = CertificateTemplateMaster.objects.filter(isActive=True,tc_id = data['tc_id']).exclude(tc_id = tem_object.tc_id).first()
        if already_exist_training is not None:
            response_={
                "n": 0,
                "msg": 'Template already exist for this College',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        serializer = CertificateTemplateMasterSerializer(tem_object,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            # if any(not value for value in form.cleaned_data.values()):
            #     candidate.status = Candidate.PENDING
            # else:
            #     candidate.status = Candidate.SUBMITTED

            response_={
                "n": 1,
                "msg": 'Template updated successfully',
                "data":serializer.data                        
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
        else:
            # print("error",serializer.errors)
            response_={
                "n": 0,
                "msg": 'Template not updated',
                "data":[]                     
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
class TemplateList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        
        template_object = CertificateTemplateMaster.objects.filter(isActive=True).order_by('-id')
        template_ser = CertificateTemplateMasterSerializer(template_object,many=True)
        
        for i in template_ser.data:
            if i['createdAt'] is not None and i['createdAt'] != "":
                i['createdAt'] = convertdatewithtime(i['createdAt'])
            if i['updatedAt'] is not None and i['updatedAt'] != "":
                i['updatedAt'] = convertdatewithtime(i['updatedAt'])
                
        
        response_={
            "n": 1,
            "msg": 'Templates fetched successfully',
            "data":template_ser.data                        
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        
    def get(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        template_id = request.GET.get('template_id')
        if template_id is None or template_id == "":
            response_={
                "n": 0,
                "msg": 'Templates id not found',
                "data":[]                       
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        
        template_object = CertificateTemplateMaster.objects.filter(isActive=True,id=template_id).first()
        if template_object is not None:
            template_ser = CertificateTemplateMasterSerializer(template_object)

                    
            
            response_={
                "n": 1,
                "msg": 'Templates fetched successfully',
                "data":template_ser.data                        
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
                "msg": 'Templates not found',
                "data":[]           
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
            
class DeleteTemplate(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        template_id = request.GET.get('template_id')
        if template_id is None or template_id == "":
            response_={
                "n": 0,
                "msg": 'Templates id not found',
                "data":[]                       
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        
        template_object = CertificateTemplateMaster.objects.filter(isActive=True,id=template_id).first()
        if template_object is not None:
            template_object.isActive = False
            template_object.save()
            

                    
            
            response_={
                "n": 1,
                "msg": 'Templates deleted successfully',
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
                "msg": 'Templates not deleted',
                "data":[]                  
            }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class ViewAllCertificate(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        
        cerificate_exam_object = ExamCandidateResult.objects.filter(isActive=True,is_passed=True).order_by('-id')
        cerificate_exam_ser = ExamCandidateResultSerializer(cerificate_exam_object,many=True)
        
        for i in cerificate_exam_ser.data:
            if i['createdAt'] is not None and i['createdAt'] != "":
                i['createdAt'] = convertdatewithtime(i['createdAt'])
            if i['updatedAt'] is not None and i['updatedAt'] != "":
                i['updatedAt'] = convertdatewithtime(i['updatedAt'])
                
            try:
                i['exam_result_question_ser_data'] = ast.literal_eval(i['all_data'])
                i['exam_name'] = i['exam_result_question_ser_data']['exam_detail_data']['name']
                i['exam_total_marks'] = i['exam_result_question_ser_data']['exam_detail_data']['total_marks']
                i['exam_passing_marks'] = i['exam_result_question_ser_data']['exam_detail_data']['passing_marks']
                i['schedule_exam_date_convert_date'] = i['exam_result_question_ser_data']['exam_schedule_data']['schedule_exam_date_convert_date']
                college_id = i['exam_result_question_ser_data']['exam_schedule_data']['college']
                user_object = UserAdmin.objects.filter(id = college_id).first()
                if user_object is not None:
                    i['college_name'] = user_object.name
                else:
                    i['college_name'] = ""
                # if isinstance(exam_result_question_ser_data.get("tags"), str):
                #     exam_result_question_ser_data["tags"] = json.loads(exam_result_question_ser_data["tags"])

            except Exception as e:
                i['exam_result_question_ser_data'] = {}
                i['college_name'] = ""
                
        
        response_={
            "n": 1,
            "msg": 'Certificates fetched successfully',
            "data":cerificate_exam_ser.data                        
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class CandidateResultList(GenericAPIView):
    
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        # request_data, error_response = handle_request_body(request)
        # if error_response:
        #     return error_response
        
        cerificate_exam_object = ExamCandidateResult.objects.filter(isActive=True).order_by('-id')
        cerificate_exam_ser = ExamCandidateResultSerializer(cerificate_exam_object,many=True)
        
        for i in cerificate_exam_ser.data:
            if i['createdAt'] is not None and i['createdAt'] != "":
                i['createdAt'] = convertdatewithtime(i['createdAt'])
            if i['updatedAt'] is not None and i['updatedAt'] != "":
                i['updatedAt'] = convertdatewithtime(i['updatedAt'])
            try:
                i['exam_result_question_ser_data'] = ast.literal_eval(i['all_data'])
                i['exam_name'] = i['exam_result_question_ser_data']['exam_detail_data']['name']
                i['exam_total_marks'] = i['exam_result_question_ser_data']['exam_detail_data']['total_marks']
                i['exam_passing_marks'] = i['exam_result_question_ser_data']['exam_detail_data']['passing_marks']
                i['schedule_exam_date_convert_date'] = i['exam_result_question_ser_data']['exam_schedule_data']['schedule_exam_date_convert_date']
                college_id = i['exam_result_question_ser_data']['exam_schedule_data']['college']
                user_object = UserAdmin.objects.filter(id = college_id).first()
                if user_object is not None:
                    i['college_name'] = user_object.name
                else:
                    i['college_name'] = ""
                # if isinstance(exam_result_question_ser_data.get("tags"), str):
                #     exam_result_question_ser_data["tags"] = json.loads(exam_result_question_ser_data["tags"])

            except Exception as e:
                i['exam_result_question_ser_data'] = {}
                i['college_name'] = ""
                
        response_={
            "n": 1,
            "msg": 'Certificates fetched successfully',
            "data":cerificate_exam_ser.data                        
        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
        

class GetCandidatesMockTests(GenericAPIView):
    # authentication_classes=[CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)     
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}




        candidate_id = request_data.get('candidate_id')
        today_date = timezone.now().date()
        active_exam_schedule_ids=list(ScheduleExam.objects.filter(isActive=True,schedule_exam_date__gte=today_date).values_list('id',flat=True))
        candidate_exam_schedule_ids = list(ExamCandidateSetRelation.objects.filter(isActive=True,candidate_id=candidate_id,exam_schedule_id__in=active_exam_schedule_ids).order_by('exam_schedule_id').distinct('exam_schedule_id').values_list('exam_schedule_id',flat=True))

        mock_test_obj=MockExamQuestionSet.objects.filter(isActive=True,exam_schedule_id__in=candidate_exam_schedule_ids).order_by('exam_schedule_id','set_number')
        yesterday_date = today_date - timedelta(days=1)
        if mock_test_obj.exists():
            mock_test_ser = MockExamQuestionSetSerializer(mock_test_obj,many=True)
            for test in mock_test_ser.data:
                if yesterday_date < datetime.strptime((test['createdAt']).split("T")[0], "%Y-%m-%d").date():
                    test['is_new'] = True   
                else:
                    test['is_new'] = False

                if test['createdAt'] is not None and test['createdAt'] != "":
                    test['createdAt'] = convertdatewithtime(test['createdAt'])
                if test['updatedAt'] is not None and test['updatedAt'] != "":
                    test['updatedAt'] = convertdatewithtime(test['updatedAt'])

                course_obj=Course.objects.filter(isActive=True,id=test['course']).first()

                if course_obj is not None:
                    test['course_name'] = course_obj.course_name
                else:
                    test['course_name'] = ""


                course_module_names=list(CourseModules.objects.filter(isActive=True,course_id=test['course']).values_list("module_name",flat=True))
                if len(course_module_names) > 0:
                    test['course_modules'] = course_module_names
                else:
                    test['course_modules'] = []


                test['number_of_questions']= len(test['question_id'])
                test['duration'] = str(test['exam_duration']) 
                test['name'] ="Mock Test - " + str(test['set_number'])  

                check_result = MockExamCandidateResult.objects.filter(isActive=True,mock_exam_set=test['id'],candidate_id=candidate_id).first()
                if check_result is not None:
                    test['is_attempted'] = True
                    test['marks_obtained'] = check_result.marks_obtained
                    test['is_passed'] = check_result.is_passed
                    if check_result.final_submit == True:
                        test['status'] = 'completed'
                    else:
                        test['status'] = 'in_progress'
                else:
                    test['is_attempted'] = False
                    test['marks_obtained'] = 0
                    test['is_passed'] = False
                    test['status'] = 'not_started'

                test['encrypted_candidate_id'] = encrypt_data(str(candidate_id))
                test['encrypted_mock_exam_set_id'] = encrypt_data(str(test['id']))

            response_={
                            "n": 1,
                            "msg": 'Mock tests found',
                            "data":mock_test_ser.data               
                        }
        else:
            response_={
                            "n": 1,
                            "msg": 'No mock tests found',
                            "data": []
                        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)

class GetCandidatesMockTestsHistory(GenericAPIView):
    # authentication_classes=[CandidateJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)     
    
    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        data = {}




        candidate_id = request_data.get('candidate_id')
        today_date = timezone.now().date()

        candidate_attempted_mock_test_ids=list(MockExamCandidateResult.objects.filter(candidate_id=candidate_id).order_by('mock_exam_set').distinct('mock_exam_set').values_list('mock_exam_set',flat=True))


        mock_test_obj=MockExamQuestionSet.objects.filter(isActive=True,id__in=candidate_attempted_mock_test_ids).order_by('-exam_schedule_id','set_number')
        yesterday_date = today_date - timedelta(days=1)
        if mock_test_obj.exists():
            mock_test_ser = MockExamQuestionSetSerializer(mock_test_obj,many=True)
            for test in mock_test_ser.data:
                if yesterday_date < datetime.strptime((test['createdAt']).split("T")[0], "%Y-%m-%d").date():
                    test['is_new'] = False   
                else:
                    test['is_new'] = False

                if test['createdAt'] is not None and test['createdAt'] != "":
                    test['createdAt'] = convertdatewithtime(test['createdAt'])
                if test['updatedAt'] is not None and test['updatedAt'] != "":
                    test['updatedAt'] = convertdatewithtime(test['updatedAt'])

                course_obj=Course.objects.filter(isActive=True,id=test['course']).first()

                if course_obj is not None:
                    test['course_name'] = course_obj.course_name
                else:
                    test['course_name'] = ""


                course_module_names=list(CourseModules.objects.filter(isActive=True,course_id=test['course']).values_list("module_name",flat=True))
                if len(course_module_names) > 0:
                    test['course_modules'] = course_module_names
                else:
                    test['course_modules'] = []


                test['number_of_questions']= len(test['question_id'])
                test['duration'] = str(test['exam_duration']) 
                test['name'] ="Mock Test - " + str(test['set_number'])  

                check_result = MockExamCandidateResult.objects.filter(isActive=True,mock_exam_set=test['id'],candidate_id=candidate_id).first()
                if check_result is not None:
                    test['is_attempted'] = True
                    test['marks_obtained'] = check_result.marks_obtained
                    test['is_passed'] = check_result.is_passed
                    if check_result.final_submit == True:
                        test['status'] = 'completed'
                    else:
                        test['status'] = 'in_progress'
                else:
                    test['is_attempted'] = False
                    test['marks_obtained'] = 0
                    test['is_passed'] = False
                    test['status'] = 'not_started'

                test['encrypted_candidate_id'] = encrypt_data(str(candidate_id))
                test['encrypted_mock_exam_set_id'] = encrypt_data(str(test['id']))

            response_={
                            "n": 1,
                            "msg": 'Mock tests found',
                            "data":mock_test_ser.data               
                        }
        else:
            response_={
                            "n": 1,
                            "msg": 'No mock tests found',
                            "data": []
                        }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)


class StartMockCandidateExam(GenericAPIView):
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

        data['mock_exam_set'] =  request_data.get('mock_exam_set_id')
        data['candidate_id'] =  str(request.user.id)
        data['start_created_time'] = timezone.now()

        mock_question_set_object = MockExamQuestionSet.objects.filter(isActive=True,id=data['mock_exam_set']).first()
        if mock_question_set_object is None:
            response_={
                            "n": 0,
                            "msg": 'Mock exam set not found',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        data['exam_schedule_id'] =  mock_question_set_object.exam_schedule_id if mock_question_set_object else ''

        if data['exam_schedule_id'] is None or data['exam_schedule_id'] == "":
            response_={
                            "n": 0,
                            "msg": 'Exam schedule not found for this mock exam set',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        schedule_exam_object = ScheduleExam.objects.filter(isActive=True,id=data['exam_schedule_id']).first() 
        if schedule_exam_object is None:
            response_={
                            "n": 0,
                            "msg": 'Exam schedule not found',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


        data['exam_id'] =  schedule_exam_object.exam_set if schedule_exam_object else ''




        already_exist_object = MockExamCandidateResult.objects.filter(isActive=True,mock_exam_set = data['mock_exam_set'],candidate_id = data['candidate_id']).first()
        if already_exist_object is not None:
            exam_array = {
                "exam_schedule_id" : already_exist_object.exam_schedule_id,
                "mock_exam_set" : already_exist_object.mock_exam_set,
                "candidate_id" : data['candidate_id'],
                "exam_id" : already_exist_object.exam_id,
                "candidate_exam_id":already_exist_object.id
            }
            base_data_to_serialize = convert_decimals_to_float(exam_array)
            encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
            response_={
                        "n": 1,
                        "msg": 'Exam resumed successfully',
                        "data":[],
                        'exam_link':encrypt_base_test_examination_link             
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        
        try:
            
            exam_serializer = MockExamCandidateResultSerializer(data=data)
            if exam_serializer.is_valid():                
                exam_serializer.save()
                
                exam_array = {
                    "exam_schedule_id": exam_serializer.data['exam_schedule_id'],
                    "exam_id": exam_serializer.data['exam_id'],
                    "mock_exam_set": exam_serializer.data['mock_exam_set'],
                    "candidate_id": exam_serializer.data['candidate_id'],
                    "candidate_exam_id": exam_serializer.data['id']
                }
 
                base_data_to_serialize = convert_decimals_to_float(exam_array)
                encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
                response_={
                            "n": 1,
                            "msg": 'Exam started successfully',
                            "data":[],
                            'exam_link':encrypt_base_test_examination_link             
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
                            "msg": 'Exam not started',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

from django.utils.dateparse import parse_datetime

class ViewCandidateMockExamQuestionSet(GenericAPIView):
    
    # authentication_classes=[UserAdminJWTAuthentication]
    # permission_classes = (permissions.IsAuthenticated,)
    
    def post(self,request):
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        mock_exam_set = request_data.get('mock_exam_set')
        exam_schedule_id = request_data.get('exam_schedule_id')
        exam_id = request_data.get('exam_id')
        candidate_id = request_data.get('candidate_id')
        candidate_exam_id = request_data.get('candidate_exam_id')
        final_submit = False
        final_submit_obj=MockExamCandidateResult.objects.filter(isActive=True,id=candidate_exam_id).first()
        mock_test_start_date_time = timezone.now() #2025-07-17 15:13:19.643381+05:30
        schedule_exam_start_time_convert_time = timezone.now().strftime('%H:%M:%S')
        schedule_exam_start_date_convert_date = datefilterchangeformat(str(timezone.now().strftime('%Y-%m-%d')))

        if final_submit_obj is not None:
            result_serilazer = MockExamCandidateResultSerializer(final_submit_obj)
            if final_submit_obj.final_submit == True:
                final_submit = True
            if final_submit_obj.start_created_time is not None:
                serialized_time = result_serilazer.data['start_created_time']
                dt = parse_datetime(serialized_time)
                mock_test_start_date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                schedule_exam_start_date_convert_date = datefilterchangeformat(str(dt.strftime('%Y-%m-%d')))
                schedule_exam_start_time_convert_time = dt.strftime('%H:%M')
        
        if mock_exam_set is None or mock_exam_set == "":
            response_={
                        "n": 0,
                        "msg": 'Mock exam set Id is required',
                        "data":[]          
                    }
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            

        exam_set_question_objects = MockExamQuestionSet.objects.filter(isActive=True,id=mock_exam_set).first()
        if exam_set_question_objects is not None:
            question_set_ser = MockExamQuestionSetSerializer(exam_set_question_objects)
            
            #exam schedule
            exam_schedule_object = ScheduleExam.objects.filter(isActive=True,id=exam_schedule_id).first()
            exam_schedule_ser = ScheduleExamSerializer(exam_schedule_object)
            exam_schedule_ser_data = exam_schedule_ser.data
            
            if exam_schedule_ser.data['schedule_exam_date'] is not None and exam_schedule_ser.data['schedule_exam_date'] != "":
                schedule_exam_date_convert_date =  datefilterchangeformat(exam_schedule_ser.data['schedule_exam_date'])
            exam_schedule_ser_data.update({
                'schedule_exam_date_convert_date':schedule_exam_date_convert_date
            })
            #exam candidate relation
            # exam_candidate_relation_object = ExamCandidateSetRelation.objects.filter(isActive=True,exam_schedule_id=exam_schedule_id,exam_id=exam_id,exam_set=exam_set_id,candidate_id=candidate_id).first()
            # exam_candidate_relation_ser = ExamCandidateSetRelationSerializer(exam_candidate_relation_object)
            # exam_candidate_relation_ser_data = exam_candidate_relation_ser.data
            
            #candidate data
            candidate_object = Candidate.objects.filter(isActive=True,id=candidate_id).first()
            candidate_ser = CandidateSerializer(candidate_object)
            candidate_ser_data = candidate_ser.data
            
            
            question_set_ser_data = question_set_ser.data
            question_data = ""
            exam_detail_data = ""
            exam_detail_object = ExamSet.objects.filter(isActive=True,id=question_set_ser.data['exam_id']).first()
            if exam_detail_object is not None:
                exam_detail_ser = ExamSetSerializer(exam_detail_object)
                exam_detail_data = exam_detail_ser.data
                course_object = Course.objects.filter(isActive=True,id=exam_detail_ser.data['course']).first()
                if course_object is not None:
                    exam_detail_data.update({
                        'course_name':course_object.course_name,
                        'course_code':course_object.course_code
                    })
                else:
                    exam_detail_data.update({
                        'course_name':'',
                        'course_code':''
                    })
                    
                question_object = Question.objects.filter(isActive=True,id__in = question_set_ser.data['question_id']).order_by('id')
                question_ser = QuestionSerializer(question_object,many=True)
                for q in question_ser.data:
                    exam_result_question_object = MockExamCandidateResultAnswer.objects.filter(isActive=True,mock_exam_candidate_result_id=candidate_exam_id,question_id =q['id']).first()



                    if exam_result_question_object is not None:
                        q['candidate_option_id'] = exam_result_question_object.candidate_option_id
                        q['correct_answer_option'] = exam_result_question_object.correct_answer_option
                        q['candidate_option_answer'] = exam_result_question_object.candidate_option_answer
                        q['mark_for_review'] = exam_result_question_object.mark_for_review
                        question_answered_data = exam_result_question_object.question_data
                        try:
                            exam_result_question_ser_data = ast.literal_eval(question_answered_data)
                            if isinstance(exam_result_question_ser_data.get("tags"), str):
                                exam_result_question_ser_data["tags"] = json.loads(exam_result_question_ser_data["tags"])

                        except Exception as e:
                            exam_result_question_ser_data = {}
                    else:
                        q['candidate_option_id'] = None
                        q['candidate_option_answer'] = None
                        q['correct_answer_option'] = None
                        q['mark_for_review'] = None
                        exam_result_question_ser_data = {}



                    q['correct_answer_data'] = exam_result_question_ser_data
                    question_all_image_object = QuestionImages.objects.filter(isActive=True,question_id=q['id']).order_by('id')
                    question_all_image_ser = QuestionImagesSerializer(question_all_image_object,many=True)
                    
                    question_option_object = QuestionOption.objects.filter(isActive=True,question_id=q['id'])
                    question_option_ser = QuestionOptionSerializer(question_option_object,many=True)
                    
                    q['question_all_image_data'] = question_all_image_ser.data
                    q['question_option_data'] = question_option_ser.data
                    

                
                question_data = question_ser.data
            else:
                question_data = ""
                exam_detail_data = ""
            
            # data_to_serialize = convert_decimals_to_float(question_data)
            # encrypt_question_data = encrypt_data(json.dumps(data_to_serialize))
            question_set_ser_data.update({
                'exam_detail_data':exam_detail_data,
                'question_data':question_data,
                'exam_schedule_data':exam_schedule_ser_data,
                # 'exam_candidate_relation_data':exam_candidate_relation_ser_data,
                'candidate_data':candidate_ser_data,
                'final_submit':final_submit,
                'mock_test_start_date_time':mock_test_start_date_time,
                'schedule_exam_start_date_convert_date':schedule_exam_start_date_convert_date,
                'schedule_exam_start_time_convert_time':schedule_exam_start_time_convert_time,
                # 'encrypt_question_data':encrypt_question_data
                
            })
            
         

            
            response_={
                        "n": 1,
                        "msg": 'Details fetched successfully',
                        "data":question_set_ser_data,
                        # "cvdata":text_data
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
                        "msg": 'Mock exam set not found',
                        "data":[]          
                    }
            
            
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
       
class CaptureCandidateMockExamResult(GenericAPIView):

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        # exam_schedule_id = exam_serializer.data['id'],
        # exam_id = data['exam_set'],
        # exam_set = k['set'],
        # candidate_id = k['candidate']


        data = {}
        data['mock_exam_candidate_result_id'] =  request_data.get('exam_candidate_result_id')
        data['question_data'] =  request_data.get('question_data')
        
        if request_data.get('candidate_option_answer') is not None and request_data.get('candidate_option_answer') != "":
            data['candidate_option_answer'] =  request_data.get('candidate_option_answer')
        else:
            data['candidate_option_answer'] =  None
        


        if request_data.get('candidate_option_id') is not None and request_data.get('candidate_option_id') != "":
            data['candidate_option_id'] = request_data.get('candidate_option_id')
        else:
            data['candidate_option_id'] =  None
            
        if request_data.get('markreview') == "1":
            data['mark_for_review'] = True
        else:
            data['mark_for_review'] = False 
        data['question_id'] =  request_data.get('question_id')
        
        if request_data.get('correct_answer_option') is not None and request_data.get('correct_answer_option') != "":
            data['correct_answer_option'] =  request_data.get('correct_answer_option')
      
        else:
            data['correct_answer_option'] =  None
        data['marks'] =  request_data.get('marks')
        
        try:
            final_submit_obj = MockExamCandidateResult.objects.filter(id=data['mock_exam_candidate_result_id'],final_submit=True).first()
            if final_submit_obj is not None:
                response_={
                            "n": 0,
                            "msg": 'Exam already submitted,unable to submit answer',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)




            answer_object = MockExamCandidateResultAnswer.objects.filter(isActive=True,mock_exam_candidate_result_id=data['mock_exam_candidate_result_id'],question_id=data['question_id']).first()
            if answer_object is not None:
                exam_serializer = MockExamCandidateResultAnswerSerializer(answer_object,data=data,partial=True)
                if exam_serializer.is_valid():                
                    exam_serializer.save()
                    
                    response_={
                                "n": 1,
                                "msg": 'Capured',
                                "data":exam_serializer.data,           
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
                                "msg": 'Data not captured',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            else:

                exam_serializer = MockExamCandidateResultAnswerSerializer(data=data)
                if exam_serializer.is_valid():
                    exam_serializer.save()
                    
                    response_={
                                "n": 1,
                                "msg": 'Data Captured successfully',
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
                                "msg": 'Data not captured',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class SubmitCandidateMockExam(GenericAPIView):

    def post(self,request): 
        
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
            
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        # exam_schedule_id = exam_serializer.data['id'],
        # exam_id = data['exam_set'],
        # exam_set = k['set'],
        # candidate_id = k['candidate']
        data = {}
        data['candidate_exam_id'] =  request_data.get('candidate_exam_id')
        data['all_data'] = str(request_data.get('all_data'))
        data['end_created_time'] = timezone.now()  
        data['final_submit']=True
        # data['exam_schedule_id'] = request_data['all_data']['exam_candidate_relation_data']['exam_schedule_id']
    
        try:
            exam_result_object = MockExamCandidateResult.objects.filter(id=data['candidate_exam_id'],).first()
            if exam_result_object is None:
                response_={
                            "n": 0,
                            "msg": 'Exam not found',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                

            if exam_result_object.final_submit == True:
                response_={
                            "n": 0,
                            "msg": 'Exam already submitted',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
                



            #check mandatory questions is selected or not
            submited_questions_count=MockExamCandidateResultAnswer.objects.filter(mock_exam_candidate_result_id=exam_result_object.id,mark_for_review=False,).order_by('question_id').distinct('question_id').count()

            exam_set_obj=MockExamQuestionSet.objects.filter(id=exam_result_object.mock_exam_set).first()
            if exam_set_obj is not None:
                mandatory_questions_count=exam_set_obj.mandatory_questions
                if int(submited_questions_count) < int(mandatory_questions_count):

                    response_={
                                "n": 0,
                                "msg": 'Please attempt atleast '+str(mandatory_questions_count)+' questions',
                                "data":[]                
                            }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)


            exam_serializer = MockExamCandidateResultSerializer(exam_result_object,data=data,partial=True)
            if exam_serializer.is_valid():                
                exam_serializer.save()
                
                generate_pdf_task = threading.Thread(target=save_mock_result_async, args=(str(exam_serializer.data['id']), exam_serializer.data))
                generate_pdf_task.start()

                # generate_pdf_task = threading.Thread(target=check_generate_certificate_pdf_async, args=(str(exam_serializer.data['id']), exam_serializer.data))
                # generate_pdf_task.start()

                response_={
                            "n": 1,
                            "msg": 'Exam Submitted successfully',
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
                            "msg": 'Exam not submitted',
                            "data":[]                
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
        
        except ValueError as e:
            response_={
                            "n": 0,
                            "msg": str(e),
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    
class GetCandidateMockExamResultDetails(GenericAPIView):
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

        data['mock_exam_set'] =  request_data.get('mock_exam_set_id')
        data['candidate_id'] =  str(request.user.id)
        data['start_created_time'] = timezone.now()

        mock_question_set_object = MockExamQuestionSet.objects.filter(isActive=True,id=data['mock_exam_set']).first()
        if mock_question_set_object is None:
            response_={
                            "n": 0,
                            "msg": 'Mock exam set not found',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        data['exam_schedule_id'] =  mock_question_set_object.exam_schedule_id if mock_question_set_object else ''

        if data['exam_schedule_id'] is None or data['exam_schedule_id'] == "":
            response_={
                            "n": 0,
                            "msg": 'Exam schedule not found for this mock exam set',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
            
        schedule_exam_object = ScheduleExam.objects.filter(isActive=True,id=data['exam_schedule_id']).first() 
        if schedule_exam_object is None:
            response_={
                            "n": 0,
                            "msg": 'Exam schedule not found',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


        data['exam_id'] =  schedule_exam_object.exam_set if schedule_exam_object else ''




        already_exist_object = MockExamCandidateResult.objects.filter(isActive=True,mock_exam_set = data['mock_exam_set'],candidate_id = data['candidate_id']).first()
        if already_exist_object is not None:
            
            exam_array = {
                "exam_schedule_id" : already_exist_object.exam_schedule_id,
                "mock_exam_set" : already_exist_object.mock_exam_set,
                "candidate_id" : data['candidate_id'],
                "exam_id" : already_exist_object.exam_id,
                "candidate_exam_id":already_exist_object.id
            }

            base_data_to_serialize = convert_decimals_to_float(exam_array)
            encrypt_base_test_examination_link = encrypt_data(json.dumps(base_data_to_serialize))
            response_={
                        "n": 1,
                        "msg": 'Exam resumed successfully',
                        "data":[],
                        'exam_link':encrypt_base_test_examination_link             
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
                            "msg": 'Result not found for this mock exam set',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

class GetCourseNonAttemptExamCandidates(GenericAPIView):
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
        schedule_id =  request_data.get('schedule_id')
        exam_set_id =  request_data.get('exam_set_id')
        schedule_exam_attempt =  request_data.get('schedule_exam_attempt')
        course_id =  request_data.get('course_id')
        enrolled_candidate_objs=Enrollments.objects.filter(isActive=True,enrollments_status='2',).order_by('candidate').distinct('candidate')
        if request.user.member_of is not None and request.user.member_of != '' :
            college =str(request.user.member_of)
        else:
            college=str(request.user.id)
        request_data['college']=college

        if course_id is not None and course_id !='':
            enrolled_candidate_objs=enrolled_candidate_objs.filter(course=course_id)
        
        if schedule_id is not None and schedule_id !='':
            enrolled_candidate_objs=enrolled_candidate_objs.filter(schedule=schedule_id)

        candidate_ids=list(enrolled_candidate_objs.values_list('candidate',flat=True))





        candidate_objs=Candidate.objects.filter(id__in=candidate_ids,isActive=True).order_by('first_name','middle_name','last_name')
        # print("data",request_data)
        if course_id is not None and course_id !='' and schedule_id is not None and schedule_id !='' and exam_set_id is not None and exam_set_id !='' and schedule_exam_attempt is not None and schedule_exam_attempt !='':
            schedule_already_attempted_candidates=ScheduleExam.objects.filter(course=course_id,college=college,schedule=schedule_id,exam_set=exam_set_id,attempt=schedule_exam_attempt).first()
            # print("schedule_already_attempted_candidates",schedule_already_attempted_candidates)
            if schedule_already_attempted_candidates is not None:
                exclude_candidates_ids=list(ExamCandidateSetRelation.objects.filter(exam_schedule_id=schedule_already_attempted_candidates.id).order_by('candidate_id').distinct('candidate_id').values_list('candidate_id',flat=True))
                candidate_objs=candidate_objs.exclude(id__in=exclude_candidates_ids)

        if candidate_objs.exists():
            serializer=CandidateSerializer(candidate_objs,many=True)
        
            response_={
                        "n": 1,
                        "msg": 'Candidates Found successfully',
                        "data":serializer.data,
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
                            "msg": 'Candidates not found',
                            "data":[]                
                        }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)






















