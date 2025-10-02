from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceRequestViewSet, RequestMediaViewSet

router = DefaultRouter()
router.register(r'service-requests', ServiceRequestViewSet, basename='servicerequest')
router.register(r'request-media', RequestMediaViewSet, basename='requestmedia')

urlpatterns = [
    path('', include(router.urls)),
]