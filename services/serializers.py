from rest_framework import serializers
from .models import ServiceCategory, Service


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['category_id', 'category_name', 'description', 
                  'category_icon', 'is_active']
        read_only_fields = ['category_id']


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    
    class Meta:
        model = Service
        fields = ['service_id', 'category', 'category_name', 'service_name', 
                  'description', 'estimated_price_range', 
                  'estimated_duration_minutes', 'service_icon', 
                  'service_image', 'is_active']
        read_only_fields = ['service_id']