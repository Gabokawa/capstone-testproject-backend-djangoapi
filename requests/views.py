from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from .models import ServiceRequest, RequestMedia
from .serializers import (
    ServiceRequestListSerializer, 
    ServiceRequestDetailSerializer,
    ServiceRequestCreateSerializer,
    RequestMediaSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, status
from rest_framework.decorators import action

# Create your views here.

class ServiceRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for ServiceRequest CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Base queryset with optimizations"""
        return ServiceRequest.objects.select_related(
            'customer', 'address', 'service', 'service__category', 'professional' #<-- added professional here
        ).prefetch_related('requestmedia_set')
    
    def list(self, request):
        """GET /api/service-requests/ - List all service requests"""
        queryset = self.get_queryset()
        
        # Filtering
        customer_id = request.query_params.get('customer', None)
        status_filter = request.query_params.get('status', None)
        service_id = request.query_params.get('service', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        professional_id = request.query_params.get('professional', None)

        if professional_id:
            # queryset = queryset.filter(professional_id=professional_id)
            # Filter for requests where the professional is either:
            # 1. Assigned (in the professional ForeignKey field), OR
            # 2. In the potential professionals list (professionals ManyToManyField)
            queryset = queryset.filter(
                Q(professional_id=professional_id) | Q(professionals__id=professional_id)
            ).distinct()  # Use distinct() to avoid duplicate results from M2M joins
            
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        if date_from:
            queryset = queryset.filter(requested_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(requested_at__lte=date_to)
        
        # Ordering
        queryset = queryset.order_by('-requested_at')
        
        serializer = ServiceRequestListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """POST /api/service-requests/ - Create a new service request"""
        serializer = ServiceRequestCreateSerializer(data=request.data)
        if serializer.is_valid():
            service_request = serializer.save()
            detail_serializer = ServiceRequestDetailSerializer(service_request)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """GET /api/service-requests/{id}/ - Retrieve a specific service request"""
        service_request = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = ServiceRequestDetailSerializer(service_request)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT /api/service-requests/{id}/ - Full update of a service request"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        serializer = ServiceRequestCreateSerializer(service_request, data=request.data)
        if serializer.is_valid():
            service_request = serializer.save()
            detail_serializer = ServiceRequestDetailSerializer(service_request)
            return Response(detail_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """PATCH /api/service-requests/{id}/ - Partial update of a service request"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        serializer = ServiceRequestCreateSerializer(
            service_request, data=request.data, partial=True
        )
        if serializer.is_valid():
            service_request = serializer.save()
            detail_serializer = ServiceRequestDetailSerializer(service_request)
            return Response(detail_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /api/service-requests/{id}/ - Delete a service request"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        service_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """POST /api/service-requests/{id}/update_status/ - Update request status"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        new_status = request.data.get('status')
        
        if new_status not in dict(ServiceRequest.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service_request.status = new_status
        
        # Auto-set completed_at when status is completed
        if new_status == 'completed' and not service_request.completed_at:
            service_request.completed_at = timezone.now()
        
        service_request.save()
        serializer = ServiceRequestDetailSerializer(service_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """POST /api/service-requests/{id}/schedule/ - Schedule a service request"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        scheduled_for = request.data.get('scheduled_for')
        
        if not scheduled_for:
            return Response(
                {'error': 'scheduled_for is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service_request.scheduled_for = scheduled_for
        service_request.status = 'booked'
        service_request.save()
        
        serializer = ServiceRequestDetailSerializer(service_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/service-requests/{id}/cancel/ - Cancel a service request"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        service_request.status = 'cancelled'
        service_request.save()
        
        serializer = ServiceRequestDetailSerializer(service_request)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """GET /api/service-requests/statistics/ - Get request statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_status': {},
            'pending_count': queryset.filter(status='pending').count(),
            'active_count': queryset.filter(
                status__in=['pending', 'quoted', 'booked']
            ).count(),
        }
        
        # Count by status
        for status_code, status_label in ServiceRequest.STATUS_CHOICES:
            stats['by_status'][status_code] = queryset.filter(
                status=status_code
            ).count()
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def media(self, request, pk=None):
        """GET /api/service-requests/{id}/media/ - Get all media for a request"""
        service_request = get_object_or_404(ServiceRequest, pk=pk)
        media_files = RequestMedia.objects.filter(request=service_request)
        serializer = RequestMediaSerializer(media_files, many=True)
        return Response(serializer.data)


class RequestMediaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RequestMedia CRUD operations
    """

    queryset = RequestMedia.objects.all()
    serializer_class = RequestMediaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def list(self, request):
        """GET /api/request-media/ - List all media files"""
        queryset = RequestMedia.objects.select_related('request').all()
        
        # Filtering
        request_id = request.query_params.get('request', None)
        media_type = request.query_params.get('media_type', None)
        is_public = request.query_params.get('is_public', None)
        
        if request_id:
            queryset = queryset.filter(request_id=request_id)
        if media_type:
            queryset = queryset.filter(media_type=media_type)
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        queryset = queryset.order_by('-uploaded_at')
        
        serializer = RequestMediaSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # def create(self, request):
    #     """POST /requests/request-media/ - Upload a new media file"""
    #     serializer = RequestMediaSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        """POST /requests/request-media/ - Upload a new media file"""
        # --- THIS IS THE FIX ---
        # 1. Make a mutable copy of the data
        mutable_data = request.data.copy()
        
        # 2. Manually convert the 'request' field from str to int
        # This checks if 'request' is present and is a string-digit
        if 'request' in mutable_data and isinstance(mutable_data['request'], str):
            if mutable_data['request'].isdigit():
                mutable_data['request'] = int(mutable_data['request'])
                print(f"Converted 'request' to int: {mutable_data['request']}")
            else:
                # Handle case where it's not a valid digit string
                return Response(
                    {'request': 'Invalid pk. Must be an integer.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 3. Pass the *cleaned* data to the serializer
        serializer = self.get_serializer(data=mutable_data)
        # --- END OF FIX ---
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # The serializer.errors will now be much more accurate
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """GET /api/request-media/{id}/ - Retrieve a specific media file"""
        media = get_object_or_404(RequestMedia, pk=pk)
        serializer = RequestMediaSerializer(media)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT /api/request-media/{id}/ - Full update of a media file"""
        media = get_object_or_404(RequestMedia, pk=pk)
        serializer = RequestMediaSerializer(media, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """PATCH /api/request-media/{id}/ - Partial update of a media file"""
        media = get_object_or_404(RequestMedia, pk=pk)
        serializer = RequestMediaSerializer(media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /api/request-media/{id}/ - Delete a media file"""
        media = get_object_or_404(RequestMedia, pk=pk)
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """POST /api/request-media/bulk_upload/ - Upload multiple media files"""
        media_items = request.data.get('media_items', [])
        
        if not media_items:
            return Response(
                {'error': 'media_items array is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_media = []
        errors = []
        
        for item in media_items:
            serializer = RequestMediaSerializer(data=item)
            if serializer.is_valid():
                media = serializer.save()
                created_media.append(RequestMediaSerializer(media).data)
            else:
                errors.append({
                    'data': item,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created_media,
            'errors': errors,
            'success_count': len(created_media),
            'error_count': len(errors)
        }, status=status.HTTP_201_CREATED if created_media else status.HTTP_400_BAD_REQUEST)
