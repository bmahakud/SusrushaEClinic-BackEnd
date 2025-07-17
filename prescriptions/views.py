from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from datetime import datetime, timedelta

from authentication.models import User
from .models import (
    Prescription, Medication, MedicationReminder, 
    PrescriptionAttachment, PrescriptionNote
)
from .serializers import (
    PrescriptionSerializer, PrescriptionCreateSerializer,
    MedicationSerializer, MedicationCreateSerializer, MedicationDetailSerializer,
    MedicationReminderSerializer, MedicationReminderCreateSerializer,
    PrescriptionAttachmentSerializer, PrescriptionAttachmentCreateSerializer,
    PrescriptionNoteSerializer, PrescriptionNoteCreateSerializer,
    PrescriptionListSerializer, PrescriptionSearchSerializer, PrescriptionStatsSerializer
)


class PrescriptionPagination(PageNumberPagination):
    """Custom pagination for prescription lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PrescriptionViewSet(ModelViewSet):
    """ViewSet for prescription management"""
    queryset = Prescription.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PrescriptionPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['prescription_number', 'patient__name', 'doctor__name', 'diagnosis']
    ordering_fields = ['created_at', 'follow_up_date', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PrescriptionCreateSerializer
        elif self.action == 'list':
            return PrescriptionListSerializer
        return PrescriptionSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = Prescription.objects.select_related('patient', 'doctor', 'consultation')
        
        if user.role == 'patient':
            # Patients can only see their own prescriptions
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            # Doctors can see prescriptions they created
            return queryset.filter(doctor=user)
        elif user.role in ['admin', 'superadmin']:
            # Admins can see all prescriptions
            return queryset
        
        return queryset.none()
    
    @extend_schema(
        responses={200: PrescriptionSerializer},
        description="Get prescription by ID"
    )
    def retrieve(self, request, pk=None):
        """Get prescription by ID"""
        prescription = self.get_object()
        serializer = PrescriptionSerializer(prescription)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescription retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        responses={200: PrescriptionListSerializer(many=True)},
        description="List all prescriptions with pagination and filtering"
    )
    def list(self, request):
        """List prescriptions with pagination and filtering"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Prescriptions retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescriptions retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=PrescriptionCreateSerializer,
        responses={201: PrescriptionSerializer},
        description="Create prescription"
    )
    def create(self, request):
        """Create prescription"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            prescription = serializer.save()
            response_serializer = PrescriptionSerializer(prescription)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Prescription created successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid data provided',
                'details': serializer.errors
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def dispense(self, request, pk=None):
        """Mark prescription as dispensed"""
        prescription = self.get_object()
        
        if prescription.status != 'active':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Only active prescriptions can be dispensed'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        prescription.status = 'dispensed'
        prescription.dispensed_at = timezone.now()
        prescription.dispensed_by = request.data.get('dispensed_by', '')
        prescription.save()
        
        serializer = PrescriptionSerializer(prescription)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescription marked as dispensed',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark prescription as completed"""
        prescription = self.get_object()
        
        prescription.status = 'completed'
        prescription.save()
        
        serializer = PrescriptionSerializer(prescription)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescription marked as completed',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class MedicationViewSet(ModelViewSet):
    """ViewSet for medication management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get medications for specific prescription"""
        prescription_id = self.kwargs.get('prescription_id')
        return Medication.objects.filter(prescription_id=prescription_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return MedicationCreateSerializer
        return MedicationSerializer


class MedicationReminderViewSet(ModelViewSet):
    """ViewSet for medication reminders"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reminders for authenticated user"""
        user = self.request.user
        if user.role == 'patient':
            return MedicationReminder.objects.filter(patient=user)
        elif user.role in ['admin', 'superadmin']:
            return MedicationReminder.objects.all()
        return MedicationReminder.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return MedicationReminderCreateSerializer
        return MedicationReminderSerializer


class PrescriptionDocumentViewSet(ModelViewSet):
    """ViewSet for prescription documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get documents for specific prescription"""
        prescription_id = self.kwargs.get('prescription_id')
        return PrescriptionDocument.objects.filter(prescription_id=prescription_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PrescriptionDocumentCreateSerializer
        return PrescriptionDocumentSerializer


class PrescriptionNoteViewSet(ModelViewSet):
    """ViewSet for prescription notes"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notes for specific prescription"""
        prescription_id = self.kwargs.get('prescription_id')
        queryset = PrescriptionNote.objects.filter(prescription_id=prescription_id)
        
        # Filter private notes based on user role
        user = self.request.user
        if user.role == 'patient':
            # Patients can see non-private notes
            return queryset.filter(is_private=False)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PrescriptionNoteCreateSerializer
        return PrescriptionNoteSerializer


class PrescriptionSearchView(APIView):
    """Search prescriptions with advanced filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='Search query'),
            OpenApiParameter('patient_id', OpenApiTypes.INT, description='Patient ID filter'),
            OpenApiParameter('doctor_id', OpenApiTypes.INT, description='Doctor ID filter'),
            OpenApiParameter('consultation_id', OpenApiTypes.STR, description='Consultation ID filter'),
            OpenApiParameter('prescription_number', OpenApiTypes.STR, description='Prescription number'),
            OpenApiParameter('status', OpenApiTypes.STR, description='Status filter'),
            OpenApiParameter('is_digital', OpenApiTypes.BOOL, description='Digital prescription filter'),
            OpenApiParameter('date_from', OpenApiTypes.DATE, description='Start date filter'),
            OpenApiParameter('date_to', OpenApiTypes.DATE, description='End date filter'),
            OpenApiParameter('medicine_name', OpenApiTypes.STR, description='Medicine name filter'),
        ],
        responses={200: PrescriptionListSerializer(many=True)},
        description="Search prescriptions with advanced filters"
    )
    def get(self, request):
        """Search prescriptions with advanced filters"""
        serializer = PrescriptionSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid search parameters',
                    'details': serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build query
        queryset = Prescription.objects.select_related('patient', 'doctor', 'consultation')
        
        # Apply role-based filtering
        user = request.user
        if user.role == 'patient':
            queryset = queryset.filter(patient=user)
        elif user.role == 'doctor':
            queryset = queryset.filter(doctor=user)
        elif user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Apply search filters
        search_data = serializer.validated_data
        
        if search_data.get('query'):
            query = search_data['query']
            queryset = queryset.filter(
                Q(patient__name__icontains=query) |
                Q(doctor__name__icontains=query) |
                Q(prescription_number__icontains=query) |
                Q(diagnosis__icontains=query)
            )
        
        if search_data.get('patient_id'):
            queryset = queryset.filter(patient_id=search_data['patient_id'])
        
        if search_data.get('doctor_id'):
            queryset = queryset.filter(doctor_id=search_data['doctor_id'])
        
        if search_data.get('consultation_id'):
            queryset = queryset.filter(consultation_id=search_data['consultation_id'])
        
        if search_data.get('prescription_number'):
            queryset = queryset.filter(prescription_number__icontains=search_data['prescription_number'])
        
        if search_data.get('status'):
            queryset = queryset.filter(status=search_data['status'])
        
        if search_data.get('is_digital') is not None:
            queryset = queryset.filter(is_digital=search_data['is_digital'])
        
        if search_data.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=search_data['date_from'])
        
        if search_data.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=search_data['date_to'])
        
        if search_data.get('medicine_name'):
            queryset = queryset.filter(
                medications__medicine_name__icontains=search_data['medicine_name']
            ).distinct()
        
        # Paginate results
        paginator = PrescriptionPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = PrescriptionListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Search results retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = PrescriptionListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Search results retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class PrescriptionStatsView(APIView):
    """Get prescription statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: PrescriptionStatsSerializer},
        description="Get prescription statistics and analytics"
    )
    def get(self, request):
        """Get prescription statistics"""
        # Check permissions
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate statistics
        total_prescriptions = Prescription.objects.count()
        active_prescriptions = Prescription.objects.filter(status='active').count()
        completed_prescriptions = Prescription.objects.filter(status='completed').count()
        digital_prescriptions = Prescription.objects.filter(is_digital=True).count()
        total_medications = Medication.objects.count()
        
        # Most prescribed medicines
        most_prescribed = list(
            Medication.objects.values('medicine_name').annotate(
                count=Count('medicine_name')
            ).order_by('-count')[:10].values_list('medicine_name', 'count')
        )
        
        # Prescription trends (last 12 months)
        prescription_trends = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_prescriptions = Prescription.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            prescription_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'prescriptions': month_prescriptions
            })
        
        # Doctor prescription stats
        doctor_stats = dict(
            Prescription.objects.values('doctor__name').annotate(
                count=Count('doctor')
            ).order_by('-count')[:10].values_list('doctor__name', 'count')
        )
        
        stats_data = {
            'total_prescriptions': total_prescriptions,
            'active_prescriptions': active_prescriptions,
            'completed_prescriptions': completed_prescriptions,
            'digital_prescriptions': digital_prescriptions,
            'total_medications': total_medications,
            'most_prescribed_medicines': most_prescribed,
            'prescription_trends': prescription_trends,
            'doctor_prescription_stats': doctor_stats
        }
        
        serializer = PrescriptionStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescription statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class MedicationListView(APIView):
    """List all medications across prescriptions"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: MedicationDetailSerializer(many=True)},
        description="List all medications with prescription details"
    )
    def get(self, request):
        """List all medications"""
        user = request.user
        
        if user.role == 'patient':
            queryset = Medication.objects.filter(prescription__patient=user)
        elif user.role == 'doctor':
            queryset = Medication.objects.filter(prescription__doctor=user)
        elif user.role in ['admin', 'superadmin']:
            queryset = Medication.objects.all()
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = queryset.select_related('prescription__patient', 'prescription__doctor')
        
        # Apply search filter if provided
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(medicine_name__icontains=search) |
                Q(generic_name__icontains=search)
            )
        
        # Paginate results
        paginator = PrescriptionPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = MedicationDetailSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Medications retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = MedicationDetailSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Medications retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

