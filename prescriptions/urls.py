from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import PrescriptionViewSet

router = DefaultRouter()
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = router.urls + [
    path('prescriptions/<int:pk>/edit/', PrescriptionViewSet.as_view({'patch': 'partial_update', 'put': 'update'}), name='prescription-edit'),
]

