from django.urls import path
from . import views

app_name = 'professionals'

urlpatterns = [
    # Professional URLs
    path('top/', views.top_professionals, name='top_professionals'),
    path('', views.professional_list_create, name='professional_list_create'),
    path('<int:professional_id>/', views.professional_detail, name='professional_detail'),
    
    # Professional Document URLs
    path('documents/', views.document_list_create, name='document_list_create'),
    path('documents/<int:document_id>/', views.document_detail, name='document_detail'),
    
    # Working Hours URLs
    path('working-hours/', views.working_hours_list_create, name='working_hours_list_create'),
    path('working-hours/<int:hours_id>/', views.working_hours_detail, name='working_hours_detail'),
    
    # Professional Service URLs
    path('professional-services/', views.professional_service_list_create, name='professional_service_list_create'),
    path('professional-services/<int:prof_service_id>/', views.professional_service_detail, name='professional_service_detail'),
]