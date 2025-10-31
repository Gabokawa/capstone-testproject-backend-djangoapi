from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    # Quote URLs
    path('quotes/', views.quote_list_create, name='quote_list_create'),
    path('quotes/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    
    # Booking URLs
    path('bookings/', views.booking_list_create, name='booking_list_create'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    
    # Service Issue URLs
    path('issues/', views.service_issue_list_create, name='service_issue_list_create'),
    path('issues/<int:issue_id>/', views.service_issue_detail, name='service_issue_detail'),
]