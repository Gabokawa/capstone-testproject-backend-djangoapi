from django.urls import path
from . import views

urlpatterns = [
    # --- Quote URLs ---
    path('quotes/', 
         views.quote_list_create, 
         name='quote-list-create'),
         
    path('quotes/<int:quote_id>/', 
         views.quote_detail, 
         name='quote-detail'),

    # --- Booking URLs ---
    path('bookings/', 
         views.booking_list_create, 
         name='booking-list-create'),
         
    path('bookings/<int:booking_id>/', 
         views.booking_detail, 
         name='booking-detail'),
     
     path('bookings/by-date/', 
          views.professional_bookings_by_date, 
          name='bookings-by-date'),

    # --- Service Issue URLs ---
    path('service-issues/', 
         views.service_issue_list_create, 
         name='service-issue-list-create'),
         
    path('service-issues/<int:issue_id>/', 
         views.service_issue_detail, 
         name='service-issue-detail'),
]