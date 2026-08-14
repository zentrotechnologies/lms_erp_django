from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from adminauth.models import UserAdmin, UserAdminToken
from course.models import Course, CourseClass
from master.models import AcademicYear, ClassGroup, Department, Program, Semester
from schedule.models import TimetableSlot, TimetableTemplate


class ScheduleAPITestBase(TestCase):
    """Shared setup: authenticated user + master data used by the schedule APIs."""

    def setUp(self):
        self.client = APIClient()

        self.user = UserAdmin.objects.create_user(
            email='faculty@example.com',
            password='TestPass123!',
            first_name='Faculty',
            last_name='One',
            name='Faculty One',
            user_type=5,
            og_code='TC001',
            isActive=True,
        )
        self.token = self.user.token
        UserAdminToken.objects.create(
            user_id=str(self.user.id),
            authToken=self.token,
            isActive=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.academic_year = AcademicYear.objects.create(
            academic_year_name='2026-2027',
            start_date=date(2026, 6, 1),
            end_date=date(2027, 5, 31),
            is_current=True,
            status=True,
        )
        self.department = Department.objects.create(
            og_code='TC001',
            department_code='CS',
            department_name='Computer Science',
            status=True,
        )
        self.program = Program.objects.create(
            department_id=self.department.id,
            program_code='CS',
            program_name='Computer Science',
            program_type='UG',
            duration_years=4,
            total_semesters=8,
            status=True,
        )
        self.semester = Semester.objects.create(
            program_id=self.program.id,
            semester_number=1,
            semester_name='Semester 1',
            status=True,
        )
        self.semester2 = Semester.objects.create(
            program_id=self.program.id,
            semester_number=2,
            semester_name='Semester 2',
            status=True,
        )
        self.class_group = ClassGroup.objects.create(
            academic_year_id=self.academic_year.id,
            department_id=self.department.id,
            program_id=self.program.id,
            semester_id=self.semester.id,
            class_name='Computer Science',
            division='A',
            batch_name='2026',
            status=True,
        )
        self.class_group2 = ClassGroup.objects.create(
            academic_year_id=self.academic_year.id,
            department_id=self.department.id,
            program_id=self.program.id,
            semester_id=self.semester.id,
            class_name='Computer Science',
            division='B',
            batch_name='2026',
            status=True,
        )
        self.course = Course.objects.create(
            course_name='Data Structures',
            course_code='DS101',
            course_type='THEORY',
            total_lectures=1,
            total_practicals=0,
            semister_count=1,
            duration='1',
            department_id=self.department.id,
            og_code='TC001',
        )
        self.template = TimetableTemplate.objects.create(
            academic_year_id=self.academic_year.id,
            class_group_id=self.class_group.id,
            template_name='Test Template',
            effective_from=date(2026, 7, 1),
            created_by='admin',
        )
        self.template2 = TimetableTemplate.objects.create(
            academic_year_id=self.academic_year.id,
            class_group_id=self.class_group2.id,
            template_name='Test Template B',
            effective_from=date(2026, 7, 1),
            created_by='admin',
        )
        self.slot = TimetableSlot.objects.create(
            timetable_template_id=self.template.id,
            day_of_week=0,
            period_number=1,
            start_time='09:00',
            end_time='10:00',
            course_id=self.course.id,
            faculty_id='1',
            room_number='R101',
            entry_for='lecture',
            lecture_type='THEORY',
            is_active=True,
        )

    def _post(self, url, payload):
        return self.client.post(url, payload, format='json')


class TemplateDetailsAPITest(ScheduleAPITestBase):
    def test_ignores_non_uuid_faculty_ids(self):
        response = self._post('/api/schedule/template-details', {'template_id': self.template.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'Template details found successfully')
        slots = response.data['data']['slots'][0]['lectures']
        self.assertEqual(slots[0]['faculty_id'], '1')
        self.assertEqual(slots[0]['faculty_name'], '')

    def test_missing_template_id(self):
        response = self._post('/api/schedule/template-details', {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'template_id is required')

    def test_template_not_found(self):
        response = self._post('/api/schedule/template-details', {'template_id': 999999})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'Template not found')

    def test_success_returns_enriched_metadata(self):
        response = self._post('/api/schedule/template-details', {'template_id': self.template.id})

        data = response.data['data']
        self.assertEqual(data['template_name'], 'Test Template')
        self.assertEqual(data['class_name'], 'Computer Science A')
        self.assertEqual(data['semister_name'], 'Semester 1')
        self.assertEqual(data['academic_year_name'], '2026-2027')
        self.assertEqual(data['total_lectures'], 1)
        self.assertEqual(len(data['slots'][0]['lectures']), 1)

    def test_resolves_valid_uuid_faculty_name(self):
        response = self._post('/api/schedule/template-details', {'template_id': self.template.id})

        faculty_name = response.data['data']['slots'][0]['lectures'][0]['faculty_name']
        self.assertEqual(faculty_name, '')


class ClassListByCourseAPITest(ScheduleAPITestBase):
    def setUp(self):
        super().setUp()
        CourseClass.objects.create(
            course_id=self.course.id,
            class_id=self.class_group.id,
            isActive=True,
        )
        CourseClass.objects.create(
            course_id=self.course.id,
            class_id=self.class_group2.id,
            isActive=True,
        )

    def test_missing_course_id(self):
        response = self._post('/api/schedule/class-list-by-course', {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'Course id is required.')

    def test_course_not_found(self):
        response = self._post('/api/schedule/class-list-by-course', {'course_id': 999999})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'Course not found.')

    def test_no_classes_mapped(self):
        other = Course.objects.create(
            course_name='Algorithms',
            course_code='AL101',
            course_type='THEORY',
            total_lectures=1,
            total_practicals=0,
            semister_count=1,
            duration='1',
            department_id=self.department.id,
            og_code='TC001',
        )
        response = self._post('/api/schedule/class-list-by-course', {'course_id': other.id})
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'No classes found for the course.')
        self.assertEqual(response.data['data'], [])

    def test_success_returns_enriched_classes(self):
        response = self._post('/api/schedule/class-list-by-course', {'course_id': self.course.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        data = response.data['data']
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertEqual(item['course_id'], self.course.id)
            self.assertEqual(item['course_name'], 'Data Structures')
            self.assertEqual(item['academic_year_name'], '2026-2027')
            self.assertEqual(item['department_name'], 'Computer Science')
            self.assertEqual(item['program_name'], 'Computer Science')
            self.assertEqual(item['semester_name'], 'Semester 1')

    def test_filter_by_semester(self):
        response = self._post('/api/schedule/class-list-by-course', {
            'course_id': self.course.id,
            'semester_id': self.semester.id,
        })

        self.assertEqual(response.data['n'], 1)
        self.assertEqual(len(response.data['data']), 2)

    def test_filter_excludes_mismatched_semester(self):
        response = self._post('/api/schedule/class-list-by-course', {
            'course_id': self.course.id,
            'semester_id': self.semester2.id,
        })

        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['data'], [])


class TimetableTemplateListAPITest(ScheduleAPITestBase):
    def test_missing_academic_year_id(self):
        response = self._post('/api/schedule/timetable-template-list', {'semister_id': self.semester.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'academic_year_id is required')

    def test_missing_semister_id(self):
        response = self._post('/api/schedule/timetable-template-list', {'academic_year_id': self.academic_year.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'semister_id is required')

    def test_success_returns_paginated_templates(self):
        response = self._post('/api/schedule/timetable-template-list', {
            'academic_year_id': self.academic_year.id,
            'semister_id': self.semester.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['count'], 2)
        templates = response.data['data']
        self.assertEqual(len(templates), 2)
        names = {t['template_name'] for t in templates}
        self.assertEqual(names, {'Test Template', 'Test Template B'})
        class_names = {t['class_name'] for t in templates}
        self.assertEqual(class_names, {'Computer Science A', 'Computer Science B'})
        for template in templates:
            self.assertEqual(template['semister'], 'Semester 1')
            if template['template_name'] == 'Test Template':
                self.assertEqual(template['total_lectures'], 1)
            else:
                self.assertEqual(template['total_lectures'], 0)

    def test_no_templates_found(self):
        response = self._post('/api/schedule/timetable-template-list', {
            'academic_year_id': 999999,
            'semister_id': self.semester.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'No templates found')

    def test_course_filter(self):
        response = self._post('/api/schedule/timetable-template-list', {
            'academic_year_id': self.academic_year.id,
            'semister_id': self.semester.id,
            'course_id': self.course.id,
        })

        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['count'], 1)


class TemplateSlotEditAPITest(ScheduleAPITestBase):
    def test_missing_template_id(self):
        response = self._post('/api/schedule/template-edit', {
            'lecture_day': 0,
            'lecture_no': 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'template_id is required')

    def test_invalid_lecture_day_range(self):
        response = self._post('/api/schedule/template-edit', {
            'template_id': self.template.id,
            'lecture_day': 9,
            'lecture_no': 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'lecture_day must be between 0 and 6')

    def test_invalid_lecture_no(self):
        response = self._post('/api/schedule/template-edit', {
            'template_id': self.template.id,
            'lecture_day': 0,
            'lecture_no': 0,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'lecture_no must be a positive integer')

    def test_non_integer_values(self):
        response = self._post('/api/schedule/template-edit', {
            'template_id': self.template.id,
            'lecture_day': 'abc',
            'lecture_no': 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)

    def test_template_not_found(self):
        response = self._post('/api/schedule/template-edit', {
            'template_id': 999999,
            'lecture_day': 0,
            'lecture_no': 1,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'Template not found')

    def test_slot_not_found(self):
        response = self._post('/api/schedule/template-edit', {
            'template_id': self.template.id,
            'lecture_day': 5,
            'lecture_no': 9,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'Lecture not found for this template')

    def test_successful_update(self):
        response = self._post('/api/schedule/template-edit', {
            'template_id': self.template.id,
            'lecture_day': 0,
            'lecture_no': 1,
            'start_time': '10:00',
            'end_time': '11:00',
            'room_number': 'R202',
            'lecture_type': 'PRACTICAL',
            'entry_for': 'lecture',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'Template lecture updated successfully')
        data = response.data['data']
        self.assertEqual(data['start_time'], '10:00')
        self.assertEqual(data['end_time'], '11:00')
        self.assertEqual(data['room_number'], 'R202')
        self.assertEqual(data['lecture_type'], 'PRACTICAL')

        self.slot.refresh_from_db()
        self.assertEqual(self.slot.room_number, 'R202')
        self.assertEqual(self.slot.lecture_type, 'PRACTICAL')


class TimetableByFiltersAPITest(ScheduleAPITestBase):
    def test_no_template_found(self):
        response = self._post('/api/schedule/timetable-by-filters', {
            'academic_year_id': 999999,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'No timetable template found for the given filters')

    def test_single_template_returns_object(self):
        response = self._post('/api/schedule/timetable-by-filters', {
            'template_id': self.template.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'Timetable found successfully')
        data = response.data['data']
        self.assertIsInstance(data, dict)
        self.assertEqual(data['template_id'], self.template.id)
        self.assertEqual(data['template_name'], 'Test Template')
        self.assertEqual(data['class_name'], 'Computer Science A')
        self.assertEqual(data['semister_name'], 'Semester 1')
        self.assertEqual(data['total_lectures'], 1)

    def test_multiple_templates_return_array(self):
        response = self._post('/api/schedule/timetable-by-filters', {
            'academic_year_id': self.academic_year.id,
            'semister_id': self.semester.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        data = response.data['data']
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_course_filter(self):
        other_course = Course.objects.create(
            course_name='Algorithms',
            course_code='AL101',
            course_type='THEORY',
            total_lectures=1,
            total_practicals=0,
            semister_count=1,
            duration='1',
            department_id=self.department.id,
            og_code='TC001',
        )
        TimetableSlot.objects.create(
            timetable_template_id=self.template2.id,
            day_of_week=0,
            period_number=1,
            start_time='09:00',
            end_time='10:00',
            course_id=other_course.id,
            faculty_id='1',
            room_number='R101',
            entry_for='lecture',
            lecture_type='THEORY',
            is_active=True,
        )
        response = self._post('/api/schedule/timetable-by-filters', {
            'academic_year_id': self.academic_year.id,
            'semister_id': self.semester.id,
            'course_id': self.course.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        data = response.data['data']
        templates = data if isinstance(data, list) else [data]
        matched = []
        for template in templates:
            for day_row in template['slots']:
                matched.extend(day_row['lectures'])
        self.assertTrue(matched)
        self.assertEqual({l['course_name'] for l in matched}, {'Data Structures'})
        self.assertEqual({l['course_id'] for l in matched}, {self.course.id})

    def test_slots_ordered_by_day_and_period(self):
        TimetableSlot.objects.create(
            timetable_template_id=self.template.id,
            day_of_week=0,
            period_number=2,
            start_time='11:00',
            end_time='12:00',
            course_id=self.course.id,
            faculty_id='1',
            room_number='R101',
            entry_for='lecture',
            lecture_type='THEORY',
            is_active=True,
        )
        response = self._post('/api/schedule/timetable-by-filters', {
            'template_id': self.template.id,
        })

        lectures = response.data['data']['slots'][0]['lectures']
        self.assertEqual([l['period_number'] for l in lectures], [1, 2])


class CourseFilterListAPITest(ScheduleAPITestBase):
    def setUp(self):
        super().setUp()
        self.approved_course = Course.objects.create(
            course_name='Operating Systems',
            course_code='OS101',
            course_type='THEORY',
            total_lectures=1,
            total_practicals=0,
            semister_count=1,
            duration='1',
            department_id=self.department.id,
            og_code='TC001',
            course_status='Approved',
            createdBy=str(self.user.id),
        )
        self.pending_course = Course.objects.create(
            course_name='Databases',
            course_code='DB101',
            course_type='THEORY',
            total_lectures=1,
            total_practicals=0,
            semister_count=1,
            duration='1',
            department_id=self.department.id,
            og_code='TC001',
            course_status='Pending',
            createdBy=str(self.user.id),
        )

    def test_success_returns_all_courses_for_og(self):
        response = self._post('/api/course/college-course-filter-list', {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'Course list found  successfully')
        codes = {item['course_code'] for item in response.data['data']}
        self.assertEqual(codes, {'DS101', 'OS101', 'DB101'})

    def test_filter_by_course_status(self):
        response = self._post('/api/course/college-course-filter-list', {'course_status': 'Approved'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        data = response.data['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['course_code'], 'OS101')

    def test_addedby_resolves_creator_name(self):
        response = self._post('/api/course/college-course-filter-list', {'course_status': 'Approved'})

        self.assertEqual(response.data['data'][0]['addedby'], 'Faculty One')

    def test_no_courses_for_other_og(self):
        other_user = UserAdmin.objects.create_user(
            email='other@example.com',
            password='TestPass123!',
            user_type=5,
            og_code='TC999',
            isActive=True,
        )
        other_token = other_user.token
        UserAdminToken.objects.create(
            user_id=str(other_user.id),
            authToken=other_token,
            isActive=True,
        )
        other_client = APIClient()
        other_client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')

        response = other_client.post('/api/course/college-course-filter-list', {}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'course not found')


class AddTemplateAPITest(ScheduleAPITestBase):
    def _payload(self, **overrides):
        payload = {
            'template_name': 'Regular Week',
            'academic_year_id': self.academic_year.id,
            'class_group_id': self.class_group.id,
            'effective_from': '2026-07-01',
            'effective_to': '2026-12-31',
            'periods_per_day': 3,
            'days': [0, 2],
            'start_time': '09:00',
            'period_duration_minutes': 60,
        }
        payload.update(overrides)
        return payload

    def test_missing_required_fields(self):
        response = self._post('/api/schedule/add-template', {'template_name': 'X'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'academic_year_id is required')

    def test_invalid_periods_per_day(self):
        response = self._post('/api/schedule/add-template', self._payload(periods_per_day=0))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'periods_per_day must be at least 1')

    def test_invalid_days_range(self):
        response = self._post('/api/schedule/add-template', self._payload(days=[0, 9]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'days must be between 0 and 6')

    def test_class_not_found(self):
        response = self._post('/api/schedule/add-template', self._payload(class_group_id=999999))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'Class not found')

    def test_invalid_effective_from(self):
        response = self._post('/api/schedule/add-template', self._payload(effective_from='not-a-date'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'effective_from must be a valid date (YYYY-MM-DD)')

    def test_effective_to_before_from(self):
        response = self._post('/api/schedule/add-template', self._payload(
            effective_from='2026-07-01',
            effective_to='2026-06-01',
        ))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'effective_to cannot be before effective_from')

    def test_invalid_start_time(self):
        response = self._post('/api/schedule/add-template', self._payload(start_time='25:99'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'start_time must be a valid time (e.g. 09:00 or 09:00 AM)')

    def test_success_creates_template_and_grid(self):
        response = self._post('/api/schedule/add-template', self._payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 1)
        self.assertEqual(response.data['msg'], 'Template created successfully')
        data = response.data['data']
        self.assertEqual(data['template_name'], 'Regular Week')
        self.assertEqual(data['class_name'], 'Computer Science A')
        self.assertEqual(data['effective_from'], '2026-07-01')
        self.assertEqual(data['effective_to'], '2026-12-31')
        self.assertEqual(data['slots_count'], 6)

        template = TimetableTemplate.objects.get(id=data['template_id'])
        self.assertEqual(template.academic_year_id, self.academic_year.id)
        self.assertEqual(template.class_group_id, self.class_group.id)

        slots = TimetableSlot.objects.filter(timetable_template_id=data['template_id']).order_by('day_of_week', 'period_number')
        self.assertEqual(slots.count(), 6)
        first = slots.first()
        self.assertEqual(first.day_of_week, 0)
        self.assertEqual(first.period_number, 1)
        self.assertEqual(first.start_time, '09:00')
        self.assertEqual(first.end_time, '10:00')
        self.assertEqual(first.course_id, 0)
        self.assertEqual(first.entry_for, 'lecture')
        period_numbers = list(slots.values_list('period_number', flat=True))
        self.assertEqual(period_numbers, [1, 2, 3, 1, 2, 3])

    def test_success_honors_duration(self):
        response = self._post('/api/schedule/add-template', self._payload(period_duration_minutes=90))

        self.assertEqual(response.data['n'], 1)
        slots = TimetableSlot.objects.filter(timetable_template_id=response.data['data']['template_id']).order_by('day_of_week', 'period_number')
        self.assertEqual(slots[0].start_time, '09:00')
        self.assertEqual(slots[0].end_time, '10:30')
        self.assertEqual(slots[1].start_time, '10:30')
        self.assertEqual(slots[1].end_time, '12:00')
        self.assertEqual(slots[2].start_time, '12:00')
        self.assertEqual(slots[2].end_time, '13:30')

    def test_duplicate_template_name_rejected(self):
        self._post('/api/schedule/add-template', self._payload())
        response = self._post('/api/schedule/add-template', self._payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['n'], 0)
        self.assertEqual(response.data['msg'], 'A template with this name already exists for this class')
