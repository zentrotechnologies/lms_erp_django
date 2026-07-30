from . import views
from django.urls import include, path

urlpatterns = [
    path('add-role',views.AddRole.as_view(), name='post'),
    path('role-list',views.RoleList.as_view(), name='post'),
    path('update-role',views.UpdateRole.as_view(), name='post'),
    path('delete-role',views.DeleteRole.as_view(), name='post'),
    # 
    path('add-member',views.AddMember.as_view(), name='post'),
    path('member-list',views.MemberList.as_view(), name='post'),
    path('delete-member',views.DeleteMember.as_view(), name='post'),
    path('update-member',views.UpdateMember.as_view(), name='post'),


    
  
]