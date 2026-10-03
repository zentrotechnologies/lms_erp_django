from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
import json
from datetime import datetime, date, timedelta, time
from django.utils import timezone

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
from adminauth.models import UserAdmin, UserAdminToken
from usermanagement.models import Designation
from candidate.jwt import CandidateJWTAuthentication
from schedule.models import TimetableTemplate, TimetableSlot, LectureEntry
from course.models import Subject
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


def _parse_date(value, field_name):
    if value in (None, ""):
        return None, None
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date(), None
    except (TypeError, ValueError):
        return None, '%s must be a valid date in YYYY-MM-DD format.' % field_name


def _requesting_admin(request):
    return UserAdmin.objects.filter(id=request.user.id, isActive=True).first()


def _is_admin_user(user):
    admin_obj = UserAdmin.objects.filter(id=user.id, isActive=True).first()
    if admin_obj is None:
        return False
    if str(admin_obj.role_code or '').strip().lower() in ('superadmin', 'admin'):
        return True
    return admin_obj.role in (1, 2, 3, 4)


def _enrich_leave_item(item):
    applicant_id = item.get('applicant_id')
    if applicant_id not in (None, ""):
        applicant = UserAdmin.objects.filter(id=applicant_id).first()
        if applicant is not None:
            item['applicant_name'] = applicant.name or (applicant.first_name + ' ' + applicant.last_name).strip()
        else:
            item['applicant_name'] = None
    else:
        item['applicant_name'] = None
    for key, name_key in (('hod_id', 'hod_name'), ('hr_id', 'hr_name'), ('admin_id', 'admin_name'), ('reviewed_by', 'reviewed_by_name')):
        ref = item.get(key)
        if ref not in (None, ""):
            ref_user = UserAdmin.objects.filter(id=ref).first()
            item[name_key] = (ref_user.name or (ref_user.first_name + ' ' + ref_user.last_name).strip()) if ref_user else None
        else:
            item[name_key] = None
    if item.get('status') not in (None, ""):
        item['status'] = str(item['status']).upper()
    item['adjacent_lectures'] = _adjacent_lectures_for(item.get('id'))
    return item


def _faculty_display(user_obj):
    if user_obj is None:
        return None
    return user_obj.name or (user_obj.first_name + ' ' + user_obj.last_name).strip()


def _subject_name(subject_id):
    if subject_id in (None, ""):
        return None
    subj = Subject.objects.filter(id=subject_id, isActive=True).first()
    return subj.subject_name if subj is not None else None


def _active_template_ids():
    return list(TimetableTemplate.objects.filter(is_active=True).values_list('id', flat=True))


def _affected_lecture_slots(faculty_id, start_date, end_date):
    if start_date is None or end_date is None or start_date > end_date:
        return []
    template_ids = _active_template_ids()
    if not template_ids:
        return []
    slots = list(TimetableSlot.objects.filter(
        timetable_template_id__in=template_ids,
        faculty_id=str(faculty_id),
        is_active=True
    ))
    rows = []
    one_day = timedelta(days=1)
    cur = start_date
    while cur <= end_date:
        weekday = cur.weekday()
        for s in slots:
            if s.day_of_week == weekday:
                rows.append({
                    'date': cur,
                    'weekday': weekday,
                    'period_number': s.period_number,
                    'start_time': s.start_time,
                    'end_time': s.end_time,
                    'slot_id': s.id,
                    'subject_id': s.course_id,
                })
        cur += one_day
    rows.sort(key=lambda r: (r['date'], r['period_number']))
    return rows


def _faculty_on_leave_on(leave_date):
    return set(str(x.applicant_id) for x in LeaveApplication.objects.filter(
        isActive=True,
        status__in=('PENDING', 'APPROVED'),
        start_date__lte=leave_date,
        end_date__gte=leave_date,
    ))


def _adjacent_candidates(faculty_id, lecture_date, period_number):
    template_ids = _active_template_ids()
    busy = set()
    if template_ids:
        for s in TimetableSlot.objects.filter(
                timetable_template_id__in=template_ids,
                day_of_week=lecture_date.weekday(),
                period_number=period_number,
                is_active=True):
            busy.add(str(s.faculty_id))
    leave_absent = _faculty_on_leave_on(lecture_date)
    already_used = set()
    for row in LeaveAdjacentLecture.objects.filter(
            lecture_date=lecture_date,
            period_number=period_number,
            status__in=('PENDING', 'RESCHEDULED'),
            isActive=True):
        already_used.add(str(row.adjacent_faculty_id))
    candidates = []
    for u in UserAdmin.objects.filter(user_type=5, isActive=True):
        if str(u.id) == str(faculty_id):
            continue
        if str(u.id) in busy or str(u.id) in leave_absent or str(u.id) in already_used:
            continue
        candidates.append({
            'faculty_id': str(u.id),
            'faculty_name': _faculty_display(u),
        })
    candidates.sort(key=lambda c: (c['faculty_name'] or '').lower())
    return candidates


def _adjacent_lectures_for(leave_id):
    if leave_id in (None, ""):
        return []
    result = []
    for row in LeaveAdjacentLecture.objects.filter(leave_application_id=str(leave_id), isActive=True).order_by('lecture_date', 'period_number'):
        adjacent = UserAdmin.objects.filter(id=row.adjacent_faculty_id).first()
        result.append({
            'lecture_date': row.lecture_date,
            'lecture_no': row.period_number,
            'subject_id': row.subject_id,
            'subject_name': _subject_name(row.subject_id),
            'primary_faculty_id': row.primary_faculty_id,
            'adjacent_faculty_id': str(row.adjacent_faculty_id),
            'adjacent_faculty_name': _faculty_display(adjacent),
            'status': str(row.status).upper(),
        })
    return result


def _validate_adjacent_assignments(faculty_id, start_date, end_date, raw_assignments):
    affected = _affected_lecture_slots(faculty_id, start_date, end_date)
    if not affected:
        return [], None
    if not raw_assignments:
        return None, 'Please select an adjacent (substitute) faculty member for every lecture during the leave dates.'
    affected_map = {(r['date'], r['period_number']): r for r in affected}
    parsed = []
    seen = set()
    for assignment in raw_assignments:
        if not isinstance(assignment, dict):
            return None, 'adjacent_assignments must be a list of objects.'
        a_date, err = _parse_date(assignment.get('date'), 'date')
        if err:
            return None, err
        try:
            period = int(assignment.get('lecture_no') if assignment.get('lecture_no') not in (None, '') else assignment.get('period_number'))
        except (TypeError, ValueError):
            return None, 'lecture_no must be a number.'
        adjacent_id = assignment.get('faculty_id') or assignment.get('adjacent_faculty_id')
        if adjacent_id in (None, ""):
            return None, 'adjacent faculty id is required for %s lecture %s.' % (a_date, period)
        key = (a_date, period)
        if key not in affected_map:
            return None, 'No lecture of the applicant on %s with lecture number %s.' % (a_date, period)
        if key in seen:
            return None, 'Duplicate assignment for %s lecture %s.' % (a_date, period)
        adjacent_user = UserAdmin.objects.filter(id=str(adjacent_id), user_type=5, isActive=True).first()
        if adjacent_user is None or str(adjacent_user.id) == str(faculty_id):
            return None, 'Adjacent faculty not found for %s lecture %s.' % (a_date, period)
        free_ids = {c['faculty_id'] for c in _adjacent_candidates(faculty_id, a_date, period)}
        if str(adjacent_user.id) not in free_ids:
            return None, 'Selected adjacent faculty has a lecture or leave at that time (%s lecture %s).' % (a_date, period)
        slot = affected_map[key]
        parsed.append({
            'lecture_date': a_date,
            'period_number': period,
            'subject_id': slot['subject_id'],
            'slot_id': slot['slot_id'],
            'primary_faculty_id': str(faculty_id),
            'adjacent_faculty_id': str(adjacent_user.id),
        })
        seen.add(key)
    missing = [key for key in affected_map if key not in seen]
    if missing:
        lines = '\n'.join('    %s  -  lecture no %s' % (k[0], k[1]) for k in sorted(missing))
        return None, 'Please select an adjacent faculty member for every lecture:\n' + lines
    return parsed, None


