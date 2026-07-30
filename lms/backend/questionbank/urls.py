from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

    #question master
    path('add-question',v.AddQuestion.as_view(),name='post'),
    path('bulk-upload-questions',v.BulkUploadQuestion.as_view(),name='post'),

    path('update-question',v.UpdateQuestion.as_view(),name='post'),

    path('question-details',v.QuestionDetail.as_view(),name='post'),
    path('question-list',v.QuestionList.as_view(),name='post'),
    path('get-dislike-reviews',v.GetDislikeReviews.as_view(),name='post'),

    #validate-question
    path('validate-question-list',v.ValidateQuestionList.as_view(),name='post'),
    path('archive-question',v.ArchiveQuestion.as_view(),name='post'),
    path('get-duplicate-questions-list',v. GetDuplicateQuestions.as_view(),name='post'),
    path('save-duplicates',v. SaveDuplicates.as_view(),name='post'),
    path('like-question',v. LikeQuestions.as_view(),name='post'),
    path('dislike-question',v. DislikeQuestions.as_view(),name='post'),

    #archive question 
    path('archive-question-list',v.ArchiveQuestionList.as_view(),name='post'),
    path('remove-archive-question',v.RemoveArchiveQuestion.as_view(),name='post'),
    path('delete-question',v.DeleteQuestion.as_view(),name='post'),


]