from . import views
from django.urls import include, path


urlpatterns = [

    path('filter-training-center-report-api',views.FilterTrainingCenterReportApi.as_view(), name='post'),
    path('get-training-center-report-counts-api',views.GetTrainingCenterReportCountsApi.as_view(), name='post'),

    path('filter-courses-schedules-report-api',views.FilterCoursesScheduleReportApi.as_view(), name='post'),
    path('get-courses-schedules-report-counts-api',views.GetCoursesScheduleReportCountsApi.as_view(), name='post'),
    
    path('filter-candidate-report-api',views.FilterCandidateReportApi.as_view(), name='post'),
    path('filter-candidate-report-counts-api',views.FilterCandidateReportCountsApi.as_view(), name='post'),
   
    path('filter-revenue-report-api',views.FilterRevenueReportApi.as_view(), name='post'),
    path('filter-revenue-report-counts-api',views.FilterRevenueReportCountsApi.as_view(), name='post'),

    path('filter-certification-report-api',views.FilterCertificationReportApi.as_view(), name='post'),
    path('filter-certification-report-counts-api',views.FilterCertificationReportCountsApi.as_view(), name='post'),
]