def _reschedule_approved_leave(leave_obj):
    rows = LeaveAdjacentLecture.objects.filter(
        leave_application_id=str(leave_obj.id), status='PENDING', isActive=True)
    log = []
    for row in rows:
        slot = TimetableSlot.objects.filter(id=row.slot_id, is_active=True).first() if row.slot_id else None
        template = TimetableTemplate.objects.filter(id=slot.timetable_template_id, is_active=True).first() if slot else None
        if slot is None or template is None:
            continue
        entry = LectureEntry.objects.filter(
            lecture_date=row.lecture_date,
            timetable_slot_id=slot.id,
            faculty_id=row.adjacent_faculty_id,
            isActive=True).first()
        defaults = {
            'academic_year_id': template.academic_year_id,
            'class_group_id': template.class_group_id,
            'course_id': row.subject_id,
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'topic': _subject_name(row.subject_id) or 'Class',
            'lecture_status': 'RESCHEDULED',
            'remarks': 'Substitute for leave #%s (%s)' % (leave_obj.id, row.primary_faculty_id),
            'created_by': str(leave_obj.applicant_id),
        }
        if entry is None:
            LectureEntry.objects.create(
                faculty_id=row.adjacent_faculty_id,
                timetable_slot_id=slot.id,
                lecture_date=row.lecture_date,
                **defaults)
        else:
            for field, value in defaults.items():
                setattr(entry, field, value)
            entry.save()
        row.status = 'RESCHEDULED'
        row.updatedBy = str(leave_obj.applicant_id)
        row.save()
        log.append('moved lecture %s on %s to %s' % (row.period_number, row.lecture_date, row.adjacent_faculty_id))
    return log


class ApplyLeave(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        error, payload = _build_leave_payload(request, request_data, applicant)
        if error:
            return error

        serializer = LeaveApplicationSerializer(data=payload['data'])
        if serializer.is_valid():
            leave_obj = serializer.save()
            for assignment in payload['parsed_adjacent']:
                LeaveAdjacentLecture.objects.create(
                    leave_application_id=str(leave_obj.id),
                    createdBy=str(applicant.id),
                    **assignment)
            item = serializer.data.copy()
            _enrich_leave_item(item)
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave applied successfully.',
                'data': item
            })
        return _error_response(request, 'Leave not applied.', serializer.errors)


class SaveLeave(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        error, payload = _build_leave_payload(request, request_data, applicant)
        if error:
            return error

        serializer = LeaveApplicationSerializer(data=payload['data'])
        if serializer.is_valid():
            leave_obj = serializer.save()
            for assignment in payload['parsed_adjacent']:
                LeaveAdjacentLecture.objects.create(
                    leave_application_id=str(leave_obj.id),
                    createdBy=str(applicant.id),
                    **assignment)
            item = serializer.data.copy()
            _enrich_leave_item(item)
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave saved successfully.',
                'data': item
            })
        return _error_response(request, 'Leave could not be saved.', serializer.errors)


def _build_leave_payload(request, request_data, applicant):
    leave_type = request_data.get('leave_type')
    type_obj = None
    if leave_type not in (None, ""):
        type_obj = LeaveType.objects.filter(leave_type_name__iexact=str(leave_type), isActive=True).first()
        if type_obj is None:
            return _error_response(request, 'leave_type is not in the leave types master.'), None
        leave_type = type_obj.leave_type_name

    start_date, err = _parse_date(request_data.get('start_date') or request_data.get('from_date'), 'start_date')
    if err:
        return _error_response(request, err), None
    end_date, err = _parse_date(request_data.get('end_date') or request_data.get('to_date'), 'end_date')
    if err:
        return _error_response(request, err), None
    reason = request_data.get('reason')
    day_type = (request_data.get('day_type') or 'Full Day').strip()
    if day_type.lower() not in ('half day', 'full day'):
        return _error_response(request, 'day_type must be Half Day or Full Day.'), None
    day_type = 'Half Day' if day_type.lower() == 'half day' else 'Full Day'

    if leave_type in (None, ""):
        return _error_response(request, 'leave_type is required.'), None
    if start_date is None:
        return _error_response(request, 'start_date is required.'), None
    if end_date is None:
        return _error_response(request, 'end_date is required.'), None
    if start_date > end_date:
        return _error_response(request, 'end_date must be on or after start_date.'), None
    if day_type == 'Half Day' and start_date != end_date:
        return _error_response(request, 'Half Day leave must have the same start_date and end_date.'), None
    number_of_days = 0.5 if day_type == 'Half Day' else (end_date - start_date).days + 1
    if number_of_days <= 0:
        return _error_response(request, 'number_of_days must be greater than zero.'), None
    if reason in (None, ""):
        return _error_response(request, 'reason is required.'), None

    application_date, err = _parse_date(request_data.get('application_date'), 'application_date')
    if err:
        return _error_response(request, err), None

    document_url = None
    uploaded_file = request.FILES.get('document') if hasattr(request, 'FILES') else None
    if uploaded_file is not None:
        try:
            document_url = save_file(os.path.join(settings.MEDIA_ROOT, 'leave_documents'), uploaded_file, request)
        except Exception:
            return _error_response(request, 'Document could not be uploaded.'), None

    hod_id = getattr(applicant, 'reporting_to', None)
    if hod_id in (None, ""):
        return _error_response(request, 'No HOD (reporting_to) configured for this user.'), None
    hod_user = UserAdmin.objects.filter(id=hod_id, isActive=True).first()
    if hod_user is None:
        return _error_response(request, 'HOD user (reporting_to) not found.'), None
    hod_id = str(hod_id)

    hr_user = UserAdmin.objects.filter(role_code='hr', isActive=True).order_by('createdAt').first()
    hr_id = str(hr_user.id) if hr_user is not None else None

    admin_user = (UserAdmin.objects.filter(role_code='superadmin', isActive=True).order_by('createdAt').first()
                  or UserAdmin.objects.filter(role_code='admin', isActive=True).order_by('createdAt').first()
                  or UserAdmin.objects.filter(role__in=(1, 2, 3, 4), isActive=True).order_by('createdAt').first())
    admin_id = str(admin_user.id) if admin_user is not None else None

    raw_assignments = request_data.get('adjacent_assignments')
    if raw_assignments in (None, ""):
        raw_assignments = request_data.get('adjacent')
    if isinstance(raw_assignments, str):
        try:
            raw_assignments = json.loads(raw_assignments)
        except Exception:
            return _error_response(request, 'adjacent_assignments must be a valid JSON array.'), None
    if raw_assignments in (None, ""):
        raw_assignments = []
    if not isinstance(raw_assignments, list):
        return _error_response(request, 'adjacent_assignments must be a list.'), None

    parsed_adjacent, adj_err = _validate_adjacent_assignments(str(applicant.id), start_date, end_date, raw_assignments)
    if adj_err:
        return _error_response(request, adj_err), None

    data = {
        'applicant_type': request_data.get('applicant_type') or 'faculty',
        'applicant_id': str(applicant.id),
        'leave_type': leave_type,
        'start_date': start_date,
        'end_date': end_date,
        'number_of_days': number_of_days,
        'reason': reason,
        'day_type': day_type,
        'application_date': application_date,
        'document': document_url,
        'hod_id': hod_id,
        'hr_id': hr_id,
        'admin_id': admin_id,
        'status': 'PENDING',
        'approval_level': 'HOD',
        'hod_status': 'PENDING',
        'hr_status': 'PENDING' if hr_id not in (None, "") else 'NA',
        'createdBy': str(applicant.id),
    }
    return None, {'data': data, 'parsed_adjacent': parsed_adjacent}


