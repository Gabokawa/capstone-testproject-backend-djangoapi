from rest_framework import serializers
from .models import ServiceRequest, RequestMedia
from accounts.models import User, Address
from services.models import Service


class RequestMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMedia
        fields = ['media_id', 'request', 'media_type', 'media_name', 
                  'media_uri', 'thumbnail_uri', 'media_size', 
                  'uploaded_at', 'caption', 'is_public']
        read_only_fields = ['media_id', 'uploaded_at']


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Serializer for list view with minimal related data"""
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.service_name', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = ['request_id', 'customer', 'customer_name', 'service', 
                  'service_name', 'device_type', 'device_brand', 'status', 
                  'scheduled_for', 'requested_at']
        read_only_fields = ['request_id', 'requested_at']


class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view with full related data"""
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone', read_only=True)
    service_name = serializers.CharField(source='service.service_name', read_only=True)
    service_category = serializers.CharField(source='service.category.category_name', read_only=True)
    address_full = serializers.SerializerMethodField()
    media_files = RequestMediaSerializer(many=True, read_only=True, source='requestmedia_set')
    
    class Meta:
        model = ServiceRequest
        fields = ['request_id', 'customer', 'customer_name', 'customer_email', 
                  'customer_phone', 'address', 'address_full', 'service', 
                  'service_name', 'service_category', 'device_type', 'device_brand', 
                  'device_model', 'device_issue_description', 'status', 
                  'scheduled_for', 'special_instructions', 'requested_at', 
                  'completed_at', 'media_files']
        read_only_fields = ['request_id', 'requested_at']
    
    def get_address_full(self, obj):
        return {
            'address_id': obj.address.address_id,
            'street': obj.address.street,
            'city': obj.address.city,
            'state': obj.address.state,
            'zip_code': obj.address.zip_code,
            'country': obj.address.country,
        }


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating service requests"""
    
    class Meta:
        model = ServiceRequest
        fields = ['customer', 'address', 'service', 'device_type', 
                  'device_brand', 'device_model', 'device_issue_description', 
                  'special_instructions', 'scheduled_for']
    
    def validate(self, data):
        # Validate that address belongs to customer
        if data['address'].user != data['customer']:
            raise serializers.ValidationError(
                "The selected address does not belong to the customer."
            )
        return data