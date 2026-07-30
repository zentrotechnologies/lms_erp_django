from django.contrib import admin
from django.urls import path
from .import views as v


urlpatterns = [
    path('course-list',v.courselist,name="courselist"),
    path('add-course',v.addcourse,name="addcourse"),
    path('update-course/<id>',v.updatecourse,name="updatecourse"),
    path('study-material',v.studymaterial,name="studymaterial"),
]