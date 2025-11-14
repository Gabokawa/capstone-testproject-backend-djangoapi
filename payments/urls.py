from django.urls import path
from .views import (
    PaymentListCreateView,
    PaymentRetrieveUpdateDeleteView,
    PaymentTransactionListCreateView,
    PaymentTransactionRetrieveUpdateDeleteView,
    VerifyPaymentView
)

urlpatterns = [
    # Payment Endpoints
    path('', PaymentListCreateView.as_view(), name='payments'),
    path('<int:pk>/', PaymentRetrieveUpdateDeleteView.as_view(), name='payment_detail'),

    # Payment Transaction Endpoints
    path('transactions/', PaymentTransactionListCreateView.as_view(), name='transactions'),
    path('transactions/<int:pk>/', PaymentTransactionRetrieveUpdateDeleteView.as_view(), name='transaction_detail'),

    # Payment Proof Endpoints
    path('proofs/<int:booking_id>/', VerifyPaymentView.as_view(), name='payment_proof')
]