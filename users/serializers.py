from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'address_id',
            'user',
            'region',
            'full_address',
            'latitude',
            'longitude',
            'is_default',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['address_id', 'created_at', 'updated_at']