class LeaveList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return self._respond(request, request.GET)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        return self._respond(request, request_data)

    def _respond(self, request, request_data):
        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        is_admin = _is_admin_user(applicant)
        qs = LeaveApplication.objects.filter(isActive=True)

        if not is_admin:
            qs = qs.filter(applicant_id=str(applicant.id))
        else:
            applicant_id = request_data.get('applicant_id')
            if applicant_id not in (None, ""):
                qs = qs.filter(applicant_id=applicant_id)
            applicant_type = request_data.get('applicant_type')
            if applicant_type not in (None, ""):
                qs = qs.filter(applicant_type=applicant_type)

        status = request_data.get('status')
        if status not in (None, ""):
            qs = qs.filter(status=str(status).upper())
        leave_type = request_data.get('leave_type')
        if leave_type not in (None, ""):
            qs = qs.filter(leave_type=leave_type)

        result = []
        for item in LeaveApplicationSerializer(qs.order_by('-createdAt'), many=True).data:
            _enrich_leave_item(item)
            result.append(item)
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave list found successfully.',
            'data': result
        })


class LeaveDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        leave_id = request_data.get('id')
        if leave_id in (None, ""):
            return _error_response(request, 'id is required.')

        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        leave_obj = LeaveApplication.objects.filter(id=leave_id, isActive=True).first()
        if leave_obj is None:
            return _error_response(request, 'Leave not found.')

        if not _is_admin_user(applicant) and str(leave_obj.applicant_id) != str(applicant.id):
            return _error_response(request, 'You are not allowed to view this leave.')

        item = LeaveApplicationSerializer(leave_obj).data
        _enrich_leave_item(item)
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave details found successfully.',
            'data': item
        })


class UpdateLeave(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        leave_id = request_data.get('id')
        if leave_id in (None, ""):
            return _error_response(request, 'id is required.')

        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        leave_obj = LeaveApplication.objects.filter(id=leave_id, isActive=True).first()
        if leave_obj is None:
            return _error_response(request, 'Leave not found.')

        is_admin = _is_admin_user(applicant)
        if not is_admin and str(leave_obj.applicant_id) != str(applicant.id):
            return _error_response(request, 'You are not allowed to update this leave.')

        data = {}
        editable_fields = ('leave_type', 'reason', 'applicant_type')
        for field in editable_fields:
            if field in request_data:
                data[field] = request_data.get(field)

        if 'start_date' in request_data:
            start_date, err = _parse_date(request_data.get('start_date'), 'start_date')
            if err:
                return _error_response(request, err)
            data['start_date'] = start_date
        if 'end_date' in request_data:
            end_date, err = _parse_date(request_data.get('end_date'), 'end_date')
            if err:
                return _error_response(request, err)
            data['end_date'] = end_date
        if 'day_type' in request_data:
            day_type = (request_data.get('day_type') or '').strip()
            if day_type.lower() not in ('half day', 'full day'):
                return _error_response(request, 'day_type must be Half Day or Full Day.')
            data['day_type'] = 'Half Day' if day_type.lower() == 'half day' else 'Full Day'

        new_start = data.get('start_date') or leave_obj.start_date
        new_end = data.get('end_date') or leave_obj.end_date
        new_day_type = data.get('day_type') or leave_obj.day_type or 'Full Day'
        if new_start is not None and new_end is not None and new_start > new_end:
            return _error_response(request, 'end_date must be on or after start_date.')
        if new_start is not None and new_end is not None:
            data['number_of_days'] = 0.5 if str(new_day_type).lower() == 'half day' else (new_end - new_start).days + 1

        parsed_adjacent = None
        pending_count = LeaveAdjacentLecture.objects.filter(
            leave_application_id=str(leave_obj.id), status='PENDING', isActive=True).count()
        if str(leave_obj.status).upper() == 'PENDING':
            raw_assignments = request_data.get('adjacent_assignments')
            if raw_assignments in (None, ""):
                raw_assignments = request_data.get('adjacent')
            if isinstance(raw_assignments, str):
                try:
                    raw_assignments = json.loads(raw_assignments)
                except Exception:
                    return _error_response(request, 'adjacent_assignments must be a valid JSON array.')
            if raw_assignments in (None, ""):
                raw_assignments = []
            if not isinstance(raw_assignments, list):
                return _error_response(request, 'adjacent_assignments must be a list.')
            affected_slots = _affected_lecture_slots(str(leave_obj.applicant_id), new_start, new_end)
            if raw_assignments:
                parsed_adjacent, adj_err = _validate_adjacent_assignments(str(leave_obj.applicant_id), new_start, new_end, raw_assignments)
                if adj_err:
                    return _error_response(request, adj_err)
            elif affected_slots and pending_count == 0:
                return _error_response(request, 'Please provide adjacent_assignments covering every lecture in the leave date range.')

        serializer = LeaveApplicationSerializer(leave_obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if parsed_adjacent is not None:
                LeaveAdjacentLecture.objects.filter(leave_application_id=str(leave_obj.id), status='PENDING').update(isActive=False)
                for assignment in parsed_adjacent:
                    LeaveAdjacentLecture.objects.create(
                        leave_application_id=str(leave_obj.id),
                        createdBy=str(applicant.id),
                        **assignment)
            item = serializer.data.copy()
            _enrich_leave_item(item)
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave updated successfully.',
                'data': item
            })
        return _error_response(request, 'Leave not updated.', serializer.errors)


class DeleteLeave(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        leave_id = request_data.get('id')
        if leave_id in (None, ""):
            return _error_response(request, 'id is required.')

        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        leave_obj = LeaveApplication.objects.filter(id=leave_id, isActive=True).first()
        if leave_obj is None:
            return _error_response(request, 'Leave not found.')

        is_admin = _is_admin_user(applicant)
        if not is_admin and str(leave_obj.applicant_id) != str(applicant.id):
            return _error_response(request, 'You are not allowed to delete this leave.')

        leave_obj.isActive = False
        leave_obj.save()
        LeaveAdjacentLecture.objects.filter(leave_application_id=str(leave_id)).update(isActive=False)
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave deleted successfully.',
            'data': {}
        })


