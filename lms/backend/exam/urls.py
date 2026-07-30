from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [
    path('find-number-of-exam-question',v.FindNumberOfExamQuestion.as_view(),name='post'),
    path('add-exam-set',v.AddExamSet.as_view(),name='post'),
    path('view-exam-questioin-set',v.ViewExamQuestionSet.as_view(),name='post'),
    path('view-exam-detail',v.ViewExamDetail.as_view(),name='post'),
    path('exam-list',v.ExamList.as_view(),name='post'),
    path('get-schedule-set-list',v.GetScheduleandSetonbasisofCourse.as_view(),name='post'),
    path('add-schedule-exam',v.AddScheduleExam.as_view(),name='post'),
    path('schedule-exam-list',v.ScheduleExamList.as_view(),name='post'),
    
    path('View-schedule-details',v.ViewScheduleList.as_view(),name='post'),
    path('delete-exam-set',v.DeleteExamSet.as_view(),name='post'),
    path('delete-schedule-exam-set',v.DeleteScheduleExamSet.as_view(),name='post'),
    
    #candidate exam 
    path('view-candidate-exam-questioin-set',v.ViewCandidateExamQuestionSet.as_view(),name='post'),
    path('start-candidate-exam',v.StartCandidateExam.as_view(),name='post'),
    path('submit-candidate-exam',v.SubmitCandidateExam.as_view(),name='post'),
    path('capture-candidate-exam-result',v.CaptureCandidateExamResult.as_view(),name='post'),
    
    #template
    path('add-template',v.AddTemplate.as_view(),name='post'),
    path('template-list',v.TemplateList.as_view(),name='post'),
    path('delete-template',v.DeleteTemplate.as_view(),name='post'),
    path('view-all-certificate',v.ViewAllCertificate.as_view(),name='post'),
    path('candidate-result-list',v.CandidateResultList.as_view(),name='post'),
    path('get-candidates-results',v.GetCandidatesResults.as_view(),name='post'),
    path('get-candidates-results-counts',v.GetCandidatesResultsCounts.as_view(),name='post'),
    
    path('get-candidates-mock-tests',v.GetCandidatesMockTests.as_view(),name='post'),
    path('get-candidates-mock-tests-history',v.GetCandidatesMockTestsHistory.as_view(),name='post'),


    path('start-mock-candidate-exam',v.StartMockCandidateExam.as_view(),name='post'),
    path('view-candidate-mock-exam-questioin-set',v.ViewCandidateMockExamQuestionSet.as_view(),name='post'),
    path('capture-candidate-mock-exam-result',v.CaptureCandidateMockExamResult.as_view(),name='post'),
    path('submit-candidate-mock-exam',v.SubmitCandidateMockExam.as_view(),name='post'),
    path('get-candidate-mock-exam-result-details',v.GetCandidateMockExamResultDetails.as_view(),name='post'),
    path('get-course-non-attempt-exam-candidates-list',v.GetCourseNonAttemptExamCandidates.as_view(),name='post'),

]