from . import views
from django.urls import include, path

urlpatterns = [

    path('login',views.UserLogin.as_view(), name='post'),
    path('logout',views.UserLogout.as_view(), name='post'),
    path('add-admin',views.AddAdmin.as_view(), name='post'),
    
    path('add-oraganisation',views.AddOrganisation.as_view(), name='post'),
    path('add-college',views.AddCollege.as_view(), name='post'),
    path('update-college',views.UpdateCollege.as_view(), name='post'),
    path('delete-college',views.DeleteCollege.as_view(), name='post'),
    path('delete-document',views.DeleteDocument.as_view(), name='post'),


    path('college-list',views.CollegeList.as_view(), name='post'),
    path('all-college-list',views.AllCollegeList.as_view(), name='post'),
    path('org-all-college-list',views.OrgAllCollegeList.as_view(), name='post'),
    path('parent-and-sub-college-list',views.ParentAndSubCollegeList.as_view(), name='post'),
    
    path('user-details',views.UserDetails.as_view(), name='post'),
    path('college-details',views.CollegeDetails.as_view(), name='post'),
    
    #country
    path('search-cities',views.SearchCities.as_view(), name='post'),
    path('search-states',views.SearchStates.as_view(), name='post'),
    path('search-country',views.SearchCountry.as_view(), name='post'),
    path('add-country-eligibility',views.AddCountryEligibility.as_view(), name='post'),

    #faculty
    path('add-faculty',views.AddFaculty.as_view(), name='post'),
    path('faculty-list',views.FacultyList.as_view(), name='get'),
    path('user-list',views.userList.as_view(), name='get'),
    path('update-faculty',views.UpdateFaculty.as_view(), name='post'),
    path('delete-faculty',views.DeleteFaculty.as_view(), name='post'),


    path('check-decrypt-data',views.CheckAndDecyptData.as_view(), name='post'),
    path('get-public-key',views.GetPublicKey.as_view(), name='post'),
    path('main-role-list',views.MainRoleList.as_view(), name='post'),
    path('main-role-document-list',views.MainRoleDocumentList.as_view(), name='post'),
    path('user-upload-docs',views.UploadUserDocument.as_view(), name='post'),
    path('user-upload-documents',views.UploadUserDocumentFormData.as_view(), name='post'),
    path('menu-details',views.MenuDetailList.as_view(),name='post'),
    
    path('add-permission',views.AddPermission.as_view(), name='post'),
    path('get-permission',views.GetPermission.as_view(), name='post'),
    path('get-usertype-permission',views.GetUserTypePermission.as_view(), name='post'),
    
    #user docs
    path('delete-user-documents',views.DeleteUserDocuments.as_view(), name='post'),
    path('get-college-courses',views.GetCollegeCourses.as_view(), name='post'),
    
]
