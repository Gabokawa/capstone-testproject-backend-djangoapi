from django.urls import path
from .views import get_user_details_by_id, signup, login_view, edit_account, logout_view, delete_account, edit_user_details, get_user_details, AddressListCreateView, AddressDetailView, check_storage_config, test_file_upload
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('edit_account/', edit_account, name='edit_account'),
    path('edit_user_details/', edit_user_details, name='edit_user_details'),
    path('delete_account/', delete_account, name='delete_account'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get_user_details', get_user_details, name='get_user_details'),
    path('get_user_details/<int:user_id>/', get_user_details_by_id, name='get_user_details_by_id'),
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:address_id>/', AddressDetailView.as_view(), name='address_detail'),
    path('debug/storage/', check_storage_config, name='check_storage_config'),
    path('debug/test_file_upload/', test_file_upload, name='test_file_upload'),
]

# Method	Endpoint	Description
# GET	/users/addresses/	Get all addresses for the logged-in user
# POST	/users/addresses/	Create a new address (auto-linked to user)
# GET	/users/addresses/<id>/	Get details of a specific address
# PUT/PATCH	/users/addresses/<id>/	Update address
# DELETE	/users/addresses/<id>/	Delete address