from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmissionRecordViewSet

router = DefaultRouter()
router.register(r'emissions', EmissionRecordViewSet, basename='emission')

urlpatterns = [
    path('', include(router.urls)),
]