from django.contrib import admin
from services.models import Service, ServiceCategory

# Register your models here.
admin.site.register(Service)
admin.site.register(ServiceCategory)