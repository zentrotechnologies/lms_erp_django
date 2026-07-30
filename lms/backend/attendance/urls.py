from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

    path('mark-candidate-attendance',v.MarkCandidateAttendance.as_view(),name='mark-candidate-attendance'),


]