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
    path('candidate-documents-submit',views.candidatedocumentssubmit.as_view(), name='post'),
    path('get-enrollment-documents',views.getenrollmentdocuments.as_view(), name='post'),
    path('candidate-course-categories',views.candidatecoursecategories.as_view(), name='get'),
    path('getresults',views.getresults.as_view(), name='post'),
    path('getcertificates',views.getcertificates.as_view(), name='get'),

    path('country-list',views.CountryList.as_view(),name='get'),
    path('non-eligible-country-list',views.NonEligibleCountryList.as_view(),name='get'),
    path('eligible-country-list',views.EligibleCountryList.as_view(),name='get'),

    path('forgot-password',views.ForgotPassword.as_view(),name='post'),
    path('reset-password',views.ResetPassword.as_view(),name='post'),
    path('send-password-verification-otp',views.SendPasswordVerificationOTP.as_view(),name='post'),
    path('set-password',views.SetPassword.as_view(),name='post'),

    path('get-general-details',views.GetGeneralDetails.as_view(),name='post'),
    path('update-general-details',views.UpdateGeneralDetails.as_view(),name='post'),
    path('update-candidate-password',views.UpdateCandidatePassword.as_view(),name='post'),
    path('update-candidate-profile-picture',views.UpdateCandidateProfilePicture.as_view(),name='post'),

    path('get-seafarers-details',views.GetSeafarersDetails.as_view(),name='post'),
    path('update-seafarers-details',views.UpdateSeafarersDetails.as_view(),name='post'),
    path('get-candidate-mandatory-document',views.GetCandidateMandatoryDocument.as_view(),name='post'),
    path('upload-candidate-documents',views.UploadCandidateDocuments.as_view(),name='post'),

    path('get-candidate-institutes-course-details',views.GetCandidateInstitutesCourseDetails.as_view(),name='post'),

    # College student API aliases. These reuse the existing candidate code paths while
    # accepting the new student fields added to the Candidate model.
    # path('student-login',views.StudentLogin.as_view(), name='post'),
    # path('student-logout',views.StudentLogout.as_view(), name='post'),
    # path('add-student',views.AddStudent.as_view(), name='post'),
    # path('student-list',views.StudentList.as_view(), name='post'),
    # path('student-details',views.StudentDetails.as_view(), name='get'),
    # path('update-student',views.UpdateStudent.as_view(), name='post'),
    # path('delete-student',views.DeleteStudent.as_view(), name='post'),
    # path('register-student',views.RegisterStudent.as_view(), name='post'),
    # path('student-profile-details',views.StudentProfileDetails.as_view(), name='get'),
    # path('update-student-profile',views.UpdateStudentProfile.as_view(), name='post'),

    path('add-admission',views.AddAdmission.as_view(), name='post'),
    path('admission-list',views.AdmissionList.as_view(), name='post'),
    path('admission-details',views.AdmissionDetails.as_view(), name='post'),
    path('update-admission',views.UpdateAdmission.as_view(), name='post'),
    path('delete-admission',views.DeleteAdmission.as_view(), name='post'),


    path('get-course-student-list',views.GetCourseStudentList.as_view(), name='post'),
]
