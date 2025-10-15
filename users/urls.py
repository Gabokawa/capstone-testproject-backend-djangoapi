from django.urls import path
from .views import signup, login_view, edit_account, logout_view, delete_account, edit_user_details, get_user_details
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup', signup, name='signup'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('edit_account', edit_account, name='edit_account'),
    path('edit_user_details', edit_user_details, name='edit_user_details'),
    path('delete_account', delete_account, name='delete_account'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get_user_details', get_user_details, name='get_user_details'),
]