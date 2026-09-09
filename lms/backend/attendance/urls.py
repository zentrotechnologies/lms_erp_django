from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

    path('mark-candidate-attendance',v.MarkCandidateAttendance.as_view(),name='mark-candidate-attendance'),

    path('apply-leave',v.ApplyLeave.as_view(),name='apply-leave'),
    path('save-leave',v.SaveLeave.as_view(),name='save-leave'),
    path('leave-list',v.LeaveList.as_view(),name='leave-list'),
    path('leave-details',v.LeaveDetails.as_view(),name='leave-details'),
    path('update-leave',v.UpdateLeave.as_view(),name='update-leave'),
    path('delete-leave',v.DeleteLeave.as_view(),name='delete-leave'),
    path('review-leave',v.ReviewLeave.as_view(),name='review-leave'),

    path('leave-timetable',v.LeaveTimetable.as_view(),name='leave-timetable'),
    path('faculty-timetable',v.FacultyTimetable.as_view(),name='faculty-timetable'),

    path('add-leave-type',v.AddLeaveType.as_view(),name='add-leave-type'),
    path('leave-type-list',v.LeaveTypeList.as_view(),name='leave-type-list'),
    path('update-leave-type',v.UpdateLeaveType.as_view(),name='update-leave-type'),
    path('delete-leave-type',v.DeleteLeaveType.as_view(),name='delete-leave-type'),

    path('add-leave-allotment',v.AddLeaveAllotment.as_view(),name='add-leave-allotment'),
    path('leave-allotment-list',v.LeaveAllotmentList.as_view(),name='leave-allotment-list'),
    path('update-leave-allotment',v.UpdateLeaveAllotment.as_view(),name='update-leave-allotment'),
    path('delete-leave-allotment',v.DeleteLeaveAllotment.as_view(),name='delete-leave-allotment'),

    path('my-leave-balance',v.MyLeaveBalance.as_view(),name='my-leave-balance'),

]