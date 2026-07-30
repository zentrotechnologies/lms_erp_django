from django.contrib import admin
from django.urls import path
from .import views as v


urlpatterns = [
    path('category-list',v.categorylist,name="category"),
    path('sub-category-list',v.sub_categorylist,name="subcategorylist"),
    path('department',v.department,name="department"),
    path('rank-list',v.rank,name="rank"),
    path('documents',v.documents,name="documents"),
    path('country-list',v.countrylist,name="country"),
    path('feedback-category',v.feedback_category,name="feedback_category"),
    path('ticket-category',v.ticket_category,name="ticket_category"),
    path('feedback-sub-category',v.FeedbackSubCategory,name="feedback-sub-category"),

    #question
    path('add-question',v.add_question_bank,name="add_question_bank"),
    path('view-question/<id>',v.view_question_bank,name="view_question"),
    path('question-list',v.question_bank,name="question_bank"),
    path('question-bank-validation',v.question_bank_validation,name="question_bank_validation"),
    path('archieve-question',v.archieve_question,name="archieve_question"),
    path('bank-summary',v.bank_summary,name="bank_summary"),
    path('dislike-comments/<id>',v.dislike_comments,name="dislike_comments"),


    #s3-upload
    path('s3-upload',v.s3upload,name="s3upload"),
    path('enquiries',v.enquiries,name="enquiries"),

    #vessel
    path('vessel-list',v.vessel_list,name="vessel_list"),
    path('add-vessel',v.add_vessel,name="add_vessel"),
    path('update-vessel/<id>',v.update_vessel,name="update_vessel"),
    path('view-vessel/<id>',v.view_vessel,name="view_vessel"),

    #qualification
    path('educational-qualification',v.educationalqualificationlist,name="educationalqualification"),
    path('language-list',v.languagelist,name="language"),
    

    
]