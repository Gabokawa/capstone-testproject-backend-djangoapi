from rest_framework import serializers
from .models import (
    Professional,
    ProfessionalDocument,
    WorkingHours,
    ProfessionalService
)
from users.serializers import UserSerializer
from services.serializers import ServiceSerializer

# ==================== PROFESSIONAL SERIALIZER ====================
class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Professional
        fields = [
            'professional_id',
            'user',
            'business_name',
            'bio',
            'rating',
            'total_reviews',
            'completed_jobs',
            'is_verified',
            'is_available',
            'availability_notes',
            'last_active',
            'service_radius_km',
        ]


# ==================== PROFESSIONAL DOCUMENT SERIALIZER ====================
class ProfessionalDocumentSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)

    class Meta:
        model = ProfessionalDocument
        fields = [
            'document_id',
            'professional',
            'document_type',
            'document_name',
            'document_uri',
            'is_verified',
            'uploaded_at',
            'verified_at',
            'verified_by_admin_id',
        ]


# ==================== WORKING HOURS SERIALIZER ====================
class WorkingHoursSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)

    class Meta:
        model = WorkingHours
        fields = [
            'hours_id',
            'professional',
            'day_of_week',
            'start_time',
            'end_time',
            'is_available',
        ]


# ==================== PROFESSIONAL SERVICE SERIALIZER ====================
class ProfessionalServiceSerializer(serializers.ModelSerializer):
    professional = ProfessionalSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = ProfessionalService
        fields = [
            'prof_service_id',
            'professional',
            'service',
            'custom_price_range',
            'service_notes',
            'estimated_duration_minutes',
            'is_available',
        ]