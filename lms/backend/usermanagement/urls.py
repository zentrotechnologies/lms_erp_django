from . import views
from django.urls import include, path

urlpatterns = [
    path('add-role',views.AddRole.as_view(), name='post'),
    path('role-list',views.RoleList.as_view(), name='post'),
    path('update-role',views.UpdateRole.as_view(), name='post'),
    path('delete-role',views.DeleteRole.as_view(), name='post'),

    # designation CRUD (uses Roles table)
    path('add-designation',views.AddDesignation.as_view(), name='post'),
    path('designation-list',views.DesignationList.as_view(), name='post'),
    path('update-designation',views.UpdateDesignation.as_view(), name='post'),
    path('delete-designation',views.DeleteDesignation.as_view(), name='post'),
    # 
    path('add-member',views.AddMember.as_view(), name='post'),
    path('member-list',views.MemberList.as_view(), name='post'),
    path('delete-member',views.DeleteMember.as_view(), name='post'),
    path('update-member',views.UpdateMember.as_view(), name='post'),

    # static roles + unified user management
    path('designations',views.StaticRoleList.as_view(), name='get'),
    path('add-user',views.AddUser.as_view(), name='post'),
    path('user-list',views.UserList.as_view(), name='get'),
    path('user-details',views.UserDetails.as_view(), name='get'),
    path('update-user',views.UpdateUser.as_view(), name='post'),
    path('delete-user',views.DeleteUser.as_view(), name='post'),
    path('parent-login',views.ParentLogin.as_view(), name='post'),
    path('parent-logout',views.ParentLogout.as_view(), name='post'),


    
  
]