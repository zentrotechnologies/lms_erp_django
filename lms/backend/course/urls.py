from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

        path('add-course',v.AddCourse.as_view(),name='post'),
        path('college-course-filter-list',v.CollegeCourseFilterList.as_view(),name='post'),
        path('college-course-list',v.CollegeCourseList.as_view(),name='post'),
        path('deactivate-course',v.DeactivateCourse.as_view(),name='post'),
        path('activate-course',v.ActivateCourse.as_view(),name='post'),
        path('delete-course',v.DeleteCourse.as_view(),name='post'),
        path('update-course',v.UpdateCourse.as_view(),name='post'),
        path('get-course-details',v.getCoursedetails.as_view(),name='post'),

        path('add-subject',v.AddSubject.as_view(),name='post'),
        path('college-subject-filter-list',v.CollegeSubjectFilterList.as_view(),name='post'),
        path('college-subject-list',v.CollegeSubjectList.as_view(),name='post'),
        path('delete-subject',v.DeleteSubject.as_view(),name='post'),
        path('update-subject',v.UpdateSubject.as_view(),name='post'),
        path('get-subject-details',v.GetSubjectdetails.as_view(),name='post'),
        path('deactivate-subject',v.DeactivateSubject.as_view(),name='post'),
        path('activate-subject',v.ActivateSubject.as_view(),name='post'),




        path('get-course-classes',v.GetCourseClases.as_view(),name='post'),
        path('get-class-semesters',v.GetClassSemesters.as_view(),name='post'),
        path('subject-list-by-course-and-semester',v.SubjectListByCourseAndSemester.as_view(),name='post'),
        path('allocate-subjects-to-student',v.AllocateSubjectToStudent.as_view(),name='post'),

]