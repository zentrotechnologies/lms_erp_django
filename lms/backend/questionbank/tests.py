from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from adminauth.models import UserAdmin, UserAdminToken, CollegeCourses
from course.models import Course, CourseSubjects, Subject
from questionbank.models import (
    DuplicateQuestion,
    Question,
    QuestionImages,
    QuestionOption,
)


class QuestionBankTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = UserAdmin.objects.create_user(
            email='qbank@example.com',
            password='TestPass123!',
            first_name='QB',
            last_name='User',
            name='QB User',
            user_type=2,
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

        self.course = Course.objects.create(
            course_name='Python Full Stack',
            course_code='PFS',
            course_status='Active',
            isActive=True,
        )

    def _create_question(self, course='9', subject='11', **kwargs):
        question = Question.objects.create(
            course=course,
            subject=subject,
            type_of_question='Objective',
            question_text=kwargs.pop('question_text', 'What is Python?'),
            correct_option=kwargs.pop('correct_option', 1),
            time_to_solve=30,
            marks=Decimal('1.00'),
            difficulty_level=kwargs.pop('difficulty_level', 'Easy'),
            tags='',
            note='',
            createdBy=str(self.user.id),
            isActive=True,
            **kwargs,
        )
        QuestionOption.objects.create(
            question_id=question.id,
            option=1,
            option_answer='A',
            isActive=True,
        )
        QuestionOption.objects.create(
            question_id=question.id,
            option=2,
            option_answer='B',
            isActive=True,
        )
        return question


class QuestionModelRenameTest(QuestionBankTestBase):
    def test_question_uses_subject_not_module(self):
        field_names = {f.name for f in Question._meta.get_fields()}
        self.assertIn('subject', field_names)
        self.assertIn('subject_id', field_names)
        self.assertNotIn('module', field_names)
        self.assertNotIn('module_id', field_names)

    def test_duplicate_question_uses_subject_id(self):
        dup = DuplicateQuestion.objects.create(
            question_id=1,
            course_id=self.course.id,
            subject_id=11,
            severity_level='High',
            type_of_question='Objective',
            isActive=True,
        )
        self.assertEqual(dup.subject_id, 11)
        self.assertFalse(hasattr(dup, 'module_id'))


class AddQuestionTest(QuestionBankTestBase):
    def test_add_question_multipart_with_subject(self):
        payload = {
            'course': str(self.course.id),
            'subject': '11',
            'type_of_question': 'Objective',
            'question_text': 'Which of these is a Python framework?',
            'correct_option': '1',
            'time_to_solve': '30',
            'marks': '2',
            'difficulty_level': 'Easy',
            'option_list[0][td_option]': 'Django',
            'option_list[1][td_option]': 'Java',
            'option_list[2][td_option]': 'MySQL',
            'option_list[3][td_option]': 'Linux',
        }
        response = self.client.post(
            '/api/questionbank/add-question', payload, format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        question = Question.objects.get(id=body['data']['id'])
        self.assertEqual(question.subject, '11')
        self.assertEqual(question.course, str(self.course.id))
        self.assertEqual(QuestionOption.objects.filter(question_id=question.id).count(), 4)


class QuestionDetailTest(QuestionBankTestBase):
    def test_detail_returns_subject_list(self):
        question = self._create_question(subject='11')
        response = self.client.post(
            '/api/questionbank/question-details',
            {'question_id': str(question.id)},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        self.assertEqual(body['data']['subject'], [11])
        self.assertIn('question_option_data', body['data'])
        self.assertIn('question_images_data', body['data'])


class QuestionListTest(QuestionBankTestBase):
    def test_list_returns_subject_and_subject_name(self):
        self._create_question(course=str(self.course.id), subject='11')
        response = self.client.post(
            '/api/questionbank/question-list',
            {'course': str(self.course.id)},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        self.assertEqual(body['count'], 1)
        item = body['data'][0]
        self.assertIn('subject', item)
        self.assertIn('subject_name', item)
        self.assertIn('question_option_data', item)


class ValidateQuestionListTest(QuestionBankTestBase):
    def test_validate_list_uses_subject_key(self):
        self._create_question(subject='11')
        response = self.client.post(
            '/api/questionbank/validate-question-list', {}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        item = body['data'][0]
        self.assertIn('subject', item)
        self.assertIn('subject_name', item)


class GetDuplicateQuestionsTest(QuestionBankTestBase):
    def test_filter_by_subject(self):
        target = self._create_question(course=str(self.course.id), subject='11', question_text='Original question')
        near_dup = self._create_question(course=str(self.course.id), subject='11', question_text='Nearly identical')
        self._create_question(course=str(self.course.id), subject='22', question_text='Different subject')
        response = self.client.post(
            '/api/questionbank/get-duplicate-questions-list',
            {
                'questionid': str(target.id),
                'course': str(self.course.id),
                'subject': '11',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        self.assertEqual([q['id'] for q in body['data']], [near_dup.id])
        self.assertEqual(body['data'][0]['question_text'], 'Nearly identical')


class SaveDuplicatesTest(QuestionBankTestBase):
    def test_save_duplicates_persists_subject_id(self):
        question = self._create_question(subject='11')
        dup_question = self._create_question(
            subject='11', question_text='Nearly identical'
        )
        response = self.client.post(
            '/api/questionbank/save-duplicates',
            {
                'questionid': str(question.id),
                'course': str(self.course.id),
                'subject': '11',
                'severity_level': 'High',
                'type': 'Objective',
                'duplicatequestions': [str(dup_question.id)],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        dup = DuplicateQuestion.objects.get(question_id=question.id)
        self.assertEqual(dup.subject_id, 11)
        question.refresh_from_db()
        self.assertTrue(question.is_duplicate)


class ArchiveQuestionListTest(QuestionBankTestBase):
    def test_archive_list_uses_subject_key(self):
        self._create_question(subject='11', is_archive=True)
        response = self.client.post(
            '/api/questionbank/archive-question-list', {}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        self.assertIn('subject', body['data'][0])
        self.assertIn('subject_name', body['data'][0])


class ArchiveFlowTest(QuestionBankTestBase):
    def test_archive_and_unarchive(self):
        question = self._create_question(subject='11')
        archive = self.client.post(
            '/api/questionbank/archive-question',
            {'questionid': str(question.id), 'archivereason': 'obsolete'},
            format='json',
        )
        self.assertEqual(archive.json()['n'], 1)
        question.refresh_from_db()
        self.assertTrue(question.is_archive)
        self.assertEqual(question.archive_reason, 'obsolete')

        unarchive = self.client.post(
            '/api/questionbank/remove-archive-question',
            {'questionid': str(question.id)},
            format='json',
        )
        self.assertEqual(unarchive.json()['n'], 1)
        question.refresh_from_db()
        self.assertFalse(question.is_archive)


class QuestionImagesTest(QuestionBankTestBase):
    def test_add_question_with_images(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        payload = {
            'course': str(self.course.id),
            'subject': '11',
            'type_of_question': 'Objective',
            'question_text': 'Question with image?',
            'correct_option': '1',
            'time_to_solve': '30',
            'marks': '2',
            'difficulty_level': 'Easy',
            'option_list[0][td_option]': 'A',
            'option_list[1][td_option]': 'B',
            'file_list': SimpleUploadedFile('q.png', b'fake-image-bytes', content_type='image/png'),
        }
        response = self.client.post(
            '/api/questionbank/add-question', payload, format='multipart'
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['n'], 1)
        self.assertEqual(QuestionImages.objects.filter(question_id=body['data']['id']).count(), 1)


class DropdownTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = UserAdmin.objects.create_user(
            email='dropdown@example.com',
            password='TestPass123!',
            first_name='DD',
            last_name='User',
            name='DD User',
            user_type=3,
            og_code='TC001',
            college_id=1,
            member_of='college-uuid-123',
            isActive=True,
        )
        self.token = self.user.token
        UserAdminToken.objects.create(
            user_id=str(self.user.id),
            authToken=self.token,
            isActive=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.course = Course.objects.create(
            course_name='Python Full Stack',
            course_code='PFS',
            og_code='TC001',
            course_status='Active',
            isActive=True,
        )
        Course.objects.create(
            course_name='Java Full Stack',
            course_code='JFS',
            og_code='TC001',
            course_status='Active',
            isActive=True,
        )
        CollegeCourses.objects.create(
            course_id=self.course.id,
            training_center_id='college-uuid-123',
            isActive=True,
        )

        self.subject = Subject.objects.create(
            subject_code='PY101',
            subject_name='Python Core',
            short_name='PYC',
            subject_type='THEORY',
            status=True,
            isActive=True,
        )
        CourseSubjects.objects.create(
            course_id=self.course.id,
            subject_id=self.subject.id,
            semester_no=1,
            isActive=True,
        )


class CourseListByCollegeTest(DropdownTestBase):
    def test_filters_by_org_code_and_college(self):
        response = self.client.post(
            '/api/questionbank/course-list-by-college',
            {'org_code': 'TC001', 'college_id': 'college-uuid-123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['course_name'], 'Python Full Stack')

    def test_uses_user_og_code_and_member_of_when_not_passed(self):
        response = self.client.post(
            '/api/questionbank/course-list-by-college', {}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.course.id)

    def test_returns_empty_when_college_has_no_courses(self):
        response = self.client.post(
            '/api/questionbank/course-list-by-college',
            {'college_id': 'another-college'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['n'], 0)
        self.assertEqual(response.json()['data'], [])


class SubjectListByCourseTest(DropdownTestBase):
    def test_lists_subjects_for_course(self):
        response = self.client.post(
            '/api/questionbank/subject-list-by-course',
            {'course_id': self.course.id},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['subject_name'], 'Python Core')

    def test_filters_by_semester(self):
        response = self.client.post(
            '/api/questionbank/subject-list-by-course',
            {'course_id': self.course.id, 'semester_id': 2},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['n'], 0)

    def test_requires_course_id(self):
        response = self.client.post(
            '/api/questionbank/subject-list-by-course', {}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['n'], 0)
        self.assertEqual(response.json()['msg'], 'Course id not provided')
