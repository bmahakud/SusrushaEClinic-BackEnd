from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'doctors'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.DoctorProfileViewSet, basename='doctor-profile')

urlpatterns = [
    # Doctor search and statistics
    path('search/', views.DoctorSearchView.as_view(), name='doctor-search'),
    path('stats/', views.DoctorStatsView.as_view(), name='doctor-stats'),
    
    # Doctor-specific nested resources
    path('<str:doctor_id>/education/', 
         views.DoctorEducationViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-education'),
    path('<str:doctor_id>/education/<int:pk>/', 
         views.DoctorEducationViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-education-detail'),
    
    path('<str:doctor_id>/experience/', 
         views.DoctorExperienceViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-experience'),
    path('<str:doctor_id>/experience/<int:pk>/', 
         views.DoctorExperienceViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-experience-detail'),
    
    path('<str:doctor_id>/documents/', 
         views.DoctorDocumentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-documents'),
    path('<str:doctor_id>/documents/<int:pk>/', 
         views.DoctorDocumentViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-document-detail'),
    
    path('<str:doctor_id>/availability/', 
         views.DoctorAvailabilityViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-availability'),
    path('<str:doctor_id>/availability/<int:pk>/', 
         views.DoctorAvailabilityViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-availability-detail'),
    
    path('<str:doctor_id>/schedule/', 
         views.DoctorScheduleViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-schedule'),
    path('<str:doctor_id>/schedule/<int:pk>/', 
         views.DoctorScheduleViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-schedule-detail'),
    
    path('<str:doctor_id>/reviews/', 
         views.DoctorReviewViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='doctor-reviews'),
    path('<str:doctor_id>/reviews/<int:pk>/', 
         views.DoctorReviewViewSet.as_view({
             'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
         }), 
         name='doctor-review-detail'),
    
    # Include router URLs for main doctor profile operations
    path('', include(router.urls)),
]

