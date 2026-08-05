"""
URL configuration for lms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    #frontend






    #backend
    path('api/adminauth/',include('adminauth.urls')),
    path('api/master/',include('master.urls')),
    path('api/course/',include('course.urls')),
    path('api/schedule/',include('schedule.urls')),
    path('api/usermanagement/',include('usermanagement.urls')),
    path('api/candidate/',include('candidate.urls')),
    path('api/questionbank/',include('questionbank.urls')),
    path('api/feedback/',include('feedback.urls')),
    path('api/exam/',include('exam.urls')),
    path('api/ticket/',include('ticket.urls')),
    path('api/enrollments/',include('enrollments.urls')),
    path('api/attendance/',include('attendance.urls')),
    path('api/rules/',include('rules.urls')),
    path('api/reports/',include('reports.urls')),
    
    #frontend
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
