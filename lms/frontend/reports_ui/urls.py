from django.contrib import admin
from django.urls import path
from .import views as v
urlpatterns = [
    path('training-center-report',v.TrainingCenterReport,name="TrainingCenterReport"),
    path('course-report',v.CourseReport,name="CourseReport"),
    path('candidate-report',v.CandidateReport,name="CandidateReport"),

    path('revenue-report',v.RevenueReport,name="RevenueReport"),
    path('certification-report',v.CertificationReport,name="CertificationReport"),

]