class ReviewLeave(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        leave_id = request_data.get('id')
        if leave_id in (None, ""):
            return _error_response(request, 'id is required.')

        reviewer = _requesting_admin(request)
        if reviewer is None:
            return _error_response(request, 'logged in user not found')

        leave_obj = LeaveApplication.objects.filter(id=leave_id, isActive=True).first()
        if leave_obj is None:
            return _error_response(request, 'Leave not found.')

        if str(leave_obj.applicant_id) == str(reviewer.id):
            return _error_response(request, 'You cannot review your own leave.')

        if str(leave_obj.status).upper() != 'PENDING':
            return _error_response(request, 'Only pending leaves can be reviewed.')

        level = (request_data.get('level') or 'HOD').strip().upper()
        if level not in ('HOD', 'HR'):
            return _error_response(request, 'level must be HOD or HR.')
        if level == 'HR' and str(leave_obj.approval_level).upper() != 'HR':
            return _error_response(request, 'Leave has not reached HR yet.')

        new_status = str(request_data.get('status') or '').strip().upper()
        if new_status not in ('APPROVED', 'REJECTED'):
            return _error_response(request, 'status must be APPROVED or REJECTED.')

        required_approver = leave_obj.hr_id if level == 'HR' else leave_obj.hod_id
        is_admin = _is_admin_user(reviewer)
        if not is_admin and (required_approver in (None, "") or str(required_approver) != str(reviewer.id)):
            return _error_response(request, 'You are not the assigned %s for this leave.' % level)

        review_remarks = request_data.get('review_remarks')
        leave_obj.reviewed_by = str(reviewer.id)
        leave_obj.reviewed_at = timezone.now()
        leave_obj.review_remarks = review_remarks
        leave_obj.updatedBy = str(reviewer.id)

        if level == 'HOD':
            leave_obj.hod_status = new_status
            if new_status == 'APPROVED':
                if leave_obj.hr_id not in (None, ""):
                    leave_obj.approval_level = 'HR'
                    leave_obj.status = 'PENDING'
                else:
                    leave_obj.approval_level = 'APPROVED'
                    leave_obj.status = 'APPROVED'
            else:
                leave_obj.approval_level = new_status
                leave_obj.status = new_status
        else:
            leave_obj.hr_status = new_status
            if new_status == 'APPROVED':
                leave_obj.approval_level = 'APPROVED'
                leave_obj.status = 'APPROVED'
            else:
                leave_obj.approval_level = new_status
                leave_obj.status = new_status
        leave_obj.save()

        if str(leave_obj.status).upper() == 'APPROVED':
            _reschedule_approved_leave(leave_obj)

        item = LeaveApplicationSerializer(leave_obj).data
        _enrich_leave_item(item)

        if new_status == 'REJECTED':
            message = 'Leave rejected by %s.' % level
        elif level == 'HOD':
            message = 'Leave approved by HOD%s.' % (' , pending HR approval' if str(leave_obj.status).upper() == 'PENDING' else '')
        else:
            message = 'Leave approved successfully.'
        return _final_response(request, {
            "n": 1,
            'msg': message,
            'data': item
        })


class LeaveTimetable(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')

        leave_id = request_data.get('leave_id')
        faculty_id = request_data.get('faculty_id')
        applied_store = {}

        if leave_id not in (None, ""):
            leave_obj = LeaveApplication.objects.filter(id=leave_id, isActive=True).first()
            if leave_obj is None:
                return _error_response(request, 'Leave not found.')
            if not _is_admin_user(user) and str(leave_obj.applicant_id) != str(user.id):
                return _error_response(request, 'You are not allowed to view this leave.')
            faculty_id = str(leave_obj.applicant_id)
            start_date, end_date = leave_obj.start_date, leave_obj.end_date
            for row in LeaveAdjacentLecture.objects.filter(leave_application_id=str(leave_id), isActive=True):
                applied_store[(row.lecture_date, row.period_number)] = str(row.adjacent_faculty_id)
        else:
            if request_data.get('start_date') in (None, ""):
                return _error_response(request, 'start_date is required (or pass leave_id).')
            start_date, err = _parse_date(request_data.get('start_date'), 'start_date')
            if err:
                return _error_response(request, err)
            end_date, err = _parse_date(request_data.get('end_date') or request_data.get('start_date'), 'end_date')
            if err:
                return _error_response(request, err)
            if start_date > end_date:
                return _error_response(request, 'end_date must be on or after start_date.')
            if (end_date - start_date).days > 31:
                return _error_response(request, 'Date range is too large (maximum 31 days).')
            if faculty_id in (None, ""):
                faculty_id = str(user.id)

        if faculty_id in (None, ""):
            return _error_response(request, 'Could not determine the faculty.')

        faculty_user = UserAdmin.objects.filter(id=faculty_id, isActive=True).first()
        if faculty_user is None:
            return _error_response(request, 'Faculty not found.')

        result = []
        for slot in _affected_lecture_slots(faculty_id, start_date, end_date):
            result.append({
                'date': slot['date'],
                'lecture_no': slot['period_number'],
                'start_time': slot['start_time'],
                'end_time': slot['end_time'],
                'subject_id': slot['subject_id'],
                'subject_name': _subject_name(slot['subject_id']),
                'faculty_id': str(faculty_id),
                'faculty_name': _faculty_display(faculty_user),
                'adjacent_candidates': _adjacent_candidates(faculty_id, slot['date'], slot['period_number']),
                'selected_adjacent_faculty_id': applied_store.get((slot['date'], slot['period_number'])),
            })
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave timetable found successfully.',
            'data': result
        })


