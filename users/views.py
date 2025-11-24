from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import User, UserRole, UserRoleMapping, Address
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken as refreshtk
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q

# SERIALIZERS IMPORT
from .serializers import AddressSerializer


@csrf_exempt
@api_view(['POST'])
def signup(request):
    try:
        data = json.loads(request.body)
        print(data)  # Debug: Print the received data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        user_type = data.get('user_type')

        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists."}, status=400)
       
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        user.set_password(password)
        user.save()
        refresh = refreshtk.for_user(user)
        print("Token generated: ", str(refresh.access_token))  # Debug: Print the generated token
        return JsonResponse({"message": "User created successfully.", "token": str(refresh.access_token)}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@api_view(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
       
        user = authenticate(request, username=email, password=password)
       
        if user is not None:
            refresh = refreshtk.for_user(user)
            return JsonResponse({
                "message": "Login successful.", 
                "user_type": user.user_type,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                }, 
                status=200)
        else:
            return JsonResponse({"error": "Invalid credentials."}, status=400)
   
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # logout(request)
    # return JsonResponse({"message": "Logged out successfully."})
    try:
        # Get refresh token from request body
        refresh_token = request.data.get("refresh_token")
        
        if refresh_token:
            # Blacklist the refresh token
            token = refreshtk(refresh_token)
            token.blacklist()
            
            return Response({
                "message": "Logged out successfully."
            }, status=200)
        else:
            return Response({
                "error": "Refresh token is required."
            }, status=400)
            
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=200)


@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_account(request):
    try:
        data = request.data
        user = request.user
       
        if not data:
            return JsonResponse({"error": "No data provided for update."}, status=400)
       
        # Update user fields if they exist in the request data
        for field, value in data.items():
            if hasattr(user, field) and field not in ['user_id', 'is_superuser', 'is_staff', 'created_at', 'updated_at', 'password']:
                setattr(user, field, value)
       
        # Handle password change separately and securely
        new_password = data.get('password')
        if new_password:
            user.set_password(new_password)
       
        user.save()
       
        return JsonResponse({"message": "Account updated successfully."})
   
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_user_details(request):
    """
    Edit user details other than password.
    Request body:
    {
        "profile_picture": "url_to_image",
        "roles": [1, 2, 3],  // Array of role_ids to assign
        "addresses": [
            {
                "address_id": 1,  // Only send if updating address, omit for new address
                "region": "Misamis Oriental",
                "full_address": "Lapasan, Cagayan de Oro City",
                "latitude": "67.6767",
                "longitude": "-67.6767",
                "is_default": true
            }
        ],
        "delete_addresses": [2, 3]  // Array of address_ids to delete
    }
    """
    try:
        data = json.loads(request.body)
        user = request.user
        
        if not data:
            return JsonResponse({"error": "No data provided for update."}, status=400)
        
        with transaction.atomic():
            # Update profile picture
            if 'profile_picture' in data:
                user.profile_picture = data['profile_picture']
                user.save()
            
            # Update user roles
            if 'roles' in data:
                role_ids = data['roles']
                if not isinstance(role_ids, list):
                    return JsonResponse({"error": "Roles must be an array of role IDs."}, status=400)
                
                # Remove existing role mappings
                UserRoleMapping.objects.filter(user=user).delete()
                
                # Add new role mappings
                for role_id in role_ids:
                    try:
                        role = UserRole.objects.get(role_id=role_id)
                        UserRoleMapping.objects.create(user=user, role=role)
                    except UserRole.DoesNotExist:
                        return JsonResponse({"error": f"Role with ID {role_id} does not exist."}, status=400)
            
            # Handle address updates/creates
            if 'addresses' in data:
                addresses = data['addresses']
                if not isinstance(addresses, list):
                    return JsonResponse({"error": "Addresses must be an array."}, status=400)
                
                for addr_data in addresses:
                    address_id = addr_data.get('address_id')
                    
                    # Validate required fields for new addresses
                    required_fields = ['region', 'full_address', 'latitude', 'longitude']
                    if not address_id:
                        missing_fields = [field for field in required_fields if field not in addr_data]
                        if missing_fields:
                            return JsonResponse({
                                "error": f"Missing required fields for address: {', '.join(missing_fields)}"
                            }, status=400)
                    
                    # If is_default is True, set all other addresses to False
                    if addr_data.get('is_default', False):
                        Address.objects.filter(user=user).update(is_default=False)
                    
                    if address_id:
                        # Update existing address
                        try:
                            address = Address.objects.get(address_id=address_id, user=user)
                            for field in ['region', 'full_address', 'latitude', 'longitude', 'is_default']:
                                if field in addr_data:
                                    setattr(address, field, addr_data[field])
                            address.save()
                        except Address.DoesNotExist:
                            return JsonResponse({
                                "error": f"Address with ID {address_id} does not exist or doesn't belong to user."
                            }, status=400)
                    else:
                        # Create new address
                        Address.objects.create(
                            user=user,
                            region=addr_data['region'],
                            full_address=addr_data['full_address'],
                            latitude=addr_data['latitude'],
                            longitude=addr_data['longitude'],
                            is_default=addr_data.get('is_default', False)
                        )
            
            # Delete addresses
            if 'delete_addresses' in data:
                delete_ids = data['delete_addresses']
                if not isinstance(delete_ids, list):
                    return JsonResponse({"error": "delete_addresses must be an array of address IDs."}, status=400)
                
                Address.objects.filter(address_id__in=delete_ids, user=user).delete()
        
        return JsonResponse({
            "message": "User details updated successfully.",
            "updated_fields": list(data.keys())
        })
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except ValueError as e:
        return JsonResponse({"error": f"Invalid value: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    try:
        user = request.user
        logout(request) # Log out the user before deletion
        user.delete()
        return JsonResponse({"message": "Account deleted successfully."})
   
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    # request.user is automatically set from the JWT token!
    user = request.user
   
    return JsonResponse({
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "profile_picture": user.profile_picture,
        "user_type": user.user_type,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "device_token": user.device_token,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }, status=200)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "profile_picture": user.profile_picture if user.profile_picture else None,
        "user_type": user.user_type,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "device_token": user.device_token,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }, status=200)

class AddressListCreateView(generics.ListCreateAPIView):
    """
    GET: List all addresses of the authenticated user or with user id.
    POST: Create a new address for the authenticated user.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all addresses
        for the currently authenticated user, OR for a specific user
        if a 'user_id' query parameter is provided.
        """
        # Get 'user_id' from query parameters (e.g., /addresses/?user_id=123)
        user_id = self.request.query_params.get('user_id')

        if user_id:
            # If user_id is provided, filter addresses for that specific user.
            # You should add permissions here to ensure not just anyone
            # can snoop on other users' addresses.
            return Address.objects.filter(user__id=user_id)
        
        # If no user_id is provided, just return addresses
        # for the user making the request.
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific address.
    Only the owner can perform these actions.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'address_id'

    def get_queryset(self):
        # User can only access their own addresses
        user_id = self.kwargs.get('user_id')
        return Address.objects.filter(Q(user=self.request.user) | Q(user__id=user_id))

    def perform_update(self, serializer):
        # Prevent changing the owner through update
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to edit this address.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this address.")
        instance.delete()






