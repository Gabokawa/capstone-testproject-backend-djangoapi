from rest_framework import serializers
from .models import Payment, PaymentTransaction, PaymentProof

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'

class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProof
        fields = "__all__"