class FacultyTimetable(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')

        start_date, err = _parse_date(request_data.get('start_date') or request_data.get('from_date'), 'start_date')
        if err or start_date is None:
            return _error_response(request, 'start_date is required (YYYY-MM-DD).')
        end_date, err = _parse_date(request_data.get('end_date') or request_data.get('to_date') or request_data.get('start_date'), 'end_date')
        if err:
            return _error_response(request, err)
        if start_date > end_date:
            return _error_response(request, 'end_date must be on or after start_date.')
        if (end_date - start_date).days > 31:
            return _error_response(request, 'Date range is too large (maximum 31 days).')

        faculty_id = request_data.get('faculty_id') or str(user.id)
        if faculty_id in (None, ""):
            return _error_response(request, 'Could not determine the faculty.')
        faculty_user = UserAdmin.objects.filter(id=faculty_id, isActive=True).first()
        if faculty_user is None:
            return _error_response(request, 'Faculty not found.')

        rows_map = {}
        for slot in _affected_lecture_slots(faculty_id, start_date, end_date):
            key = (slot['date'], slot['period_number'])
            rows_map[key] = {
                'date': slot['date'],
                'lecture_no': slot['period_number'],
                'start_time': slot['start_time'],
                'end_time': slot['end_time'],
                'subject_id': slot['subject_id'],
                'subject_name': _subject_name(slot['subject_id']),
                'faculty_id': str(faculty_id),
                'faculty_name': _faculty_display(faculty_user),
                'status': 'SCHEDULED',
                'assigned_faculty_id': str(faculty_id),
                'assigned_faculty_name': _faculty_display(faculty_user),
                'original_faculty_id': None,
                'original_faculty_name': None,
                'leave_id': None,
            }

        for row in LeaveAdjacentLecture.objects.filter(
                primary_faculty_id=str(faculty_id),
                lecture_date__gte=start_date, lecture_date__lte=end_date,
                status='RESCHEDULED', isActive=True):
            key = (row.lecture_date, row.period_number)
            adjacent = UserAdmin.objects.filter(id=row.adjacent_faculty_id).first()
            existing = rows_map.get(key)
            if existing is not None:
                existing['status'] = 'REASSIGNED'
                existing['assigned_faculty_id'] = str(row.adjacent_faculty_id)
                existing['assigned_faculty_name'] = _faculty_display(adjacent)
                existing['leave_id'] = row.leave_application_id
            else:
                rows_map[key] = {
                    'date': row.lecture_date,
                    'lecture_no': row.period_number,
                    'start_time': None,
                    'end_time': None,
                    'subject_id': row.subject_id,
                    'subject_name': _subject_name(row.subject_id),
                    'faculty_id': str(faculty_id),
                    'faculty_name': _faculty_display(faculty_user),
                    'status': 'REASSIGNED',
                    'assigned_faculty_id': str(row.adjacent_faculty_id),
                    'assigned_faculty_name': _faculty_display(adjacent),
                    'original_faculty_id': str(faculty_id),
                    'original_faculty_name': _faculty_display(faculty_user),
                    'leave_id': row.leave_application_id,
                }

        for entry in LectureEntry.objects.filter(
                faculty_id=str(faculty_id),
                lecture_date__gte=start_date, lecture_date__lte=end_date,
                lecture_status='RESCHEDULED', isActive=True):
            key = (entry.lecture_date, entry.timetable_slot_id)
            leave_match = None
            if entry.remarks:
                leave_match = entry.remarks.split(' ')[-2] if str(entry.remarks).startswith('Substitute for leave #') else None
            period = None
            slot_obj = TimetableSlot.objects.filter(id=entry.timetable_slot_id).first() if entry.timetable_slot_id else None
            if slot_obj is not None:
                period = slot_obj.period_number
            row_key = (entry.lecture_date, period) if period is not None else None
            if row_key is None:
                continue
            existing = rows_map.get(row_key)
            if existing is not None:
                existing['status'] = 'RESCHEDULED'
                existing['faculty_id'] = str(faculty_id)
                existing['faculty_name'] = _faculty_display(faculty_user)
                existing['assigned_faculty_id'] = str(faculty_id)
                existing['assigned_faculty_name'] = _faculty_display(faculty_user)
                existing['subject_id'] = entry.course_id
                existing['subject_name'] = _subject_name(entry.course_id)
                existing['start_time'] = entry.start_time
                existing['end_time'] = entry.end_time
                existing['original_faculty_id'] = None
                existing['original_faculty_name'] = None
                existing['leave_id'] = entry.leave_id if hasattr(entry, 'leave_id') else leave_match
            else:
                rows_map[row_key] = {
                    'date': entry.lecture_date,
                    'lecture_no': period,
                    'start_time': entry.start_time,
                    'end_time': entry.end_time,
                    'subject_id': entry.course_id,
                    'subject_name': _subject_name(entry.course_id),
                    'faculty_id': str(faculty_id),
                    'faculty_name': _faculty_display(faculty_user),
                    'status': 'RESCHEDULED',
                    'assigned_faculty_id': str(faculty_id),
                    'assigned_faculty_name': _faculty_display(faculty_user),
                    'original_faculty_id': None,
                    'original_faculty_name': None,
                    'leave_id': leave_match,
                }

        result = []
        sr_no = 1
        for key in sorted(rows_map.keys()):
            item = rows_map[key]
            item['sr_no'] = sr_no
            sr_no += 1
            result.append(item)
        return _final_response(request, {
            "n": 1,
            'msg': 'Faculty timetable found successfully.',
            'data': result
        })


WORK_START = time(9, 30)
WORK_END = time(18, 30)
LATE_THRESHOLD = time(10, 30)
EARLY_THRESHOLD = time(17, 30)


def _designation_name(designation_id):
    if designation_id in (None, ""):
        return ""
    desig = Designation.objects.filter(id=designation_id).first()
    return desig.role_name if desig is not None else ""


def _faculty_profile(faculty_id):
    u = UserAdmin.objects.filter(id=faculty_id, isActive=True).first()
    if u is None:
        return None
    return {
        'faculty_id': str(u.id),
        'name': _faculty_display(u),
        'email': u.email or '',
        'employee_code': u.employee_code or '',
        'designation_id': u.designation,
        'designation': _designation_name(u.designation),
    }


def _approved_leave_on(faculty_id, d):
    return LeaveApplication.objects.filter(
        applicant_id=str(faculty_id), isActive=True, status='APPROVED',
        start_date__lte=d, end_date__gte=d).exists()


def _is_holiday(d):
    return AttendanceHoliday.objects.filter(holiday_date=d, isActive=True).exists()


def _parse_clock(value, field_name, base_date):
    if value in (None, ""):
        return None, None
    raw = str(value).strip()
    try:
        parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            parsed = timezone.make_aware(parsed)
        return parsed, None
    except ValueError:
        pass
    try:
        parsed_time = datetime.strptime(raw, '%H:%M').time()
    except ValueError:
        return None, '%s must be HH:MM or ISO datetime.' % field_name
    combined = datetime.combine(base_date, parsed_time)
    if timezone.is_naive(combined):
        combined = timezone.make_aware(combined)
    return combined, None


def _facility_day_status(faculty_id, d):
    base = {
        'date': d,
        'day_name': d.strftime('%A'),
        'week_day': d.weekday(),
        'check_in': None,
        'check_out': None,
        'total_hours': None,
        'is_late': False,
        'is_early': False,
        'remarks': '',
    }
    if _approved_leave_on(faculty_id, d):
        base['status'] = 'LEAVE'
        base['remarks'] = 'Approved leave'
        return base
    fa = FacultyAttendance.objects.filter(faculty_id=str(faculty_id), attendance_date=d, isActive=True).first()
    if fa is not None and (fa.check_in is not None or fa.check_out is not None):
        late = fa.check_in is not None and fa.check_in.time() > LATE_THRESHOLD
        early = fa.check_out is not None and fa.check_out.time() < EARLY_THRESHOLD
        if late and early:
            status = 'LATE_EARLY'
        elif late:
            status = 'LATE'
        elif early:
            status = 'EARLY'
        else:
            status = 'PRESENT'
        base.update({
            'status': status,
            'check_in': fa.check_in,
            'check_out': fa.check_out,
            'total_hours': float(fa.total_hours) if fa.total_hours is not None else None,
            'is_late': late,
            'is_early': early,
            'remarks': fa.remarks or '',
        })
        return base
    if d.weekday() >= 5:
        base['status'] = 'WEEKLY_OFF'
        base['remarks'] = 'Weekly off'
        return base
    if _is_holiday(d):
        base['status'] = 'HOLIDAY'
        base['remarks'] = 'Holiday'
        return base
    base['status'] = 'ABSENT'
    base['remarks'] = 'No attendance entry'
    return base


class MarkFacultyAttendance(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')

        faculty_id = request_data.get('faculty_id') or str(user.id)
        if faculty_id in (None, ""):
            return _error_response(request, 'Could not determine the faculty.')
        if str(faculty_id) != str(user.id) and not _is_admin_user(user):
            return _error_response(request, 'You are only allowed to mark your own attendance.')

        faculty_user = UserAdmin.objects.filter(id=faculty_id, isActive=True).first()
        if faculty_user is None:
            return _error_response(request, 'Faculty not found.')

        attendance_date, err = _parse_date(request_data.get('attendance_date') or request_data.get('date'), 'attendance_date')
        if err:
            return _error_response(request, err)
        if attendance_date is None:
            attendance_date = timezone.localdate()

        today = timezone.localdate()
        if attendance_date > today:
            return _error_response(request, 'Attendance cannot be marked for a future date.')

        if _approved_leave_on(faculty_id, attendance_date):
            return _error_response(request, 'Faculty is on approved leave on this date (check-in/check-out not applicable).')
        if attendance_date.weekday() >= 5:
            return _error_response(request, 'Cannot mark attendance on a weekly off day.')
        if _is_holiday(attendance_date):
            return _error_response(request, 'Cannot mark attendance on a holiday.')

        check_in, err = _parse_clock(request_data.get('check_in'), 'check_in', attendance_date)
        if err:
            return _error_response(request, err)
        check_out, err = _parse_clock(request_data.get('check_out'), 'check_out', attendance_date)
        if err:
            return _error_response(request, err)
        if check_in is None and check_out is None:
            return _error_response(request, 'Provide check_in and/or check_out.')

        if check_in is not None and check_out is not None:
            if check_out < check_in:
                return _error_response(request, 'Check-out cannot be before check-in.')

        fa, _ = FacultyAttendance.objects.get_or_create(
            faculty_id=str(faculty_id),
            attendance_date=attendance_date,
            defaults={'createdBy': str(user.id), 'isActive': True})
        fa.updatedBy = str(user.id)
        fa.updatedAt = timezone.now()
        if check_in is not None:
            fa.check_in = check_in
        if check_out is not None:
            fa.check_out = check_out

        late = fa.check_in is not None and fa.check_in.time() > LATE_THRESHOLD
        early = fa.check_out is not None and fa.check_out.time() < EARLY_THRESHOLD
        if fa.check_in is not None and fa.check_out is not None:
            fa.total_hours = round((fa.check_out - fa.check_in).total_seconds() / 3600.0, 2)
        fa.is_late = late
        fa.is_early = early
        if late and early:
            fa.day_status = 'LATE_EARLY'
        elif late:
            fa.day_status = 'LATE'
        elif early:
            fa.day_status = 'EARLY'
        elif fa.check_in is not None or fa.check_out is not None:
            fa.day_status = 'PRESENT'
        fa.save()

        item = {
            'faculty': _faculty_profile(faculty_id),
            'attendance_date': fa.attendance_date,
            'day_name': fa.attendance_date.strftime('%A'),
            'check_in': fa.check_in,
            'check_out': fa.check_out,
            'total_hours': float(fa.total_hours) if fa.total_hours is not None else None,
            'day_status': fa.day_status,
            'is_late': fa.is_late,
            'is_early': fa.is_early,
            'remarks': fa.remarks or '',
        }
        return _final_response(request, {
            "n": 1,
            'msg': 'Attendance marked successfully.',
            'data': item
        })


class FacultyDailyAttendance(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')

        faculty_id = request_data.get('faculty_id') or str(user.id)
        if faculty_id in (None, ""):
            return _error_response(request, 'Could not determine the faculty.')

        start_date, err = _parse_date(request_data.get('start_date') or request_data.get('from_date'), 'start_date')
        if err or start_date is None:
            return _error_response(request, 'start_date is required (YYYY-MM-DD).')
        end_date, err = _parse_date(request_data.get('end_date') or request_data.get('to_date') or request_data.get('start_date'), 'end_date')
        if err:
            return _error_response(request, err)
        if start_date > end_date:
            return _error_response(request, 'end_date must be on or after start_date.')
        if (end_date - start_date).days + 1 > 90:
            return _error_response(request, 'Date range is too large (maximum 90 days).')

        faculty_user = UserAdmin.objects.filter(id=faculty_id, isActive=True).first()
        if faculty_user is None:
            return _error_response(request, 'Faculty not found.')

        rows = []
        d = start_date
        while d <= end_date:
            rows.append(_facility_day_status(faculty_id, d))
            d += timedelta(days=1)
        return _final_response(request, {
            "n": 1,
            'msg': 'Faculty attendance found successfully.',
            'data': {
                'faculty': _faculty_profile(faculty_id),
                'rows': rows,
            }
        })


class FacultyAttendanceSummary(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response

        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')

        faculty_id = request_data.get('faculty_id') or str(user.id)
        if faculty_id in (None, ""):
            return _error_response(request, 'Could not determine the faculty.')

        start_date, err = _parse_date(request_data.get('start_date'), 'start_date')
        if err:
            return _error_response(request, err)
        end_date, err = _parse_date(request_data.get('end_date'), 'end_date')
        if err:
            return _error_response(request, err)
        month = request_data.get('month') or request_data.get('month_year')
        if start_date is None and month in (None, ""):
            today = timezone.localdate()
            start_date = today.replace(day=1)
            end_date = today
        elif start_date is not None and end_date is None:
            end_date = start_date
        elif start_date is None and month not in (None, ""):
            try:
                m = datetime.strptime(str(month), '%Y-%m').date()
                start_date = m.replace(day=1)
                next_month = (m.replace(day=28) + timedelta(days=4)).replace(day=1)
                end_date = next_month - timedelta(days=1)
            except ValueError:
                return _error_response(request, 'month must be YYYY-MM.')
        if end_date is None:
            end_date = start_date
        if start_date > end_date:
            return _error_response(request, 'end_date must be on or after start_date.')
        if (end_date - start_date).days + 1 > 90:
            return _error_response(request, 'Date range is too large (maximum 90 days).')

        faculty_user = UserAdmin.objects.filter(id=faculty_id, isActive=True).first()
        if faculty_user is None:
            return _error_response(request, 'Faculty not found.')

        summary_counts = {}
        total_attended_hours_seconds = 0
        attended_days = 0
        d = start_date
        while d <= end_date:
            status = _facility_day_status(faculty_id, d)['status']
            summary_counts[status] = summary_counts.get(status, 0) + 1
            fa = FacultyAttendance.objects.filter(faculty_id=str(faculty_id), attendance_date=d, isActive=True).first()
            if fa is not None and fa.total_hours is not None and status in ('PRESENT', 'LATE', 'EARLY', 'LATE_EARLY'):
                total_attended_hours_seconds += float(fa.total_hours)
                attended_days += 1
            d += timedelta(days=1)

        late_marks = summary_counts.get('LATE', 0) + summary_counts.get('LATE_EARLY', 0)
        early_marks = summary_counts.get('EARLY', 0) + summary_counts.get('LATE_EARLY', 0)

        eat = late_marks
        deduction_days = 0.0
        while eat >= 6:
            deduction_days += 1.0
            eat -= 6
        while eat >= 3:
            deduction_days += 0.5
            eat -= 3

        avg_daily_hours = round(total_attended_hours_seconds / attended_days, 2) if attended_days else 0

        return _final_response(request, {
            "n": 1,
            'msg': 'Faculty attendance summary found successfully.',
            'data': {
                'faculty': _faculty_profile(faculty_id),
                'start_date': start_date,
                'end_date': end_date,
                'total_days': (end_date - start_date).days + 1,
                'present_days': summary_counts.get('PRESENT', 0),
                'late_days': summary_counts.get('LATE', 0),
                'early_days': summary_counts.get('EARLY', 0),
                'late_early_days': summary_counts.get('LATE_EARLY', 0),
                'leave_days': summary_counts.get('LEAVE', 0),
                'weekly_off_days': summary_counts.get('WEEKLY_OFF', 0),
                'holiday_days': summary_counts.get('HOLIDAY', 0),
                'absent_days': summary_counts.get('ABSENT', 0),
                'late_marks': late_marks,
                'early_marks': early_marks,
                'avg_daily_hours': avg_daily_hours,
                'late_deduction_days': deduction_days,
            }
        })


class AddHoliday(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')
        if not _is_admin_user(user):
            return _error_response(request, 'Admin access required.')
        holiday_date, err = _parse_date(request_data.get('holiday_date'), 'holiday_date')
        if err or holiday_date is None:
            return _error_response(request, 'holiday_date is required (YYYY-MM-DD).')
        name = request_data.get('name')
        if name in (None, ""):
            return _error_response(request, 'name is required.')
        obj, created = AttendanceHoliday.objects.get_or_create(
            holiday_date=holiday_date,
            defaults={'name': name, 'createdBy': str(user.id), 'isActive': True})
        if not created:
            obj.name = name
            obj.isActive = True
            obj.updatedBy = str(user.id)
            obj.updatedAt = timezone.now()
            obj.save()
        return _final_response(request, {
            "n": 1,
            'msg': 'Holiday saved successfully.',
            'data': {
                'id': obj.id,
                'holiday_date': obj.holiday_date,
                'name': obj.name,
            }
        })


class HolidayList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        holidays = AttendanceHoliday.objects.filter(isActive=True).order_by('holiday_date')
        data = [{'id': h.id, 'holiday_date': h.holiday_date, 'name': h.name} for h in holidays]
        return _final_response(request, {
            "n": 1,
            'msg': 'Holidays found successfully.',
            'data': data
        })


class DeleteHoliday(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        user = _requesting_admin(request)
        if user is None:
            return _error_response(request, 'logged in user not found')
        if not _is_admin_user(user):
            return _error_response(request, 'Admin access required.')
        holiday_obj = AttendanceHoliday.objects.filter(id=request_data.get('id'), isActive=True).first()
        if holiday_obj is None:
            return _error_response(request, 'Holiday not found.')
        holiday_obj.isActive = False
        holiday_obj.updatedBy = str(user.id)
        holiday_obj.updatedAt = timezone.now()
        holiday_obj.save()
        return _final_response(request, {
            "n": 1,
            'msg': 'Holiday deleted successfully.',
            'data': {'id': holiday_obj.id, 'holiday_date': holiday_obj.holiday_date, 'name': holiday_obj.name}
        })


class MarkCandidateAttendance(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
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


def _require_admin(request, message='You are not allowed to perform this action.'):
    applicant = _requesting_admin(request)
    if applicant is None:
        return None, None, _error_response(request, 'logged in user not found')
    if not _is_admin_user(applicant):
        return None, None, _error_response(request, message)
    return applicant, None, None


def _enrich_allotment_item(item):
    leave_type_id = item.get('leave_type_id')
    ltype = LeaveType.objects.filter(id=leave_type_id).first()
    item['leave_type_name'] = ltype.leave_type_name if ltype else None

    designation_id = item.get('designation_id')
    des = Designation.objects.filter(id=designation_id).first()
    item['designation_name'] = des.role_name if des else None

    academic_year_id = item.get('academic_year_id')
    year = AcademicYear.objects.filter(id=academic_year_id).first()
    item['academic_year_name'] = year.academic_year_name if year else None
    return item


class AddLeaveType(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        admin, _, err = _require_admin(request)
        if err:
            return err

        leave_type_name = (request_data.get('leave_type_name') or '').strip()
        if leave_type_name == "":
            return _error_response(request, 'leave_type_name is required.')
        if LeaveType.objects.filter(leave_type_name__iexact=leave_type_name).exists():
            return _error_response(request, 'Leave type already exists.')

        data = {
            'leave_type_name': leave_type_name,
            'units': request_data.get('units') or 'Days',
            'description': request_data.get('description'),
            'createdBy': str(admin.id),
        }
        serializer = LeaveTypeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave type added successfully.',
                'data': serializer.data
            })
        return _error_response(request, 'Leave type not added.', serializer.errors)


class LeaveTypeList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return self._respond(request, request.GET)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        return self._respond(request, request_data)

    def _respond(self, request, request_data):
        if _requesting_admin(request) is None:
            return _error_response(request, 'logged in user not found')
        qs = LeaveType.objects.filter(isActive=True)
        show_inactive = request_data.get('show_inactive')
        if str(show_inactive).lower() in ('1', 'true'):
            qs = LeaveType.objects.all()
        result = LeaveTypeSerializer(qs.order_by('id'), many=True).data
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave type list found successfully.',
            'data': result
        })


class UpdateLeaveType(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        admin, _, err = _require_admin(request)
        if err:
            return err

        type_id = request_data.get('id')
        if type_id in (None, ""):
            return _error_response(request, 'id is required.')
        type_obj = LeaveType.objects.filter(id=type_id, isActive=True).first()
        if type_obj is None:
            return _error_response(request, 'Leave type not found.')

        data = {}
        if 'leave_type_name' in request_data:
            new_name = (request_data.get('leave_type_name') or '').strip()
            if new_name == "":
                return _error_response(request, 'leave_type_name cannot be empty.')
            if LeaveType.objects.filter(leave_type_name__iexact=new_name).exclude(id=type_obj.id).exists():
                return _error_response(request, 'Leave type already exists.')
            data['leave_type_name'] = new_name
        if 'units' in request_data:
            data['units'] = request_data.get('units') or 'Days'
        if 'description' in request_data:
            data['description'] = request_data.get('description')
        if 'isActive' in request_data:
            data['isActive'] = True if str(request_data.get('isActive')).lower() in ('1', 'true') else False

        serializer = LeaveTypeSerializer(type_obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave type updated successfully.',
                'data': serializer.data
            })
        return _error_response(request, 'Leave type not updated.', serializer.errors)


class DeleteLeaveType(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        admin, _, err = _require_admin(request)
        if err:
            return err

        type_id = request_data.get('id')
        if type_id in (None, ""):
            return _error_response(request, 'id is required.')
        type_obj = LeaveType.objects.filter(id=type_id, isActive=True).first()
        if type_obj is None:
            return _error_response(request, 'Leave type not found.')
        type_obj.isActive = False
        type_obj.save()
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave type deleted successfully.',
            'data': {}
        })


class AddLeaveAllotment(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        admin, _, err = _require_admin(request)
        if err:
            return err

        leave_type_id = request_data.get('leave_type_id')
        designation_id = request_data.get('designation_id')
        academic_year_id = request_data.get('academic_year_id')
        if leave_type_id in (None, ""):
            return _error_response(request, 'leave_type_id is required.')
        if designation_id in (None, ""):
            return _error_response(request, 'designation_id is required.')
        if academic_year_id in (None, ""):
            return _error_response(request, 'academic_year_id is required.')

        if LeaveType.objects.filter(id=leave_type_id, isActive=True).count() == 0:
            return _error_response(request, 'Leave type not found.')
        if Designation.objects.filter(id=designation_id).count() == 0:
            return _error_response(request, 'Designation not found.')
        if AcademicYear.objects.filter(id=academic_year_id).count() == 0:
            return _error_response(request, 'Academic year not found.')
        if LeaveTypeAllotment.objects.filter(
                leave_type_id=leave_type_id, designation_id=designation_id,
                academic_year_id=academic_year_id).exists():
            return _error_response(request, 'Allotment already exists for this type, designation and academic year.')

        try:
            allowed = float(request_data.get('allowed') or 0)
            opening = float(request_data.get('opening_balance') or 0)
        except (TypeError, ValueError):
            return _error_response(request, 'allowed and opening_balance must be numbers.')

        serializer = LeaveTypeAllotmentSerializer(data={
            'leave_type_id': leave_type_id,
            'designation_id': designation_id,
            'academic_year_id': academic_year_id,
            'allowed': allowed,
            'opening_balance': opening,
            'createdBy': str(admin.id),
        })
        if serializer.is_valid():
            serializer.save()
            item = serializer.data.copy()
            _enrich_allotment_item(item)
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave allotment added successfully.',
                'data': item
            })
        return _error_response(request, 'Leave allotment not added.', serializer.errors)


class LeaveAllotmentList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return self._respond(request, request.GET)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        return self._respond(request, request_data)

    def _respond(self, request, request_data):
        if _requesting_admin(request) is None:
            return _error_response(request, 'logged in user not found')
        qs = LeaveTypeAllotment.objects.filter(isActive=True)
        designation_id = request_data.get('designation_id')
        if designation_id not in (None, ""):
            qs = qs.filter(designation_id=designation_id)
        academic_year_id = request_data.get('academic_year_id')
        if academic_year_id not in (None, ""):
            qs = qs.filter(academic_year_id=academic_year_id)
        leave_type_id = request_data.get('leave_type_id')
        if leave_type_id not in (None, ""):
            qs = qs.filter(leave_type_id=leave_type_id)

        result = []
        for item in LeaveTypeAllotmentSerializer(qs.order_by('designation_id', 'academic_year_id', 'id'), many=True).data:
            _enrich_allotment_item(item)
            result.append(item)
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave allotment list found successfully.',
            'data': result
        })


