from django.shortcuts import render
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import json
import uuid
from django.utils import timezone
from .models import *
from usermanagement.serializers import *
from adminauth.serializers import *
from helpers.validations import *
from rest_framework import permissions
from adminauth.jwt import UserAdminJWTAuthentication
from django.contrib.auth.hashers import make_password,check_password
from adminauth.models import *
from adminauth.serializers import *
from candidate.models import *
from candidate.serializers import *
from master.models import Department

# Create your views here.

def _encrypted_header(request):
    if 'encrypted' in request.headers.keys():
        return request.headers.get('encrypted')
    return ""

def _final_response(request, response_):
    encryped_header = _encrypted_header(request)
    if encryped_header == "1":
        data_to_serialize = convert_decimals_to_float(response_)
        encdata = encrypt_data(json.dumps(data_to_serialize))
        return Response(encdata, status=200)
    return Response(response_, status=200)

def _error_response(request, msg, data=None, n=0):
    return _final_response(request, {"n": n, "msg": msg, "data": data if data is not None else {}})

def _requesting_admin(request):
    return UserAdmin.objects.filter(id=request.user.id, isActive=True).first()

def _requesting_college_id(request):
    admin_obj = _requesting_admin(request)
    if admin_obj is not None and admin_obj.college_id is not None:
        return str(admin_obj.college_id)
    return None

def _valid_role(role_code):
    if role_code in (None, ""):
        return None
    return Roles.objects.filter(role_code=role_code, is_active=True).first()


class StaticRoleList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        obj = Roles.objects.filter(is_active=True).order_by('id')
        ser = RolesSerializer(obj, many=True)
        response_ = {
            "n": 1,
            'msg': 'Roles found successfully.',
            'data': ser.data
        }
        return _final_response(request, response_)


