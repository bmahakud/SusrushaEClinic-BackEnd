from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'consultations'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.ConsultationViewSet, basename='consultation')

urlpatterns = [
    # Consultation search and statistics
    path('search/', views.ConsultationSearchView.as_view(), name='consultation-search'),
    path('stats/', views.ConsultationStatsView.as_view(), name='consultation-stats'),
    
    # Consultation-specific nested resources
    path('<str:consultation_id>/diagnosis/', 
         views.ConsultationDiagnosisViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-diagnosis'),
    path('<str:consultation_id>/diagnosis/<int:pk>/', 
         views.ConsultationDiagnosisViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-diagnosis-detail'),
    
    path('<str:consultation_id>/vital-signs/', 
         views.ConsultationVitalSignsViewSet.as_view({"get": "list", "post": "create"}), 
         name='consultation-vital-signs'),
    path('<str:consultation_id>/vital-signs/<int:pk>/', 
         views.ConsultationVitalSignsViewSet.as_view({
             "get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"
         }), 
         name='consultation-vital-signs-detail'),
    
    path('<str:consultation_id>/documents/', 
         views.ConsultationAttachmentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-documents'),
    path('<str:consultation_id>/documents/<int:pk>/', 
         views.ConsultationAttachmentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-document-detail'),
    
    path('<str:consultation_id>/notes/', 
         views.ConsultationNoteViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-notes'),
    path('<str:consultation_id>/notes/<int:pk>/', 
         views.ConsultationNoteViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-note-detail'),
    
    path('<str:consultation_id>/symptoms/', 
         views.ConsultationSymptomViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='consultation-symptoms'),
    path('<str:consultation_id>/symptoms/<int:pk>/', 
         views.ConsultationSymptomViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='consultation-symptom-detail'),
    
    # Get prescription for consultation
    path('<str:consultation_id>/prescription/', 
         views.ConsultationPrescriptionView.as_view(), 
         name='consultation-prescription'),
    
    # Include router URLs for main consultation operations
    path('', include(router.urls)),
]

