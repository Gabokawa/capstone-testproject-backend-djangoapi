from django.contrib import admin
from quotes.models import Quote, Booking, ServiceIssue

# Register your models here.
admin.site.register(Quote)
admin.site.register(Booking)
admin.site.register(ServiceIssue)
