from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ServiceCategory, Service
from .serializers import ServiceCategorySerializer, ServiceSerializer

# Create your views here.

class ServiceCategoryViewSet(viewsets.ViewSet):
    """
    ViewSet for ServiceCategory CRUD operations
    """
    
    def list(self, request):
        """GET /api/service-categories/ - List all categories"""
        queryset = ServiceCategory.objects.all()
        
        # Optional filtering
        is_active = request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = ServiceCategorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """POST /api/service-categories/ - Create a new category"""
        serializer = ServiceCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """GET /api/service-categories/{id}/ - Retrieve a specific category"""
        category = get_object_or_404(ServiceCategory, pk=pk)
        serializer = ServiceCategorySerializer(category)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT /api/service-categories/{id}/ - Full update of a category"""
        category = get_object_or_404(ServiceCategory, pk=pk)
        serializer = ServiceCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """PATCH /api/service-categories/{id}/ - Partial update of a category"""
        category = get_object_or_404(ServiceCategory, pk=pk)
        serializer = ServiceCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /api/service-categories/{id}/ - Delete a category"""
        category = get_object_or_404(ServiceCategory, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def services(self, request, pk=None):
        """GET /api/service-categories/{id}/services/ - Get all services in a category"""
        category = get_object_or_404(ServiceCategory, pk=pk)
        services = Service.objects.filter(category=category)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

class ServiceViewSet(viewsets.ViewSet):
    """
    ViewSet for Service CRUD operations
    """
    
    def list(self, request):
        """GET /api/services/ - List all services"""
        queryset = Service.objects.select_related('category').all()
        
        # Optional filtering
        category_id = request.query_params.get('category', None)
        is_active = request.query_params.get('is_active', None)
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """POST /api/services/ - Create a new service"""
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """GET /api/services/{id}/ - Retrieve a specific service"""
        service = get_object_or_404(Service.objects.select_related('category'), pk=pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """PUT /api/services/{id}/ - Full update of a service"""
        service = get_object_or_404(Service, pk=pk)
        serializer = ServiceSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """PATCH /api/services/{id}/ - Partial update of a service"""
        service = get_object_or_404(Service, pk=pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """DELETE /api/services/{id}/ - Delete a service"""
        service = get_object_or_404(Service, pk=pk)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)