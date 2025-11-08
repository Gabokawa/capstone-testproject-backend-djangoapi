from rest_framework import serializers
from .models import Quote, Booking, ServiceIssue
from requests.serializers import ServiceRequestDetailSerializer

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = '__all__'  # This tells DRF to serialize *all* fields on the model
        read_only_fields = ['quote_id', 'created_at']

class ServiceIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceIssue
        fields = '__all__'
        read_only_fields = ['issue_id', 'reported_at']

class BookingSerializer(serializers.ModelSerializer):
    request = ServiceRequestDetailSerializer(read_only=True)
    quote = QuoteSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['booking_id', 'created_at']