from django.contrib import admin
from professionals.models import Professional, ProfessionalDocument, ProfessionalService, WorkingHours

# Register your models here.
admin.site.register(Professional)
admin.site.register(ProfessionalDocument)
admin.site.register(ProfessionalService)
admin.site.register(WorkingHours)
