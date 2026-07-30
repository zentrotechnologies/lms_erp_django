from . import views
from django.urls import include, path

urlpatterns = [
    path('add-enrollments',views.AddEnrollments.as_view(), name='post'),
    path('enrollments-list',views.EnrollmentsList.as_view(), name='post'),
    path('admission-request-list',views.AdmissionRequestList.as_view(), name='post'),
    path('approved-enrollment-status',views.ApprovedEnrollmentStatus.as_view(), name='post'),
    path('declined-enrollments',views.DeclinedEnrollments.as_view(), name='post'),
    path('profile-pending-enrollments',views.ProfilePendingEnrollments.as_view(), name='post'),
    path('payment-enrollments',views.PaymentEnrollments.as_view(), name='post'),
    path('send-payment-link',views.SendPaymentLink.as_view(), name='post'),
    path('save-payment',views.SavePayment.as_view(), name='post'),

]