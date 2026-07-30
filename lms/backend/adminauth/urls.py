from . import views
from django.urls import include, path

urlpatterns = [

    path('login',views.UserLogin.as_view(), name='post'),
    path('logout',views.UserLogout.as_view(), name='post'),
    
    path('add-admin',views.AddAdmin.as_view(), name='post'),
    
    path('add-oraganisation',views.AddOrganisation.as_view(), name='post'),
    path('add-training-center',views.AddTrainingCenter.as_view(), name='post'),
    path('update-training-center',views.UpdateTrainingCenter.as_view(), name='post'),
    path('delete-training-center',views.DeleteTrainingCenter.as_view(), name='post'),
    path('delete-document',views.DeleteDocument.as_view(), name='post'),

    #sub training center
    path('add-sub-training-center',views.AddSubTrainingCenter.as_view(), name='post'),
    path('update-sub-training-center',views.UpdateSubTrainingCenter.as_view(), name='post'),
    path('sub-training-center-list',views.SubTrainingCenterList.as_view(), name='post'),
    path('training-center-list',views.TrainingCenterList.as_view(), name='post'),
    path('all-training-center-list',views.AllTrainingCenterList.as_view(), name='post'),
    path('org-all-training-center-list',views.OrgAllTrainingCenterList.as_view(), name='post'),
    path('parent-and-sub-training-center-list',views.ParentAndSubTrainingCenterList.as_view(), name='post'),
    
    path('user-details',views.UserDetails.as_view(), name='post'),
    path('training-center-details',views.TrainingCenterDetails.as_view(), name='post'),
    
    #country
    path('search-cities',views.SearchCities.as_view(), name='post'),
    path('add-country-eligibility',views.AddCountryEligibility.as_view(), name='post'),

    #faculty
    path('add-faculty',views.AddFaculty.as_view(), name='post'),
    path('faculty-list',views.FacultyList.as_view(), name='get'),
    path('user-list',views.userList.as_view(), name='get'),
    path('update-faculty',views.UpdateFaculty.as_view(), name='post'),
    path('deletefaculty',views.DeleteFaculty.as_view(), name='post'),

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
    path('get-training-center-courses',views.GetTrainingCenterCourses.as_view(), name='post'),
    
]