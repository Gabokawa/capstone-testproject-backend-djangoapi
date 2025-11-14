from django.contrib import admin
from payments.models import Payment, PaymentTransaction, PaymentProof

# Register your models here.
admin.site.register(Payment)    
admin.site.register(PaymentTransaction)
admin.site.register(PaymentProof)
