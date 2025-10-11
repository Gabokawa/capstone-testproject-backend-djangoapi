from django.contrib import admin
from requests.models import ServiceRequest, RequestMedia

# Register your models here.
admin.site.register(ServiceRequest)
admin.site.register(RequestMedia)
