from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    PrescriptionViewSet, 
    PrescriptionMedicationViewSet, 
    PrescriptionVitalSignsViewSet
)

router = DefaultRouter()
router.register(r'', PrescriptionViewSet, basename='prescription')

# Nested routers for medications and vital signs
medication_router = DefaultRouter()
medication_router.register(r'medications', PrescriptionMedicationViewSet, basename='prescription-medication')

vital_signs_router = DefaultRouter()
vital_signs_router.register(r'vital-signs', PrescriptionVitalSignsViewSet, basename='prescription-vital-signs')

urlpatterns = router.urls + [
    # Nested routes for prescription medications and vital signs
    path('<int:prescription_pk>/', include(medication_router.urls)),
    path('<int:prescription_pk>/', include(vital_signs_router.urls)),
    
    # Custom endpoints
    path('<int:pk>/edit/', PrescriptionViewSet.as_view({'patch': 'partial_update', 'put': 'update'}), name='prescription-edit'),
    path('<int:pk>/finalize/', PrescriptionViewSet.as_view({'post': 'finalize'}), name='prescription-finalize'),
    path('<int:pk>/save-draft/', PrescriptionViewSet.as_view({'post': 'save_draft'}), name='prescription-save-draft'),
    path('drafts/', PrescriptionViewSet.as_view({'get': 'drafts'}), name='prescription-drafts'),
    path('finalized/', PrescriptionViewSet.as_view({'get': 'finalized'}), name='prescription-finalized'),


]

