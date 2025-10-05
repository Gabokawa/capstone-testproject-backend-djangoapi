from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import User
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required

@csrf_exempt
@require_POST
def signup(request):
    try:
        data = json.loads(request.body)
        print(data)  # Debug: Print the received data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        user_type = data.get('user_type')
       
        required_fields = ['email', 'password', 'first_name', 'last_name', 'user_type']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing_fields)}"}, status=400)
        
        # if not all([email, password, first_name, last_name, user_type]):
        #     return JsonResponse({"error": "Missing required fields."}, status=400)
       
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists."}, status=400)
       
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            username=email # Using email as username for consistency
        )
        user.set_password(password)
        user.save()
       
        return JsonResponse({"message": "User created successfully."}, status=201)
   
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
       
        user = authenticate(request, username=email, password=password)
       
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "Login successful."})
        else:
            return JsonResponse({"error": "Invalid credentials."}, status=400)
   
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

@csrf_exempt
@require_POST
@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully."})


@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def edit_account(request):
    try:
        data = json.loads(request.body)
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
@require_http_methods(["DELETE"])
@login_required
def delete_account(request):
    try:
        user = request.user
        logout(request) # Log out the user before deletion
        user.delete()
        return JsonResponse({"message": "Account deleted successfully."})
   
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)











# # Generic imports
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# # For signup imports
# from django.contrib.auth.hashers import make_password
# # For login imports
# from django.contrib.auth import authenticate, login, logout
# # Model imports
# from users.models import User
# @csrf_exempt
# def signup(request):
#     try:
#         if request.method == 'POST':
#             data = json.loads(request.body) # Convert Request Body to JSON
#             username = data['username']
#             password = data['password']
            
#             if User.objects.filter(username=username).exists(): # Check if username already exists
#                 return JsonResponse({
#                     'status': 400,
#                     'message': 'Username already exists'
#                 })
#             else:
#                 User.objects.create(username=username, password=make_password(password)) # Create User
#                 return JsonResponse({
#                     'status': 200,
#                     'message': 'User created'
#                 })
            
#         else:
#             return JsonResponse({
#                 'status': 400,
#                 'message': 'Invalid request'
#             })
        
#     except Exception as e:
#         return JsonResponse({
#             'status': 400,
#             'message': 'Error: ' + str(e)
#         })

# @csrf_exempt
# def login_view(request):
#     try:
#         if request.method == 'POST':
#             data = json.loads(request.body)

#             username = data['username']
#             password = data['password']

#             # Debug
#             print("Username: ", username)
#             print("Password: ", password)

#             # Check if exists and password matches
#             try:
#                 user = User.objects.get(username=username)
#                 if user.check_password(password):
#                     print("Password matches!")
#                 else:
#                     print("Password does not match!")
#             except User.DoesNotExist:
#                 print("User not found!")

#             # Check user is already authenticated
#             if request.user.is_authenticated:
#                 return JsonResponse({
#                     'status': 400,
#                     'message': 'User already logged in'
#                 })

#             # Authenticate user
#             user = authenticate(username=username, password=password)
#             print("Authenticated user: ", user)

#             if user is not None:
#                 login(request, user)
#                 return JsonResponse({
#                     'status': 200,
#                     'message': 'Logged in'
#                 })
#             else:
#                 return JsonResponse({
#                     'status': 400,
#                     'message': 'Invalid credentials'
#                 })
        
#         else:
#             return JsonResponse({
#                 'status': 400,
#                 'message': 'Invalid request method'
#             })

#     except Exception as e:
#         return JsonResponse({
#             'status': 400,
#             'message': 'Error: ' + str(e)
#         })

# @csrf_exempt
# def logout_view(request):
#     try:
#         if request.method == 'POST':
#             logout(request) # MIGHT CHANGE, LOGS USER OUT REGARDLESS KUNG KINSA NAGCLICK. MIGHT LOG EVERYONE OUT
#             return JsonResponse({
#                 'status': 200,
#                 'message': 'Logged out'
#             })
#         else:
#             return JsonResponse({
#                 'status': 400,
#                 'message': 'Invalid request method'
#             })
    
#     except Exception as e:
#         return JsonResponse({
#             'status': 400,
#             'message': 'Error: ' + str(e)
#         })

# @csrf_exempt
# def get_details(request):
#     try:
#         if request.method == 'GET':
#             data = json.loads(request.body)
#             username = data['username']

#             user = User.objects.get(username=username)

#             if request.user.is_authenticated:
#                 return JsonResponse({
#                     'status': 200,
#                     'username': user.username
#                 })
#             else:
#                 return JsonResponse({
#                     'status': 400,
#                     'message': 'Not logged in'
#                 })
        
#         else:
#             return JsonResponse({
#                 'status': 400,
#                 'message': 'Invalid request'
#             })

#     except Exception as e:
#         return JsonResponse({
#             'status': 400,
#             'message': 'Error: ' + str(e)
#         })
