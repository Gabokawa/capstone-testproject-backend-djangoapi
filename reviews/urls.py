# reviews/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewResponseViewSet

router = DefaultRouter()
router.register(r'review-responses', ReviewResponseViewSet, basename='reviewresponse')
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]

# In your main urls.py, include this:
# path('api/', include('reviews.urls')),