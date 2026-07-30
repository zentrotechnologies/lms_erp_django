from django.contrib import admin
from django.urls import path
from .import views as v
urlpatterns = [
    path('role',v.role,name="role"),
    path('member',v.member,name="member"),
    path('add-member',v.add_member,name="add_member"),
    path('update-member/<uuid:id>',v.update_member,name="update_member"),
    path('permission',v.permission,name="permission"),
    path('getpermissionbyrole',v.getpermissionbyrole, name='getpermissionbyrole'),
    
]