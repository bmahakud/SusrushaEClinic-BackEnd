from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'eclinic'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.ClinicViewSet, basename='clinic')

urlpatterns = [
    # Clinic search and statistics
    path('search/', views.ClinicSearchView.as_view(), name='clinic-search'),
    path('stats/', views.ClinicStatsView.as_view(), name='clinic-stats'),
    path('analytics/', views.ClinicAnalyticsView.as_view(), name='clinic-analytics'),
    path('nearby/', views.NearbyClinicView.as_view(), name='nearby-clinics'),
    
    # Global medication management (Super Admin only)
    path('medications/', views.GlobalMedicationViewSet.as_view({
        'get': 'list', 'post': 'create'
    }), name='global-medications'),
    path('medications/<int:pk>/', views.GlobalMedicationViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='global-medication-detail'),
    path('medications/search/', views.GlobalMedicationViewSet.as_view({
        'get': 'search_medications'
    }), name='global-medication-search'),
    path('medications/bulk-create/', views.GlobalMedicationViewSet.as_view({
        'post': 'bulk_create_medications'
    }), name='global-medication-bulk-create'),
    
    # Clinic-specific nested resources
    path('<str:clinic_id>/services/', views.ClinicServiceViewSet.as_view({
        'get': 'list', 'post': 'create'
    }), name='clinic-services'),
    path('<str:clinic_id>/services/<int:pk>/', 
         views.ClinicServiceViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='clinic-service-detail'),
    
    path('<str:clinic_id>/inventory/', views.ClinicInventoryViewSet.as_view({
        'get': 'list', 'post': 'create'
    }), name='clinic-inventory'),
    path('<str:clinic_id>/inventory/<int:pk>/', 
         views.ClinicInventoryViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='clinic-inventory-detail'),
    
    # New medication search endpoints
    path('<str:clinic_id>/inventory/medications/search/', 
         views.ClinicInventoryViewSet.as_view({'get': 'search_medications'}), 
         name='clinic-inventory-medication-search'),
    path('<str:clinic_id>/inventory/medications/auto-create/', 
         views.ClinicInventoryViewSet.as_view({'post': 'auto_create_medication'}), 
         name='clinic-inventory-medication-auto-create'),
    
    path('<str:clinic_id>/appointments/', views.ClinicAppointmentViewSet.as_view({
        'get': 'list', 'post': 'create'
    }), name='clinic-appointments'),
    path('<str:clinic_id>/appointments/<int:pk>/', 
         views.ClinicAppointmentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='clinic-appointment-detail'),
    
    path('<str:clinic_id>/reviews/', views.ClinicReviewViewSet.as_view({
        'get': 'list', 'post': 'create'
    }), name='clinic-reviews'),
    path('<str:clinic_id>/reviews/<int:pk>/', 
         views.ClinicReviewViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='clinic-review-detail'),
    
    path('<str:clinic_id>/documents/', views.ClinicDocumentViewSet.as_view({
        'get': 'list', 'post': 'create'
    }), name='clinic-documents'),
    path('<str:clinic_id>/documents/<int:pk>/', 
         views.ClinicDocumentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='clinic-document-detail'),
    
    # Include router URLs
    path('', include(router.urls)),
]

