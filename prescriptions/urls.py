from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'prescriptions'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.PrescriptionViewSet, basename='prescription')
router.register(r'reminders', views.MedicationReminderViewSet, basename='medication-reminder')

urlpatterns = [
    # Prescription search and statistics
    path('search/', views.PrescriptionSearchView.as_view(), name='prescription-search'),
    path('stats/', views.PrescriptionStatsView.as_view(), name='prescription-stats'),
    path('medications/', views.MedicationListView.as_view(), name='medication-list'),
    
    # Prescription-specific nested resources
    path('<str:prescription_id>/medications/', 
         views.MedicationViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='prescription-medications'),
    path('<str:prescription_id>/medications/<int:pk>/', 
         views.MedicationViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='prescription-medication-detail'),
    
    path('<str:prescription_id>/documents/', 
         views.PrescriptionDocumentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='prescription-documents'),
    path('<str:prescription_id>/documents/<int:pk>/', 
         views.PrescriptionDocumentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='prescription-document-detail'),
    
    path('<str:prescription_id>/notes/', 
         views.PrescriptionNoteViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='prescription-notes'),
    path('<str:prescription_id>/notes/<int:pk>/', 
         views.PrescriptionNoteViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='prescription-note-detail'),
    
    # Include router URLs for main prescription operations
    path('', include(router.urls)),
]

