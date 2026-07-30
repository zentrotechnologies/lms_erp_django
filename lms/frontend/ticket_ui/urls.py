from django.contrib import admin
from django.urls import path
from .import views as v


urlpatterns = [
    path('ticket-list',v.ticketlist,name="ticketlist"),
    # path('add-ticket',v.addticket,name="addticket"),
    # path('edit-ticket/<id>',v.editticket,name="editticket"),
    # path('ticket-calender',v.ticketcalender,name="ticketcalender"),
    path('ticket-info/<id>',v.ticketinfo,name="ticket-info"),

]