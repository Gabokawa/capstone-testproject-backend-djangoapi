from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Professional, ProfessionalDocument, WorkingHours, ProfessionalService
from users.models import User
from services.models import Service
import json
from .serializers import (ProfessionalSerializer, 
                          ProfessionalDocumentSerializer, 
                          WorkingHoursSerializer, 
                          ProfessionalServiceSerializer)

# ==================== PROFESSIONAL VIEWS ====================

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def professional_list_create(request):
    """List all professionals or create a new professional"""

    if request.method == "GET":
        user_id = request.GET.get('user_id')
        is_verified = request.GET.get('is_verified')
        is_available = request.GET.get('is_available')
        min_rating = request.GET.get('min_rating')
        
        professionals = Professional.objects.all()

        if user_id:
            professionals = professionals.filter(user_id=user_id)
        if is_verified is not None:
            professionals = professionals.filter(is_verified=is_verified.lower() == 'true')
        if is_available is not None:
            professionals = professionals.filter(is_available=is_available.lower() == 'true')
        if min_rating:
            professionals = professionals.filter(rating__gte=min_rating)

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

        return Response({'professionals': data}, status=status.HTTP_200_OK)

    elif request.method == "POST":
        try:
            data = request.data
            required_fields = ['user_id', 'business_name', 'bio', 'service_radius_km']
            
            for field in required_fields:
                if field not in data:
                    return Response({'error': f'Missing required field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(id=data['user_id'])
            except ObjectDoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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

            return Response({
                'message': 'Professional created successfully',
                'professional_id': professional.professional_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def professional_detail(request, professional_id):
    """Retrieve, update or delete a professional"""

    try:
        professional = Professional.objects.get(professional_id=professional_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Professional not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # data = {
        #     'professional_id': professional.professional_id,
        #     'user_id': professional.user_id,
        #     'business_name': professional.business_name,
        #     'bio': professional.bio,
        #     'rating': str(professional.rating),
        #     'total_reviews': professional.total_reviews,
        #     'completed_jobs': professional.completed_jobs,
        #     'is_verified': professional.is_verified,
        #     'is_available': professional.is_available,
        #     'availability_notes': professional.availability_notes,
        #     'last_active': professional.last_active.isoformat(),
        #     'service_radius_km': str(professional.service_radius_km),
        # }
        # return Response(data, status=status.HTTP_200_OK)
        serializer = ProfessionalSerializer(professional)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        data = request.data
        for field in ['business_name', 'bio', 'rating', 'total_reviews', 
                      'completed_jobs', 'is_verified', 'is_available', 
                      'availability_notes', 'service_radius_km']:
            if field in data:
                setattr(professional, field, data[field])
        professional.save()
        return Response({'message': 'Professional updated successfully'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        professional.delete()
        return Response({'message': 'Professional deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def top_professionals(request):
    professionals = Professional.objects.filter(
        is_available=True,
        is_verified=True
    ).order_by('-rating', '-total_reviews')[:5]
    
    serializer = ProfessionalSerializer(professionals, many=True)
    return Response(serializer.data)

# ==================== PROFESSIONAL DOCUMENT VIEWS ====================

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def document_list_create(request):
    """List all documents or create a new document"""

    if request.method == "GET":
        professional_id = request.GET.get('professional_id')
        document_type = request.GET.get('document_type')
        is_verified = request.GET.get('is_verified')

        documents = ProfessionalDocument.objects.all()
        if professional_id:
            documents = documents.filter(professional_id=professional_id)
        if document_type:
            documents = documents.filter(document_type=document_type)
        if is_verified is not None:
            documents = documents.filter(is_verified=is_verified.lower() == 'true')

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

        return Response({'documents': data}, status=status.HTTP_200_OK)

    elif request.method == "POST":
        data = request.data
        required_fields = ['professional_id', 'document_type', 'document_name', 'document_uri']

        for field in required_fields:
            if field not in data:
                return Response({'error': f'Missing required field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

        document = ProfessionalDocument.objects.create(
            professional_id=data['professional_id'],
            document_type=data['document_type'],
            document_name=data['document_name'],
            document_uri=data['document_uri'],
            is_verified=data.get('is_verified', False),
            verified_by_admin_id=data.get('verified_by_admin_id')
        )

        return Response({
            'message': 'Document created successfully',
            'document_id': document.document_id
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def document_detail(request, document_id):
    """Retrieve, update or delete a document"""

    try:
        document = ProfessionalDocument.objects.get(document_id=document_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        data = request.data
        for field in ['document_type', 'document_name', 'document_uri', 
                      'is_verified', 'verified_at', 'verified_by_admin_id']:
            if field in data:
                setattr(document, field, data[field])
        document.save()
        return Response({'message': 'Document updated successfully'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        document.delete()
        return Response({'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)


# ==================== WORKING HOURS VIEWS ====================

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def working_hours_list_create(request):
    """List all working hours or create new working hours"""

    if request.method == "GET":
        # GET REQUEST TO professionals/working_hours/
        professional_id = request.GET.get('professional_id')
        day_of_week = request.GET.get('day_of_week')
        is_available = request.GET.get('is_available')

        hours = WorkingHours.objects.all()
        if professional_id:
            hours = hours.filter(professional_id=professional_id)
        if day_of_week:
            hours = hours.filter(day_of_week=day_of_week)
        if is_available is not None:
            hours = hours.filter(is_available=is_available.lower() == 'true')

        data = [{
            'hours_id': h.hours_id,
            'professional_id': h.professional_id,
            'day_of_week': h.day_of_week,
            'start_time': h.start_time.isoformat(),
            'end_time': h.end_time.isoformat(),
            'is_available': h.is_available,
        } for h in hours]

        return Response({'working_hours': data}, status=status.HTTP_200_OK)

    elif request.method == "POST":
        # POST REQUEST TO professionals/working_hours/
        data = request.data
        required_fields = ['professional_id', 'day_of_week', 'start_time', 'end_time']

        for field in required_fields:
            if field not in data:
                return Response({'error': f'Missing required field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

        hours = WorkingHours.objects.create(
            professional_id=data['professional_id'],
            day_of_week=data['day_of_week'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_available=data.get('is_available', True)
        )

        return Response({
            'message': 'Working hours created successfully',
            'hours_id': hours.hours_id
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def working_hours_detail(request, hours_id):
    """Retrieve, update or delete working hours"""

    try:
        hours = WorkingHours.objects.get(hours_id=hours_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Working hours not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        data = {
            'hours_id': hours.hours_id,
            'professional_id': hours.professional_id,
            'day_of_week': hours.day_of_week,
            'start_time': hours.start_time.isoformat(),
            'end_time': hours.end_time.isoformat(),
            'is_available': hours.is_available,
        }
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        data = request.data
        for field in ['day_of_week', 'start_time', 'end_time', 'is_available']:
            if field in data:
                setattr(hours, field, data[field])
        hours.save()
        return Response({'message': 'Working hours updated successfully'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        hours.delete()
        return Response({'message': 'Working hours deleted successfully'}, status=status.HTTP_200_OK)


# ==================== PROFESSIONAL SERVICE VIEWS ====================

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def professional_service_list_create(request):
    """List all professional services or create a new professional service"""

    if request.method == "GET":
        professional_id = request.GET.get('professional_id')
        service_id = request.GET.get('service_id')
        is_available = request.GET.get('is_available')

        prof_services = ProfessionalService.objects.all()
        if professional_id:
            prof_services = prof_services.filter(professional_id=professional_id)
        if service_id:
            prof_services = prof_services.filter(service_id=service_id)
        if is_available is not None:
            prof_services = prof_services.filter(is_available=is_available.lower() == 'true')

        # Use the serializer instead of manual dict construction
        serializer = ProfessionalServiceSerializer(prof_services, many=True)
        
        return Response({'professional_services': serializer.data}, status=status.HTTP_200_OK)

    elif request.method == "POST":
        data = request.data
        required_fields = ['professional_id', 'service_id', 'estimated_duration_minutes']

        for field in required_fields:
            if field not in data:
                return Response({'error': f'Missing required field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            professional = Professional.objects.get(professional_id=data['professional_id'])
            service = Service.objects.get(service_id=data['service_id'])
        except ObjectDoesNotExist as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        prof_service = ProfessionalService.objects.create(
            professional=professional,
            service=service,
            custom_price_range=data.get('custom_price_range'),
            service_notes=data.get('service_notes'),
            estimated_duration_minutes=data['estimated_duration_minutes'],
            is_available=data.get('is_available', True)
        )

        return Response({
            'message': 'Professional service created successfully',
            'prof_service_id': prof_service.prof_service_id
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def professional_service_detail(request, prof_service_id):
    """Retrieve, update or delete a professional service"""

    try:
        prof_service = ProfessionalService.objects.get(prof_service_id=prof_service_id)
    except ObjectDoesNotExist:
        return Response({'error': 'Professional service not found'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        data = request.data
        for field in ['custom_price_range', 'service_notes', 
                      'estimated_duration_minutes', 'is_available']:
            if field in data:
                setattr(prof_service, field, data[field])
        prof_service.save()
        return Response({'message': 'Professional service updated successfully'}, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        prof_service.delete()
        return Response({'message': 'Professional service deleted successfully'}, status=status.HTTP_200_OK)
