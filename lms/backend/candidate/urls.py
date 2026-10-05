from . import views
from django.urls import include, path

urlpatterns = [
    path('candidate-login',views.CandidateLogin.as_view(), name='post'),
    path('candidate-logout',views.CandidateLogout.as_view(), name='post'),
    path('candidate-exam-portal-login',views.CandidateExamPortalLogin.as_view(), name='post'),

    path('add-candidate',views.AddCandidate.as_view(), name='post'),
    path('candidate-list',views.CandidateList.as_view(), name='post'),
    path('pagination-candidate-list',views.PaginationCandidateList.as_view(), name='post'),
    path('delete-candidate',views.DeleteCandidate.as_view(), name='post'),
    path('update-candidate',views.UpdateCandidate.as_view(), name='post'),
    path('update-details-candidate-page',views.UpdateDetailsCandidatePage.as_view(), name='post'),
    path('candidate-upload-documents',views.UploadCandidateDocumentFormData.as_view(), name='post'),
    path('approved-candidate-status',views.ApprovedCandidateStatus.as_view(), name='post'),
    path('declined-candidate-status',views.DeclinedCandidateStatus.as_view(), name='post'),

    path('sendemail-otp',views.SendMailOTP.as_view(), name='post'),
    path('verify-otp',views.VerifyOTP.as_view(), name='post'),
    path('register-candidate',views.RegisterCandidate.as_view(), name='post'),
    path('candidate-details',views.CandidateDetails.as_view(), name='post'),

    path('getresults',views.getresults.as_view(), name='post'),
    path('getcertificates',views.getcertificates.as_view(), name='get'),



    path('forgot-password',views.ForgotPassword.as_view(),name='post'),
    path('reset-password',views.ResetPassword.as_view(),name='post'),
    path('send-password-verification-otp',views.SendPasswordVerificationOTP.as_view(),name='post'),
    path('set-password',views.SetPassword.as_view(),name='post'),

    path('update-candidate-password',views.UpdateCandidatePassword.as_view(),name='post'),
    path('update-candidate-profile-picture',views.UpdateCandidateProfilePicture.as_view(),name='post'),



    path('add-admission',views.AddAdmission.as_view(), name='post'),
    path('admission-list',views.AdmissionList.as_view(), name='post'),
    path('admission-details',views.AdmissionDetails.as_view(), name='post'),
    path('update-admission',views.UpdateAdmission.as_view(), name='post'),
    path('delete-admission',views.DeleteAdmission.as_view(), name='post'),


    path('get-course-student-list',views.GetCourseStudentList.as_view(), name='post'),
]
