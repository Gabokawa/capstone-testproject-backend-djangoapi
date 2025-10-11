from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import json
from .models import Professional, ProfessionalDocument, WorkingHours, ProfessionalService
from users.models import User
from services.models import Service

# Create your views here.

# ============ PROFESSIONAL VIEWS ============

@csrf_exempt
@require_http_methods(["GET", "POST"])
def professional_list_create(request):
    """List all professionals or create a new professional"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        user_id = request.GET.get('user_id')
        is_verified = request.GET.get('is_verified')
        is_available = request.GET.get('is_available')
        min_rating = request.GET.get('min_rating')
        
        professionals = Professional.objects.all()
        
        # Apply filters
        if user_id:
            professionals = professionals.filter(user_id=user_id)
        if is_verified is not None:
            professionals = professionals.filter(is_verified=is_verified.lower() == 'true')
        if is_available is not None:
            professionals = professionals.filter(is_available=is_available.lower() == 'true')
        if min_rating:
            professionals = professionals.filter(rating__gte=min_rating)
        
        # Serialize data
        data = [{
            'professional_id': p.professional_id,
            'user_id': p.user_id,
            'business_name': p.business_name,
            'bio': p.bio,
            'rating': str(p.rating),
            'total_reviews': p.total_reviews,
            'completed_jobs': p.completed_jobs,
            'is_verified': p.is_verified,
            'is_available': p.is_available,
            'availability_notes': p.availability_notes,
            'last_active': p.last_active.isoformat(),
            'service_radius_km': str(p.service_radius_km),
        } for p in professionals]
        
        return JsonResponse({'html': '<html><head><title>Professionals</title></head><body><h1>Professionals</h1></body></html>', 'professionals': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['user_id', 'business_name', 'bio', 'service_radius_km']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Verify user exists
            try:
                user = User.objects.get(user_id=data['user_id'])
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            
            # Create professional
            professional = Professional.objects.create(
                user=user,
                business_name=data['business_name'],
                bio=data['bio'],
                rating=data.get('rating', 0),
                total_reviews=data.get('total_reviews', 0),
                completed_jobs=data.get('completed_jobs', 0),
                is_verified=data.get('is_verified', False),
                is_available=data.get('is_available', True),
                availability_notes=data.get('availability_notes'),
                service_radius_km=data['service_radius_km']
            )
            
            return JsonResponse({
                'message': 'Professional created successfully',
                'professional_id': professional.professional_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def professional_detail(request, professional_id):
    """Retrieve, update or delete a professional"""
    
    try:
        professional = Professional.objects.get(professional_id=professional_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Professional not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'professional_id': professional.professional_id,
            'user_id': professional.user_id,
            'business_name': professional.business_name,
            'bio': professional.bio,
            'rating': str(professional.rating),
            'total_reviews': professional.total_reviews,
            'completed_jobs': professional.completed_jobs,
            'is_verified': professional.is_verified,
            'is_available': professional.is_available,
            'availability_notes': professional.availability_notes,
            'last_active': professional.last_active.isoformat(),
            'service_radius_km': str(professional.service_radius_km),
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['business_name', 'bio', 'rating', 'total_reviews', 
                         'completed_jobs', 'is_verified', 'is_available', 
                         'availability_notes', 'service_radius_km']:
                if field in data:
                    setattr(professional, field, data[field])
            
            professional.save()
            
            return JsonResponse({'message': 'Professional updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        professional.delete()
        return JsonResponse({'message': 'Professional deleted successfully'}, status=200)


# ============ PROFESSIONAL DOCUMENT VIEWS ============

@csrf_exempt
@require_http_methods(["GET", "POST"])
def document_list_create(request):
    """List all documents or create a new document"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        professional_id = request.GET.get('professional_id')
        document_type = request.GET.get('document_type')
        is_verified = request.GET.get('is_verified')
        
        documents = ProfessionalDocument.objects.all()
        
        # Apply filters
        if professional_id:
            documents = documents.filter(professional_id=professional_id)
        if document_type:
            documents = documents.filter(document_type=document_type)
        if is_verified is not None:
            documents = documents.filter(is_verified=is_verified.lower() == 'true')
        
        # Serialize data
        data = [{
            'document_id': d.document_id,
            'professional_id': d.professional_id,
            'document_type': d.document_type,
            'document_name': d.document_name,
            'document_uri': d.document_uri,
            'is_verified': d.is_verified,
            'uploaded_at': d.uploaded_at.isoformat(),
            'verified_at': d.verified_at.isoformat() if d.verified_at else None,
            'verified_by_admin_id': d.verified_by_admin_id,
        } for d in documents]
        
        return JsonResponse({'documents': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['professional_id', 'document_type', 'document_name', 'document_uri']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create document
            document = ProfessionalDocument.objects.create(
                professional_id=data['professional_id'],
                document_type=data['document_type'],
                document_name=data['document_name'],
                document_uri=data['document_uri'],
                is_verified=data.get('is_verified', False),
                verified_by_admin_id=data.get('verified_by_admin_id')
            )
            
            return JsonResponse({
                'message': 'Document created successfully',
                'document_id': document.document_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def document_detail(request, document_id):
    """Retrieve, update or delete a document"""
    
    try:
        document = ProfessionalDocument.objects.get(document_id=document_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Document not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'document_id': document.document_id,
            'professional_id': document.professional_id,
            'document_type': document.document_type,
            'document_name': document.document_name,
            'document_uri': document.document_uri,
            'is_verified': document.is_verified,
            'uploaded_at': document.uploaded_at.isoformat(),
            'verified_at': document.verified_at.isoformat() if document.verified_at else None,
            'verified_by_admin_id': document.verified_by_admin_id,
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['document_type', 'document_name', 'document_uri', 
                         'is_verified', 'verified_at', 'verified_by_admin_id']:
                if field in data:
                    setattr(document, field, data[field])
            
            document.save()
            
            return JsonResponse({'message': 'Document updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        document.delete()
        return JsonResponse({'message': 'Document deleted successfully'}, status=200)


# ============ WORKING HOURS VIEWS ============

@csrf_exempt
@require_http_methods(["GET", "POST"])
def working_hours_list_create(request):
    """List all working hours or create new working hours"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        professional_id = request.GET.get('professional_id')
        day_of_week = request.GET.get('day_of_week')
        is_available = request.GET.get('is_available')
        
        hours = WorkingHours.objects.all()
        
        # Apply filters
        if professional_id:
            hours = hours.filter(professional_id=professional_id)
        if day_of_week:
            hours = hours.filter(day_of_week=day_of_week)
        if is_available is not None:
            hours = hours.filter(is_available=is_available.lower() == 'true')
        
        # Serialize data
        data = [{
            'hours_id': h.hours_id,
            'professional_id': h.professional_id,
            'day_of_week': h.day_of_week,
            'start_time': h.start_time.isoformat(),
            'end_time': h.end_time.isoformat(),
            'is_available': h.is_available,
        } for h in hours]
        
        return JsonResponse({'working_hours': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['professional_id', 'day_of_week', 'start_time', 'end_time']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Create working hours
            hours = WorkingHours.objects.create(
                professional_id=data['professional_id'],
                day_of_week=data['day_of_week'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                is_available=data.get('is_available', True)
            )
            
            return JsonResponse({
                'message': 'Working hours created successfully',
                'hours_id': hours.hours_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def working_hours_detail(request, hours_id):
    """Retrieve, update or delete working hours"""
    
    try:
        hours = WorkingHours.objects.get(hours_id=hours_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Working hours not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'hours_id': hours.hours_id,
            'professional_id': hours.professional_id,
            'day_of_week': hours.day_of_week,
            'start_time': hours.start_time.isoformat(),
            'end_time': hours.end_time.isoformat(),
            'is_available': hours.is_available,
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['day_of_week', 'start_time', 'end_time', 'is_available']:
                if field in data:
                    setattr(hours, field, data[field])
            
            hours.save()
            
            return JsonResponse({'message': 'Working hours updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        hours.delete()
        return JsonResponse({'message': 'Working hours deleted successfully'}, status=200)


# ============ PROFESSIONAL SERVICE VIEWS ============

@csrf_exempt
@require_http_methods(["GET", "POST"])
def professional_service_list_create(request):
    """List all professional services or create a new professional service"""
    
    if request.method == "GET":
        # Get query parameters for filtering
        professional_id = request.GET.get('professional_id')
        service_id = request.GET.get('service_id')
        is_available = request.GET.get('is_available')
        
        prof_services = ProfessionalService.objects.all()
        
        # Apply filters
        if professional_id:
            prof_services = prof_services.filter(professional_id=professional_id)
        if service_id:
            prof_services = prof_services.filter(service_id=service_id)
        if is_available is not None:
            prof_services = prof_services.filter(is_available=is_available.lower() == 'true')
        
        # Serialize data
        data = [{
            'prof_service_id': ps.prof_service_id,
            'professional_id': ps.professional_id,
            'service_id': ps.service_id,
            'custom_price_range': ps.custom_price_range,
            'service_notes': ps.service_notes,
            'estimated_duration_minutes': ps.estimated_duration_minutes,
            'is_available': ps.is_available,
        } for ps in prof_services]
        
        return JsonResponse({'professional_services': data}, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['professional_id', 'service_id', 'estimated_duration_minutes']
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
            
            # Verify professional and service exist
            try:
                professional = Professional.objects.get(professional_id=data['professional_id'])
                service = Service.objects.get(service_id=data['service_id'])
            except ObjectDoesNotExist as e:
                return JsonResponse({'error': str(e)}, status=404)
            
            # Create professional service
            prof_service = ProfessionalService.objects.create(
                professional=professional,
                service=service,
                custom_price_range=data.get('custom_price_range'),
                service_notes=data.get('service_notes'),
                estimated_duration_minutes=data['estimated_duration_minutes'],
                is_available=data.get('is_available', True)
            )
            
            return JsonResponse({
                'message': 'Professional service created successfully',
                'prof_service_id': prof_service.prof_service_id
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def professional_service_detail(request, prof_service_id):
    """Retrieve, update or delete a professional service"""
    
    try:
        prof_service = ProfessionalService.objects.get(prof_service_id=prof_service_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Professional service not found'}, status=404)
    
    if request.method == "GET":
        data = {
            'prof_service_id': prof_service.prof_service_id,
            'professional_id': prof_service.professional_id,
            'service_id': prof_service.service_id,
            'custom_price_range': prof_service.custom_price_range,
            'service_notes': prof_service.service_notes,
            'estimated_duration_minutes': prof_service.estimated_duration_minutes,
            'is_available': prof_service.is_available,
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            
            # Update fields
            for field in ['custom_price_range', 'service_notes', 
                         'estimated_duration_minutes', 'is_available']:
                if field in data:
                    setattr(prof_service, field, data[field])
            
            prof_service.save()
            
            return JsonResponse({'message': 'Professional service updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == "DELETE":
        prof_service.delete()
        return JsonResponse({'message': 'Professional service deleted successfully'}, status=200)