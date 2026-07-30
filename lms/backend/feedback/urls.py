from . import views
from django.urls import include, path

urlpatterns = [
    path('add-feedback-category',views.AddFeedbackCategory.as_view(), name='post'),
    path('feedback-category-list',views.FeedbackCategoryList.as_view(), name='post'),
    path('update-feedback-category',views.UpdateFeedbackCategory.as_view(), name='post'),
    path('delete-feedback-category',views.FeedbackDeleteCategory.as_view(), name='post'),
    path('change-feedback-category-status',views.ChangeFeedbackCategoryStatus.as_view(), name='post'),

    # 
    
    path('add-feedback-form',views.AddFeedbackForm.as_view(), name='post'),
    path('feedback-form-list',views.FeedbackFormList.as_view(), name='post'),
    path('update-feedback-form',views.UpdateFeedbackForm.as_view(), name='post'),
    path('delete-feedback-form',views.FeedbackDeleteForm.as_view(), name='post'),
    
    path('feedback-activation',views.FeedbackActivation.as_view(), name='post'),
    # 
    
]