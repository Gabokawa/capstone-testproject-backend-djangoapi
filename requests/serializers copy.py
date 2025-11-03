from rest_framework import serializers
from .models import ServiceRequest, RequestMedia
from users.models import User, Address
from services.models import Service
from professionals.models import Professional


class RequestMediaSerializer(serializers.ModelSerializer):
    # This field accepts the actual file upload.
    # It must match the key you used in formData.append()
    # I've named it 'media_file' to match the frontend code
    media_file = serializers.FileField(write_only=True)

    class Meta:
        model = RequestMedia
        
        # 'media_file' is write-only. It won't be in the response.
        # The model's FileField (e.g., 'media') will be in the response,
        # which will serialize to a URL.
        
        # I'm assuming your model has a FileField named 'media'
        # and all these other fields.
        fields = [
            'media_id', 'request', 'media_type', 'media_name', 
            'media', 'thumbnail_uri', 'media_size', 
            'uploaded_at', 'caption', 'is_public',
            'media_file'  # Add the FileField
        ]
        read_only_fields = ['media_id', 'uploaded_at', 'media', 'thumbnail_uri']

    def create(self, validated_data):
        # 1. Pop the file off the validated data
        uploaded_file = validated_data.pop('media_file')
        
        # 2. Get the other data
        
        # 3. Create the model instance with the metadata
        media_instance = RequestMedia.objects.create(**validated_data)
        
        # 4. Save the file to the instance's FileField
        media_instance.media.save(uploaded_file.name, uploaded_file, save=True)
        
        return media_instance

class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Serializer for list view with minimal related data"""
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.service_name', read_only=True)
    professional_business_name = serializers.CharField(source='professional.business_name', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = ['request_id', 'customer', 'customer_name', 'service', 
                  'service_name', 'professional', 'professional_business_name', 'device_type', 'device_brand', 'status', 
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
            'region': obj.address.region,
            'full_address': obj.address.full_address,
            'latitude': obj.address.latitude,
            'longitude': obj.address.longitude,
        }


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating service requests"""
    
    class Meta:
        model = ServiceRequest

        fields = ['customer', 'address', 'service', 'device_type', 
                  'device_brand', 'device_model', 'device_issue_description', 
                  'special_instructions', 'scheduled_for', 'professional']
    
    def validate(self, data):
        # Validate that address belongs to customer
        if data['address'].user != data['customer']:
            raise serializers.ValidationError(
                "The selected address does not belong to the customer."
            )
        return data