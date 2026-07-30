from django.contrib import admin
from django.urls import path
from .import views as v
urlpatterns = [
    path('',v.login,name="login"),
    path('logout',v.logout,name="logout"),

    path('org_base',v.org_base,name="org_base"),
    path('dashboard',v.dashboard,name="dashboard"),
    
    # #training center
    
    path('add-training-center',v.addtrainingcenter,name="addtrainingcenter"),
    path('update-training-center/<uuid:id>',v.updatetrainingcenter,name="updatetrainingcenter"),
    path('training-center-list',v.trainingcenterlist,name="trainingcenterlist"),
    path('sub-training-center-list',v.subtrainingcenterlist,name="subtrainingcenterlist"),
    path('add-sub-training-center',v.addsubtrainingcenter,name="addsubtrainingcenter"),
    path('update-sub-training-center/<uuid:id>',v.updatesubtrainingcenter,name="updatesubtrainingcenter"),
    path('training-center-profile/<str:id>',v.TrainingCenterProfile,name="TrainingCenterProfile"),
    



    # #faculty
    # path('add-faculty',v.addfaculty,name="addfaculty"),
    # path('update-faculty/<uuid:id>',v.updatefaculty,name="updatefaculty"),
    # path('faculty-list',v.facultylist,name="facultylist"),
    
    # #branch
    # path('add-branch',v.addbranch,name="addbranch"),
    # path('branch-list',v.branchlist,name="branchlist"),
    # path('update-branch/<int:id>',v.updatebranch,name="updatebranch"),
    
    #certificate
    path('certificate/templates',v.templatelist,name="templatelist"),
    path('certificate/view-all',v.viewallcertificate,name="viewallcertificate"),
]