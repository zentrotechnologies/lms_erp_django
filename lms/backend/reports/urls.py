from . import views
from django.urls import include, path


urlpatterns = [

    path('filter-college-report-api',views.FilterCollegeReportApi.as_view(), name='post'),
    path('get-college-report-counts-api',views.GetCollegeReportCountsApi.as_view(), name='post'),

    path('filter-courses-schedules-report-api',views.FilterCoursesScheduleReportApi.as_view(), name='post'),
    path('get-courses-schedules-report-counts-api',views.GetCoursesScheduleReportCountsApi.as_view(), name='post'),
    
    path('filter-candidate-report-api',views.FilterCandidateReportApi.as_view(), name='post'),
    path('filter-candidate-report-counts-api',views.FilterCandidateReportCountsApi.as_view(), name='post'),
   
    path('filter-revenue-report-api',views.FilterRevenueReportApi.as_view(), name='post'),
    path('filter-revenue-report-counts-api',views.FilterRevenueReportCountsApi.as_view(), name='post'),

    path('filter-certification-report-api',views.FilterCertificationReportApi.as_view(), name='post'),
    path('filter-certification-report-counts-api',views.FilterCertificationReportCountsApi.as_view(), name='post'),
]