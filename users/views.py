# Generic imports
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# For signup imports
from django.contrib.auth.hashers import make_password

# For login imports
from django.contrib.auth import authenticate, login, logout

# Model imports
from users.models import User


# Create your views here.

@csrf_exempt
def signup(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body) # Convert Request Body to JSON
            username = data['username']
            password = data['password']
            
            if User.objects.filter(username=username).exists(): # Check if username already exists
                return JsonResponse({
                    'status': 400,
                    'message': 'Username already exists'
                })
            else:
                User.objects.create(username=username, password=make_password(password)) # Create User
                return JsonResponse({
                    'status': 200,
                    'message': 'User created'
                })
            
        else:
            return JsonResponse({
                'status': 400,
                'message': 'Invalid request'
            })
        
    except Exception as e:
        return JsonResponse({
            'status': 400,
            'message': 'Error: ' + str(e)
        })

@csrf_exempt
def login_view(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)

            username = data['username']
            password = data['password']

            # Debug
            print("Username: ", username)
            print("Password: ", password)

            # Check if exists and password matches
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    print("Password matches!")
                else:
                    print("Password does not match!")
            except User.DoesNotExist:
                print("User not found!")

            # Check user is already authenticated
            if request.user.is_authenticated:
                return JsonResponse({
                    'status': 400,
                    'message': 'User already logged in'
                })

            # Authenticate user
            user = authenticate(username=username, password=password)
            print("Authenticated user: ", user)

            if user is not None:
                login(request, user)
                return JsonResponse({
                    'status': 200,
                    'message': 'Logged in'
                })
            else:
                return JsonResponse({
                    'status': 400,
                    'message': 'Invalid credentials'
                })
        
        else:
            return JsonResponse({
                'status': 400,
                'message': 'Invalid request method'
            })

    except Exception as e:
        return JsonResponse({
            'status': 400,
            'message': 'Error: ' + str(e)
        })

@csrf_exempt
def logout_view(request):
    try:
        if request.method == 'POST':
            logout(request) # MIGHT CHANGE, LOGS USER OUT REGARDLESS KUNG KINSA NAGCLICK. MIGHT LOG EVERYONE OUT
            return JsonResponse({
                'status': 200,
                'message': 'Logged out'
            })
        else:
            return JsonResponse({
                'status': 400,
                'message': 'Invalid request method'
            })
    
    except Exception as e:
        return JsonResponse({
            'status': 400,
            'message': 'Error: ' + str(e)
        })

@csrf_exempt
def get_details(request):
    try:
        if request.method == 'GET':
            data = json.loads(request.body)
            username = data['username']

            user = User.objects.get(username=username)

            if request.user.is_authenticated:
                return JsonResponse({
                    'status': 200,
                    'username': user.username
                })
            else:
                return JsonResponse({
                    'status': 400,
                    'message': 'Not logged in'
                })
        
        else:
            return JsonResponse({
                'status': 400,
                'message': 'Invalid request'
            })

    except Exception as e:
        return JsonResponse({
            'status': 400,
            'message': 'Error: ' + str(e)
        })