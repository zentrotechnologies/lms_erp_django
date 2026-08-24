from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

    path('add-schedule',v.AddSchedule.as_view(),name='add-schedule'),
    path('update-schedule',v.UpdateSchedule.as_view(),name='update-schedule'),
    path('delete-schedule',v.DeleteSchedule.as_view(),name='delete-schedule'),
    path('get-schedule-by-id',v.GetScheduleById.as_view(),name='get-schedule-by-id'),
    path('filter-schedule-api',v.ScheduleFilterApi.as_view(),name='filter-schedule-api'),
    path('schedule-calender-events',v.ScheduleCalenderEvents.as_view(),name='schedule-calender-events'),

    path('timetable-template-list',v.TimetableTemplateListByYearSemester.as_view(),name='timetable-template-list'),
    path('timetable-by-filters',v.TimetableTimeTableByFilters.as_view(),name='timetable-by-filters'),
    path('semester-list-by-course',v.SemesterListByCourse.as_view(),name='semester-list-by-course'),
    path('template-edit',v.TemplateSlotEdit.as_view(),name='template-edit'),
    path('template-details',v.TemplateDetails.as_view(),name='template-details'),
    path('add-template',v.AddTemplate.as_view(),name='add-template'),


    


    path('filter-faculty-schedule-pending-requests-list-api',v.FilterFacultySchedulePendingRequestsListApi.as_view(),name='filter-faculty-schedule-pending-requests-list-api'),
    path('filter-faculty-schedule-approved-requests-list-api',v.FilterFacultyScheduleApprovedRequestsListApi.as_view(),name='filter-faculty-schedule-approved-requests-list-api'),
    path('filter-faculty-schedule-decline-requests-list-api',v.FilterFacultyScheduleDeclineRequestsListApi.as_view(),name='filter-faculty-schedule-decline-requests-list-api'),

    path('approve-schedule-request',v.ApproveScheduleRequest.as_view(),name='approve-schedule-request'),
    path('decline-schedule-request',v.DeclineScheduleRequest.as_view(),name='decline-schedule-request'),
    path('reschedule-request',v.RescheduleRequest.as_view(),name='reschedule-request'),
    
    path('filter-faculty-current-schedule-list-api',v.FacultyCurrentScheduleFilterApi.as_view(),name='filter-faculty-current-schedule-list-api'),
    path('filter-faculty-upcoming-schedule-list-api',v.FacultyUpcomingScheduleFilterApi.as_view(),name='filter-faculty-upcoming-schedule-list-api'),
    path('filter-faculty-previous-schedule-list-api',v.FacultyPreviousScheduleFilterApi.as_view(),name='filter-faculty-previous-schedule-list-api'),
    
    path('get-schedule-attendance',v.GetScheduleAttendance.as_view(),name='get-schedule-attendance'),
    path('get-schedule-candidates-attendance',v.GetScheduleCandidatesAttendance.as_view(),name='get-schedule-candidates-attendance'),
    path('class-list-by-course',v.ClassListByCourse.as_view(),name='post'),


]