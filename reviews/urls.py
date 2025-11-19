# reviews/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewResponseViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'review-responses', ReviewResponseViewSet, basename='reviewresponse')

urlpatterns = [
    path('', include(router.urls)),
]

# In your main urls.py, include this:
# path('api/', include('reviews.urls')),