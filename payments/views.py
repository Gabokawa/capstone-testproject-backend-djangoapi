from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Payment, PaymentTransaction
from .serializers import PaymentSerializer, PaymentTransactionSerializer, PaymentProof

from quotes.models import Booking
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
import time

# ---------- PAYMENTS CRUD ----------
class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
            """
            Optionally restricts the returned payments to a given booking,
            by filtering against a `booking_id` query parameter in the URL.
            """
            # Get the base queryset
            queryset = Payment.objects.all()
            
            # Get the 'booking_id' from the URL's query parameters
            booking_id = self.request.query_params.get('booking_id', None)
            
            if booking_id is not None:
                # Filter the queryset if booking_id is provided
                queryset = queryset.filter(booking__booking_id=booking_id)
                
            return queryset

class PaymentRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


# ---------- PAYMENT TRANSACTIONS CRUD ----------
class PaymentTransactionListCreateView(generics.ListCreateAPIView):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class PaymentTransactionRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class VerifyPaymentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        # Create payment entry (can adjust logic)
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.final_price,
            payment_method="cash",   # Or from request.data
            status="completed",
            transaction_reference=f"REF-{booking_id}-{int(time.time())}",
            payment_date=timezone.now()
        )

        # Save uploaded payment proof(s)
        for key in request.FILES:
            PaymentProof.objects.create(
                payment=payment,
                file=request.FILES[key]
            )

        return Response({
            "message": "Payment verified successfully",
            "payment_id": payment.payment_id
        })