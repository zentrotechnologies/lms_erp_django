from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

#course
path('add-course',v.AddCourse.as_view(),name='post'),
path('course-list',v.CourseList.as_view(),name='post'),
path('course-modules-list',v.CourseModulesList.as_view(),name='get'),
path('course-filter-list',v.CourseFilterList.as_view(),name='post'),
path('training-center-course-filter-list',v.TrainingCenterCourseFilterList.as_view(),name='post'),

path('deactivate-course',v.DeactivateCourse.as_view(),name='post'),
path('activate-course',v.activateCourse.as_view(),name='post'),
path('approve-course',v.ApproveCourse.as_view(),name='post'),
path('decline-course',v.DeclineCourse.as_view(),name='post'),
path('add-course-material',v.AddCourseMaterial.as_view(),name='post'),
path('delete-course-material',v.DeleteCourseMaterial.as_view(),name='post'),

# path('update-course-material',v.UpdateCourseMaterial.as_view()),
path('update-course',v.UpdateCourse.as_view(),name='post'),
path('get-course-details',v.getCoursedetails.as_view(),name='post'),
path('get-course-material',v.getCoursematerial.as_view(),name='post'),

path('delete-module',v.deletemodule.as_view(),name='post'),

#training-mode
path('training-modelist',v.trainingmodelist.as_view(),name='trainingmodelist'),

#course-eligibility
path('getsubcategorylist',v.getsubcategorylist.as_view(),name='post'),
path('getoptsubcategorylist',v.getoptsubcategorylist.as_view(),name='post'),

path('getdeptwiseranklist',v.getdeptwiseranklist.as_view(),name='post'),
path('getdeptranklist',v.getdeptranklist.as_view(),name='post'),

path('add-course-eligibility',v.addcourseeligibility.as_view(),name='post'),

path('get-course-detail-multiple',v.GetCourseDetailMultiple.as_view(),name='GetCourseDetailMultiple'),


#candidate-home
path('getcourses-bycategory',v.CoursesByCategory.as_view(), name='post'),
path('get-allcourses-bycategory',v.AllCoursesByCategory.as_view(), name='post'),
path('get-course-detailsbystatus',v.GetCoursedetailsbystatus.as_view(),name='post'), #not in use
path('get-course-detailsbyid',v.GetCoursedetailsbyId.as_view(),name='post'),
path('get-course-resources',v.GetCourseResources.as_view(),name='post'),
path('get-course-category-list',v.GetCourseCategoryList.as_view(),name='get'),
path('get-category-list',v.GetCategoryList.as_view(),name='get'),
path('get-course-institutions',v.InstitutionsList.as_view(),name='post'),

path('recommendation-list',v.RecommendationList.as_view(),name='post'),
path('training-list',v.TrainingList.as_view(),name='post'),


]