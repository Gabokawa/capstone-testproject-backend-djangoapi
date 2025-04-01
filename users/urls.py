from django.urls import path
from .views import signup, login_view, get_details, logout_view

urlpatterns = [
    path('signup', signup, name='signup'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('get_details', get_details, name='get_details'),
]