class AddDesignation(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        role_code = request_data.get('role_code')
        role_name = request_data.get('role_name')
        if role_code in (None, ''):
            return _error_response(request, 'role_code is required.')
        if role_name in (None, ''):
            return _error_response(request, 'role_name is required.')

        if Designation.objects.filter(role_code=role_code).exists():
            return _error_response(request, 'Designation with this role_code already exists.')

        data = {
            'role_code': role_code,
            'role_name': role_name,
            'description': request_data.get('description'),
            'is_active': request_data.get('is_active', True),
            'createdBy': str(request.user.id),
        }
        ser = DesignationSerializer(data=data)
        if ser.is_valid():
            ser.save()
            response_ = {
                "n": 1,
                'msg': 'Designation added successfully.',
                'data': ser.data
            }
            return _final_response(request, response_)
        return _error_response(request, 'Designation not added.', ser.errors)


class DesignationList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        obj = Designation.objects.filter(is_active=True).order_by('id')
        ser = DesignationSerializer(obj, many=True)
        response_ = {
            "n": 1,
            'msg': 'Designation list found successfully.',
            'data': ser.data
        }
        return _final_response(request, response_)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        id = request_data.get('id')
        if id in (None, ''):
            return _error_response(request, 'id is required.')

        obj = Designation.objects.filter(id=id, is_active=True).first()
        if obj is None:
            return _error_response(request, 'Designation not found.')
        ser = DesignationSerializer(obj)
        response_ = {
            "n": 1,
            'msg': 'Designation details found.',
            'data': ser.data
        }
        return _final_response(request, response_)


class UpdateDesignation(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        id = request_data.get('id')
        if id in (None, ''):
            return _error_response(request, 'id is required.')

        obj = Designation.objects.filter(id=id).first()
        if obj is None:
            return _error_response(request, 'Designation not found.')

        role_code = request_data.get('role_code')
        if role_code not in (None, ''):
            if Designation.objects.filter(role_code=role_code).exclude(id=id).exists():
                return _error_response(request, 'Designation with this role_code already exists.')
            obj.role_code = role_code

        if request_data.get('role_name') not in (None, ''):
            obj.role_name = request_data.get('role_name')
        if request_data.get('description') is not None:
            obj.description = request_data.get('description')
        if request_data.get('is_active') is not None:
            obj.is_active = bool(request_data.get('is_active'))
        obj.updatedBy = str(request.user.id)
        obj.updatedAt = timezone.now()
        obj.save()

        ser = DesignationSerializer(obj)
        response_ = {
            "n": 1,
            'msg': 'Designation updated successfully.',
            'data': ser.data
        }
        return _final_response(request, response_)


class DeleteDesignation(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        id = request_data.get('id')
        if id in (None, ''):
            return _error_response(request, 'id is required.')

        obj = Designation.objects.filter(id=id).first()
        if obj is None:
            return _error_response(request, 'Designation not found.')

        check_mapping = UserAdmin.objects.filter(role_code=obj.role_code, isActive=True).first()
        if check_mapping is not None:
            return _error_response(request, 'This designation is mapped to a user.')

        obj.is_active = False
        obj.save()
        response_ = {
            "n": 1,
            'msg': 'Designation deleted successfully.',
            'data': {}
        }
        return _final_response(request, response_)


class AddUser(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        role_code = request_data.get('role_code')
        role_obj = _valid_role(role_code)
        if role_obj is None:
            return _error_response(request, 'role_code is required or not valid.')

        admin_obj = _requesting_admin(request)
        if admin_obj is None:
            return _error_response(request, 'logged in user not found')

        college_id = request_data.get('college_id') or _requesting_college_id(request)

        if role_code in ('admin', 'faculty'):
            data = {}
            data['role_code'] = role_code
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['name'] = request_data.get('name')
            data['designation'] = request_data.get('designation')
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber')
            data['email'] = str(request_data.get('email') or '').lower()
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['city'] = request_data.get('city')
            data['state'] = request_data.get('state')
            data['country'] = request_data.get('country')
            data['pincode'] = request_data.get('pincode')
            data['address_line_one'] = request_data.get('address_line_one')
            data['address_line_two'] = request_data.get('address_line_two')
            data['joining_date'] = request_data.get('joining_date')
            data['department_id'] = request_data.get('department_id')
            data['marital_status'] = request_data.get('marital_status')
            data['blood_group'] = request_data.get('blood_group')
            data['religion'] = request_data.get('religion')
            data['qualification'] = request_data.get('qualification')
            data['category'] = request_data.get('category')
            data['caste'] = request_data.get('caste')
            data['faculty_sub_role'] = request_data.get('faculty_sub_role')
            data['employee_code'] = request_data.get('employee_code')
            data['employment_type'] = request_data.get('employment_type')
            data['official_email'] = request_data.get('official_email')
            data['years_of_experience'] = request_data.get('years_of_experience')
            data['specialization'] = request_data.get('specialization')
            data['reporting_to'] = request_data.get('reporting_to')
            data['status'] = request_data.get('status', True)
            data['password'] = make_password(request_data.get('password') or 'Default@123')
            data['og_code'] = admin_obj.og_code or 'SUPER'
            data['createdBy'] = str(request.user.id)

            data['member_type'] = admin_obj.user_type
            if admin_obj.member_of is None:
                data['member_of'] = str(admin_obj.id)
            else:
                data['member_of'] = str(admin_obj.member_of)

            if role_code == 'admin':
                data['user_type'] = request_data.get('user_type') or 3
            else:
                data['user_type'] = 5
                if admin_obj.member_of is None:
                    data['parent_college'] = str(admin_obj.id)
                else:
                    data['parent_college'] = str(admin_obj.member_of)

            if college_id not in (None, ""):
                data['college_id'] = int(college_id)

            if data['email'] in (None, ""):
                return _error_response(request, 'Email is required.')
            email_object = UserAdmin.objects.filter(isActive=True, email=data['email']).first()
            if email_object is not None:
                return _error_response(request, 'Email already exists')

            serializer = UserAdminSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return _final_response(request, {
                    "n": 1,
                    'msg': 'User added successfully.',
                    'data': serializer.data
                })
            return _error_response(request, 'User not added.', serializer.errors)

        if role_code == 'student':
            data = {}
            data['role_code'] = role_code
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['email'] = str(request_data.get('email') or '').lower()
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber')
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['blood_group'] = request_data.get('blood_group')
            data['aadhaar_number'] = request_data.get('aadhaar_number')
            data['city'] = request_data.get('city')
            data['state'] = request_data.get('state')
            data['country'] = request_data.get('country')
            data['pincode'] = request_data.get('pincode')
            data['address_line_one'] = request_data.get('address_line_one')
            data['address_line_two'] = request_data.get('address_line_two')
            data['department_id'] = request_data.get('department_id')
            data['course_id'] = request_data.get('course_id')
            data['semester_id'] = request_data.get('semester_id')
            data['class_group_id'] = request_data.get('class_group_id')
            data['academic_year_id'] = request_data.get('academic_year_id')
            data['division'] = request_data.get('division')
            data['admission_number'] = request_data.get('admission_number')
            data['roll_number'] = request_data.get('roll_number')
            data['university_prn'] = request_data.get('university_prn')
            data['admission_status'] = request_data.get('admission_status') or 'Draft'
            data['student_status'] = request_data.get('student_status') or 'Active'
            data['college_id'] = college_id
            data['password'] = make_password(request_data.get('password') or 'Student@123')
            data['createdBy'] = str(request.user.id)

            if data['email'] in (None, ""):
                return _error_response(request, 'Email is required.')
            email_object = Candidate.objects.filter(isActive=True, email=data['email']).first()
            if email_object is not None:
                return _error_response(request, 'Email already exists')

            serializer = CandidateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return _final_response(request, {
                    "n": 1,
                    'msg': 'User added successfully.',
                    'data': serializer.data
                })
            return _error_response(request, 'User not added.', serializer.errors)

        if role_code == 'parent':
            data = {}
            data['role_code'] = role_code
            data['parent_code'] = request_data.get('parent_code') or ('PARENT' + uuid.uuid4().hex[:8].upper())
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['email'] = str(request_data.get('email') or '').lower()
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['alternate_mobilenumber'] = request_data.get('alternate_mobilenumber')
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['occupation'] = request_data.get('occupation')
            data['parent_relationship'] = request_data.get('parent_relationship')
            data['address_line_one'] = request_data.get('address_line_one')
            data['address_line_two'] = request_data.get('address_line_two')
            data['city'] = request_data.get('city')
            data['state'] = request_data.get('state')
            data['country'] = request_data.get('country')
            data['pincode'] = request_data.get('pincode')
            data['college_id'] = college_id
            data['student_ids'] = request_data.get('student_ids') or []
            data['password'] = make_password(request_data.get('password') or 'Parent@123')
            data['createdBy'] = str(request.user.id)

            if data['email'] in (None, ""):
                return _error_response(request, 'Email is required.')
            email_object = Parent.objects.filter(isActive=True, email=data['email']).first()
            if email_object is not None:
                return _error_response(request, 'Email already exists')

            serializer = ParentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return _final_response(request, {
                    "n": 1,
                    'msg': 'User added successfully.',
                    'data': serializer.data
                })
            return _error_response(request, 'User not added.', serializer.errors)

        return _error_response(request, 'role_code is not valid.')


def _enrich_useradmin_display_fields(item):
    department_id = item.get('department_id')
    if department_id not in (None, ""):
        dept = Department.objects.filter(id=department_id).first()
        item['department_name'] = dept.department_name if dept is not None else None
    else:
        item['department_name'] = None
    return item


def _user_list_data(request, request_data):
    college_id = request_data.get('college_id') or _requesting_college_id(request)
    search = request_data.get('search')
    role_code = request_data.get('role_code') or 'faculty'

    result = []

    def apply_search(qs, fields):
        if search not in (None, ""):
            from django.db.models import Q
            query = Q()
            for f in fields:
                query = query | Q(**{f + '__icontains': search})
            qs = qs.filter(query)
        return qs

    def apply_college(qs, column):
        if college_id not in (None, ""):
            qs = qs.filter(**{column: college_id})
        return qs

    if role_code in ('admin', 'faculty'):
        qs = UserAdmin.objects.filter(isActive=True, role_code__in=['admin', 'faculty'])
        if role_code in ('admin', 'faculty'):
            qs = qs.filter(role_code=role_code)
        if college_id not in (None, ""):
            qs = qs.filter(college_id=int(college_id))
        qs = apply_search(qs, ['first_name', 'last_name', 'name', 'email', 'mobilenumber'])
        for item in UserAdminSerializer(qs.order_by('-createdAt'), many=True).data:
            item['role_code'] = item.get('role_code') or role_code
            if item.get('name') not in (None, ""):
                item['display_name'] = item['name']
            else:
                item['display_name'] = ((item.get('first_name') or '') + ' ' + (item.get('last_name') or '')).strip()
            _enrich_useradmin_display_fields(item)
            result.append(item)

    if role_code in (None, "", 'student'):
        qs = Candidate.objects.filter(isActive=True, role_code='student')
        qs = apply_college(qs, 'college_id')
        qs = apply_search(qs, ['first_name', 'last_name', 'email', 'mobilenumber', 'admission_number', 'roll_number'])
        for item in CandidateSerializer(qs.order_by('-createdAt'), many=True).data:
            item['role_code'] = 'student'
            item['display_name'] = ((item.get('first_name') or '') + ' ' + (item.get('last_name') or '')).strip()
            result.append(item)

    if role_code in (None, "", 'parent'):
        qs = Parent.objects.filter(isActive=True, role_code='parent')
        qs = apply_college(qs, 'college_id')
        qs = apply_search(qs, ['first_name', 'last_name', 'email', 'mobilenumber'])
        for item in ParentSerializer(qs.order_by('-createdAt'), many=True).data:
            item['role_code'] = 'parent'
            item['display_name'] = ((item.get('first_name') or '') + ' ' + (item.get('last_name') or '')).strip()
            result.append(item)

    return result


class UserList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        response_ = {
            "n": 1,
            'msg': 'Users found successfully.',
            'data': _user_list_data(request, request.GET)
        }
        return _final_response(request, response_)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        response_ = {
            "n": 1,
            'msg': 'Users found successfully.',
            'data': _user_list_data(request, request_data)
        }
        return _final_response(request, response_)


class UserDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return self._respond(request, request.GET)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        return self._respond(request, request_data)

    def _respond(self, request, request_data):
        user_id = request_data.get('id')
        role_code = request_data.get('role_code')
        if user_id in (None, ""):
            return _error_response(request, 'id is required.')
        if role_code in (None, ""):
            return _error_response(request, 'role_code is required.')

        obj = None
        if role_code in ('admin', 'faculty'):
            obj = UserAdmin.objects.filter(id=user_id, isActive=True).first()
            ser = UserAdminSerializer(obj).data if obj is not None else None
        elif role_code == 'student':
            obj = Candidate.objects.filter(id=user_id, isActive=True).first()
            ser = CandidateSerializer(obj).data if obj is not None else None
        elif role_code == 'parent':
            obj = Parent.objects.filter(id=user_id, isActive=True).first()
            ser = ParentSerializer(obj).data if obj is not None else None
        else:
            return _error_response(request, 'role_code is not valid.')

        if ser is None:
            return _error_response(request, 'User not found.')
        ser['role_code'] = role_code
        if role_code in ('admin', 'faculty'):
            _enrich_useradmin_display_fields(ser)
        return _final_response(request, {
            "n": 1,
            'msg': 'User details found successfully.',
            'data': ser
        })


class UpdateUser(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user_id = request_data.get('id')
        role_code = request_data.get('role_code')
        if user_id in (None, ""):
            return _error_response(request, 'id is required.')
        if role_code in (None, ""):
            return _error_response(request, 'role_code is required.')

        data = dict(request_data)
        data.pop('id', None)
        data.pop('role_code', None)

        password = data.pop('password', None)
        if password not in (None, ""):
            data['password'] = make_password(password)

        if role_code in ('admin', 'faculty'):
            if 'college_id' in data and data['college_id'] not in (None, ""):
                data['college_id'] = int(data['college_id'])
            obj = UserAdmin.objects.filter(id=user_id, isActive=True).first()
            if obj is None:
                return _error_response(request, 'User not found.')
            serializer = UserAdminSerializer(obj, data=data, partial=True)
        elif role_code == 'student':
            obj = Candidate.objects.filter(id=user_id, isActive=True).first()
            if obj is None:
                return _error_response(request, 'User not found.')
            serializer = CandidateSerializer(obj, data=data, partial=True)
        elif role_code == 'parent':
            obj = Parent.objects.filter(id=user_id, isActive=True).first()
            if obj is None:
                return _error_response(request, 'User not found.')
            serializer = ParentSerializer(obj, data=data, partial=True)
        else:
            return _error_response(request, 'role_code is not valid.')

        if serializer.is_valid():
            serializer.save()
            return _final_response(request, {
                "n": 1,
                'msg': 'User updated successfully.',
                'data': serializer.data
            })
        return _error_response(request, 'User not updated.', serializer.errors)


class DeleteUser(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user_id = request_data.get('id')
        role_code = request_data.get('role_code')
        if user_id in (None, ""):
            return _error_response(request, 'id is required.')
        if role_code in (None, ""):
            return _error_response(request, 'role_code is required.')

        obj = None
        if role_code in ('admin', 'faculty'):
            obj = UserAdmin.objects.filter(id=user_id, isActive=True).first()
        elif role_code == 'student':
            obj = Candidate.objects.filter(id=user_id, isActive=True).first()
        elif role_code == 'parent':
            obj = Parent.objects.filter(id=user_id, isActive=True).first()
        else:
            return _error_response(request, 'role_code is not valid.')

        if obj is None:
            return _error_response(request, 'User not found.')

        obj.isActive = False
        obj.save()
        return _final_response(request, {
            "n": 1,
            'msg': 'User deleted successfully.',
            'data': {}
        })


class ParentLogin(GenericAPIView):
    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        username = request_data.get('username')
        password = request_data.get('password')
        if username in (None, ""):
            return _error_response(request, 'Username is required')
        if password in (None, ""):
            return _error_response(request, 'Password is required')

        user_object = Parent.objects.filter(
            Q(isActive=True, username=username) | Q(isActive=True, email=username)
        ).first()
        if user_object is None:
            return _error_response(request, 'User not found')

        check_user_password = check_password(password, user_object.password)
        if check_user_password is False:
            return _error_response(request, 'Incorrect password')

        ParentToken.objects.filter(user_id=user_object.id).update(isActive=False)
        user_token = ParentToken.objects.create(user_id=user_object.id, authToken=user_object.token)
        return _final_response(request, {
            "n": 1,
            'msg': 'User logged in successfully',
            "token": user_token.authToken,
            "data": ParentSerializer(user_object).data
        })


class ParentLogout(GenericAPIView):
    def post(self, request):
        encryped_header = _encrypted_header(request)
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        token = request_data.get('token')
        if token in (None, ""):
            return _error_response(request, 'token required')

        token_obj = ParentToken.objects.filter(authToken=token, isActive=True).first()
        if token_obj is None:
            return _error_response(request, 'token not found')

        token_obj.isActive = False
        token_obj.save()
        return _final_response(request, {
            "n": 1,
            'msg': 'Logout Successful!',
            'data': []
        })

class AddRole(GenericAPIView):
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
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
        
            data['member_type'] = adminobj.user_type
            if adminobj.member_of is None :
                data['member_of'] = str(adminobj.id)
            else:
                data['member_of'] = str(adminobj.member_of)
            data['og_code'] = adminobj.og_code
            
            data['name'] = request_data.get('name')
            data['remark'] = request_data.get('remark')
            data['createdBy'] = str(request.user.id)
           
            if data['name'] is not None and data['name'] !="":
                obj = UsereRole.objects.filter(isActive=True)
                ser = UsereRoleSerializer(obj,many=True)
                for c in ser.data:
                    existingname = c['name'].lower()
                    newname = data['name'].lower()

                    existingmembertype = c['member_type']
                    newmembertype =  data['member_type']

                    existingmemberof = c['member_of']
                    newmemberof = data['member_of']

                    if existingname == newname and existingmembertype == newmembertype and existingmemberof == newmemberof:
                        response_={
                            "n": 0,
                            'msg':"Role already exits",
                            'data':{}
                        }    
                        if encryped_header == "1" :
                            data_to_serialize = convert_decimals_to_float(response_)
                            encdata = encrypt_data(json.dumps(data_to_serialize))
                            return Response(encdata,status=200)
                        else:
                            return Response(response_,status=200)
                  
                cser = UsereRoleSerializer(data=data)
                if cser.is_valid():
                    cser.save()
                    response_={
                        "n": 1,
                        'msg':'Role added successfully.',
                        'data':cser.data
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
                else:
                    print("error",cser.errors)
                    response_={
                        "n": 0,
                        'msg':'Role not added.',
                        'data':cser.errors
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
                    'msg':'Please Provide role name.',
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
                    "msg": 'loggedin user not found',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
    

    
class RoleList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
            member_type = adminobj.user_type
            if adminobj.member_of is None :
                member_of = str(adminobj.id)
            else:
                member_of = str(adminobj.member_of)
            og_code = adminobj.og_code

            obj = UsereRole.objects.filter(isActive=True,member_type=member_type,member_of = member_of,og_code=og_code).order_by('id')
            ser = UsereRoleSerializer(obj,many=True)
            for i in ser.data:
                usedobj = UserAdmin.objects.filter(role=i['id'],isActive=True).first()
                if usedobj is not None:
                    i['isused'] = True
                else:
                    i['isused'] = False

            response_={
                "n": 1,
                'msg':'Role list found successfully.',
                'data': ser.data
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
                'msg':'Role list not found.',
                'data': {}
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
        
        id = request_data.get('id')
        if id is not None and id != "":
            catobj=UsereRole.objects.filter(id=id,isActive=True).last()
            if catobj is not None:
                serializer = UsereRoleSerializer(catobj)
                response_={
                    "n": 1,
                    'msg':'Role Details Found.',
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
                    'msg':'No Data FOund.',
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
        
        
class UpdateRole(GenericAPIView):
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
        data['id'] = request_data.get('id')
        if data['id'] is not None:
            data['name'] = request_data.get('name')
            data['remark'] = request_data.get('remark')
        
            obj = UsereRole.objects.filter(isActive=True).exclude(id=data['id'])
            ser = UsereRoleSerializer(obj,many=True)
            for p in ser.data:
                if str(p['name']).lower() == str(data['name']).lower():
                    response_={
                        "n": 0,
                        'msg':'name already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            peobj=UsereRole.objects.filter(id=data['id'],isActive=True).first()
            if peobj is not None:
                serializer = UsereRoleSerializer(peobj,data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Role Updated Successfully.',
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
                        "n": 1,
                        'msg':'Role Not Updated.',
                        'data':serializer.errors
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
        


class DeleteRole(GenericAPIView):
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
            cat_obj=UsereRole.objects.filter(id=id,isActive=True).first()
            if cat_obj is not None:
                check_mapping=UserAdmin.objects.filter(role=id,isActive=True).first()
                if check_mapping is not None:
                    response_={
                        "n": 0,
                        'msg':'This role is mapped to user.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)



                cat_obj.isActive = False
                cat_obj.save()
                response_={
                    "n": 1,
                    'msg':'Role Deleted Successfully.',
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
                    'msg':'Role id not found.',
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
            
            

class AddMember(GenericAPIView):
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
        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
            data['member_type'] = adminobj.user_type
            if adminobj.member_of is None :
                data['member_of'] = str(adminobj.id)
            else:
                data['member_of'] = str(adminobj.member_of)
            data['og_code'] = adminobj.og_code
        
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['designation'] = request_data.get('designation')
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['email'] = str(request_data.get('email')).lower()
            data['password'] = make_password(request_data.get('password'))
            data['role'] = request_data.get('role')
            data['reporting_to'] = request_data.get('reporting_to')
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['city'] = request_data.get('city')
            data['country'] = request_data.get('country')
            data['state'] = request_data.get('state')
            data['pincode'] = request_data.get('pincode')
            data['joining_date'] = request_data.get('joining_date')
            data['is_member'] = True
            data['user_type'] =  data['member_type']
            # data['parent_college'] =  ''

            
            # data['member_type'] = 3
            # data['member_of'] = str(request.user.id)
            # data['og_code'] = str(request.user.og_code)
            data['deactivate'] = True
            
            email_object = UserAdmin.objects.filter(isActive=True,email=data['email']).last()
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
            
            serializer = UserAdminSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                response_={
                    "n": 1,
                    "msg": 'Member added successfully',
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
                    "msg": 'Member not added',
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
                    "msg": 'logged in user not found',
                    "data":[]                     
                }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)

                


class MemberList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')

        userid = request.user.id
        adminobj = UserAdmin.objects.filter(id=userid,isActive=True).first()
        if adminobj is not None:
            member_type = adminobj.user_type
            if adminobj.member_of is None :
                member_of = str(adminobj.id)
            else:
                member_of = str(adminobj.member_of)
            og_code = adminobj.og_code

            obj = UserAdmin.objects.filter(member_type = member_type,member_of=member_of,og_code=og_code,is_member=True,isActive=True)
            member_ser = UserAdminSerializer(obj,many=True)
          
            newadminobj = UserAdmin.objects.filter(id=member_of,isActive=True).first()
            userser =  UserAdminSerializer(newadminobj)


            combined_data = member_ser.data + [userser.data]
            for i in combined_data:
                if i['name'] is not None and i['name'] != '':
                    i['username'] = i['name']
                else:
                    i['username'] = i['first_name'] +" "+i['last_name']

                i['createdAt'] = i['createdAt'].split('T')[0].split('-')[2]+"-"+i['createdAt'].split('T')[0].split('-')[1]+"-"+i['createdAt'].split('T')[0].split('-')[0]
                
                obj = UsereRole.objects.filter(id=i['role']).first()
                if obj is not None:
                    i['role'] = obj.name
                else:
                    i['role'] = ""

                
            response_={
                "n": 1,
                'msg':'Members found Successfully.',
                'data':combined_data
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
                "msg": 'member list not found',
                "data":[]                     
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
        
        id = request_data.get('id')
        if id is not None and id != "":
            userobj=UserAdmin.objects.filter(id=id,isActive=True).last()
            if userobj is not None:
                serializer = UserAdminSerializer(userobj)
                member_type = serializer.data['member_type']
                member_of = serializer.data['member_of']
                og_code =  serializer.data['og_code']
                selfid =   serializer.data['id']

                obj = UserAdmin.objects.filter(member_type = member_type,member_of=member_of,og_code=og_code,is_member=True,isActive=True).exclude(id=selfid)
                member_ser = UserAdminSerializer(obj,many=True)
            
                newadminobj = UserAdmin.objects.filter(id=member_of,isActive=True).first()
                userser =  UserAdminSerializer(newadminobj)


                combined_data = member_ser.data + [userser.data]
                for i in combined_data:
                    if i['name'] is not None and i['name'] != '':
                        i['username'] = i['name']
                    else:
                        i['username'] = i['first_name'] +" "+i['last_name']

                



                response_={
                    "n": 1,
                    'msg':'User Admin Details Found.',
                    'data':serializer.data,
                    'memberdata':combined_data
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
                    'msg':'No Data FOund.',
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
        

    

class DeleteMember(GenericAPIView):
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
            user_obj=UserAdmin.objects.filter(id=id,isActive=True).first()
            if user_obj is not None:
                user_obj.isActive = False
                user_obj.save()
                response_={
                    "n": 1,
                    'msg':'Member Deleted Successfully.',
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
                    'msg':'Member id not found.',
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
            

        
class UpdateMember(GenericAPIView):
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
            data['first_name'] = request_data.get('first_name')
            data['middle_name'] = request_data.get('middle_name')
            data['last_name'] = request_data.get('last_name')
            data['designation'] = request_data.get('designation')
            data['mobilenumber'] = request_data.get('mobilenumber')
            data['email'] = str(request_data.get('email')).lower()
            data['role'] = request_data.get('role')
            data['reporting_to'] = request_data.get('reporting_to')
            data['gender'] = request_data.get('gender')
            data['dob'] = request_data.get('dob')
            data['city'] = request_data.get('city')
            data['country'] = request_data.get('country')
            data['state'] = request_data.get('state')
            data['pincode'] = request_data.get('pincode')
            data['joining_date'] = request_data.get('joining_date')
        
            
            obj = UserAdmin.objects.filter(isActive=True).exclude(id=id)
            ser = UserAdminSerializer(obj,many=True)
            for p in ser.data:
                if str(p['first_name']).lower() == str(data['first_name']).lower():
                    response_={
                        "n": 0,
                        'msg':'First name already exits.',
                        'data':{}
                    }
                    if encryped_header == "1" :
                        data_to_serialize = convert_decimals_to_float(response_)
                        encdata = encrypt_data(json.dumps(data_to_serialize))
                        return Response(encdata,status=200)
                    else:
                        return Response(response_,status=200)
            peobj=UserAdmin.objects.filter(id=id,isActive=True).first()
            if peobj is not None:
                serializer = UserAdminSerializer(peobj,data=data,partial=True)
                if serializer.is_valid():
                    serializer.save()
                    response_={
                        "n": 1,
                        'msg':'Member Updated Successfully.',
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
                        "n": 1,
                        'msg':'Member Not Updated.',
                        'data':serializer.errors
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
  

            

   
 
