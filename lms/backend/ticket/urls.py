from django.contrib import admin
from django.urls import path,include
from .import views as v


urlpatterns = [

    path('add-ticket',v.AddTicket.as_view(),name='add-ticket'),
    path('delete-ticket',v.DeleteTicket.as_view(),name='delete-ticket'),
    path('ticket-info',v.TicketInfo.as_view(),name='ticket-info'),
    path('close-ticket',v.CloseTicket.as_view(),name='close-ticket'),
    path('mark-duplicate-ticket',v.MarkDuplicateTicket.as_view(),name='mark-duplicate-ticket'),
    path('get-ticket-counts-api',v.GetTicketCounts.as_view(),name='get-ticket-counts-api'),

    path('filter-ticket-api',v.FilterTicket.as_view(),name='filter-ticket-api'),
    path('assign-user-to-ticket',v.AssignUserToTicket.as_view(),name='assign-user-to-ticket'),
    path('assign-user-list',v.AssignUserList.as_view(),name='assign-user-list'),
    path('assign-ticket-user-list',v.TicketAssignUserList.as_view(),name='assign-ticket-user-list'),
    path('get-ticket-activity',v.GetTicketActivity.as_view(),name='get-ticket-activity'),
    path('add-ticket-activity',v.AddTicketActivity.as_view(),name='add-ticket-activity'),
    path('get-ticket-all-attachments',v.GetTicketAllAttachments.as_view(),name='get-ticket-all-attachments'),
    path('mark-ticket-as-faq',v.MarkTicketAsFAQ.as_view(),name='mark-ticket-as-faq'),

]