class UpdateLeaveAllotment(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        admin, _, err = _require_admin(request)
        if err:
            return err

        allot_id = request_data.get('id')
        if allot_id in (None, ""):
            return _error_response(request, 'id is required.')
        allot_obj = LeaveTypeAllotment.objects.filter(id=allot_id, isActive=True).first()
        if allot_obj is None:
            return _error_response(request, 'Leave allotment not found.')

        data = {}
        for field, checker in (('leave_type_id', LeaveType), ('designation_id', Designation), ('academic_year_id', AcademicYear)):
            if field in request_data and request_data.get(field) not in (None, ""):
                if checker.objects.filter(id=request_data.get(field)).count() == 0:
                    return _error_response(request, '%s not found.' % field)
                data[field] = request_data.get(field)
        for field in ('allowed', 'opening_balance'):
            if field in request_data and request_data.get(field) not in (None, ""):
                try:
                    data[field] = float(request_data.get(field))
                except (TypeError, ValueError):
                    return _error_response(request, '%s must be a number.' % field)
        if 'isActive' in request_data:
            data['isActive'] = True if str(request_data.get('isActive')).lower() in ('1', 'true') else False

        dup = LeaveTypeAllotment.objects.filter(
            leave_type_id=data.get('leave_type_id', allot_obj.leave_type_id),
            designation_id=data.get('designation_id', allot_obj.designation_id),
            academic_year_id=data.get('academic_year_id', allot_obj.academic_year_id),
        ).exclude(id=allot_obj.id)
        if dup.exists():
            return _error_response(request, 'Allotment already exists for this type, designation and academic year.')

        serializer = LeaveTypeAllotmentSerializer(allot_obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            item = serializer.data.copy()
            _enrich_allotment_item(item)
            return _final_response(request, {
                "n": 1,
                'msg': 'Leave allotment updated successfully.',
                'data': item
            })
        return _error_response(request, 'Leave allotment not updated.', serializer.errors)


class DeleteLeaveAllotment(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        admin, _, err = _require_admin(request)
        if err:
            return err

        allot_id = request_data.get('id')
        if allot_id in (None, ""):
            return _error_response(request, 'id is required.')
        allot_obj = LeaveTypeAllotment.objects.filter(id=allot_id, isActive=True).first()
        if allot_obj is None:
            return _error_response(request, 'Leave allotment not found.')
        allot_obj.isActive = False
        allot_obj.save()
        return _final_response(request, {
            "n": 1,
            'msg': 'Leave allotment deleted successfully.',
            'data': {}
        })


class MyLeaveBalance(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        applicant = _requesting_admin(request)
        if applicant is None:
            return _error_response(request, 'logged in user not found')

        designation_id = request_data.get('designation_id') or getattr(applicant, 'designation', None)
        if designation_id in (None, ""):
            return _error_response(request, 'Designation is not set for the logged in user. Please set the user designation or pass designation_id.')

        academic_year_id = request_data.get('academic_year_id')
        if academic_year_id in (None, ""):
            year = AcademicYear.objects.filter(is_current=True).first() or AcademicYear.objects.order_by('-id').first()
            academic_year_id = year.id if year else None
        if academic_year_id is None:
            return _error_response(request, 'No academic year found.')

        year = AcademicYear.objects.filter(id=academic_year_id).first()
        if year is None:
            return _error_response(request, 'Academic year not found.')
        if Designation.objects.filter(id=designation_id).count() == 0:
            return _error_response(request, 'Designation not found.')

        year_start = year.start_date
        year_end = year.end_date

        allotments = LeaveTypeAllotment.objects.filter(
            designation_id=designation_id, academic_year_id=academic_year_id, isActive=True)
        result = []
        for allot in allotments:
            ltype = LeaveType.objects.filter(id=allot.leave_type_id, isActive=True).first()
            if ltype is None:
                continue
            applications = LeaveApplication.objects.filter(
                applicant_id=str(applicant.id), leave_type=ltype.leave_type_name,
                status__in=['PENDING', 'APPROVED'], isActive=True)
            if year_start is not None:
                applications = applications.filter(end_date__gte=year_start)
            if year_end is not None:
                applications = applications.filter(start_date__lte=year_end)
            planned = 0
            for app in applications:
                planned += float(app.number_of_days or 0)

            allowed = float(allot.allowed or 0)
            opening = float(allot.opening_balance or 0)
            available = round(opening + allowed - planned, 2)

            result.append({
                'id': allot.id,
                'leave_type_id': allot.leave_type_id,
                'leave_type': ltype.leave_type_name,
                'units': ltype.units,
                'allowed': round(allowed, 2),
                'planned': round(planned, 2),
                'available': available,
                'opening_balance': round(opening, 2),
                'academic_year_id': academic_year_id,
                'designation_id': designation_id,
            })

        return _final_response(request, {
            "n": 1,
            'msg': 'Leave balance found successfully.',
            'data': result
        })
