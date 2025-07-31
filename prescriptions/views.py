from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import Prescription, PrescriptionMedication, PrescriptionVitalSigns
from .serializers import (
    PrescriptionSerializer, PrescriptionCreateSerializer, PrescriptionUpdateSerializer,
    PrescriptionListSerializer, PrescriptionDetailSerializer, PrescriptionMedicationSerializer,
    PrescriptionVitalSignsSerializer
)

class PrescriptionPagination(PageNumberPagination):
    """Custom pagination for prescription lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsDoctorOrPatientOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all authenticated users to create prescriptions
        if request.method == 'POST':
            return request.user.is_authenticated
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role == 'superadmin':
            return True
        # Doctor can edit/view, patient can view
        if request.user == obj.doctor:
            return True
        if request.method in permissions.SAFE_METHODS and request.user == obj.patient:
            return True
        return False

class PrescriptionViewSet(viewsets.ModelViewSet):
    """Enhanced ViewSet for prescription management"""
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrPatientOrAdmin]
    pagination_class = PrescriptionPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PrescriptionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PrescriptionUpdateSerializer
        elif self.action == 'list':
            return PrescriptionListSerializer
        elif self.action == 'retrieve':
            return PrescriptionDetailSerializer
        return PrescriptionSerializer

    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = Prescription.objects.select_related(
            'doctor', 'patient', 'consultation'
        ).prefetch_related('medications', 'vital_signs')
        
        if user.role == 'superadmin':
            # SuperAdmin can see all prescriptions
            return queryset
        elif user.role == 'admin':
            # Admin can see prescriptions for their clinic
            try:
                assigned_clinic = user.administered_clinic
                return queryset.filter(consultation__clinic=assigned_clinic)
            except:
                return queryset.none()
        elif user.role == 'doctor':
            # Doctors can see prescriptions they created
            return queryset.filter(doctor=user)
        elif user.role == 'patient':
            # Patients can see their own prescriptions
            return queryset.filter(patient=user)
        
        return queryset.none()

    @extend_schema(
        responses={200: PrescriptionDetailSerializer},
        description="Get prescription by ID"
    )
    def retrieve(self, request, pk=None):
        """Get prescription by ID"""
        prescription = self.get_object()
        serializer = self.get_serializer(prescription)
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
        """Create prescription or update if exists"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Check if prescription already exists for this consultation-doctor-patient combination
            consultation_id = request.data.get('consultation')
            patient_id = request.data.get('patient')
            
            if consultation_id and patient_id:
                try:
                    existing_prescription = Prescription.objects.get(
                        consultation_id=consultation_id,
                        doctor=request.user,
                        patient_id=patient_id
                    )
                    # Update existing prescription
                    update_serializer = PrescriptionUpdateSerializer(
                        existing_prescription, 
                        data=request.data, 
                        partial=True,
                        context={'request': request}
                    )
                    if update_serializer.is_valid():
                        prescription = update_serializer.save()
                        response_serializer = PrescriptionDetailSerializer(prescription)
                        return Response({
                            'success': True,
                            'data': response_serializer.data,
                            'message': 'Prescription updated successfully',
                            'timestamp': timezone.now().isoformat()
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'success': False,
                            'error': {
                                'code': 'VALIDATION_ERROR',
                                'message': 'Invalid data provided',
                                'details': update_serializer.errors
                            },
                            'timestamp': timezone.now().isoformat()
                        }, status=status.HTTP_400_BAD_REQUEST)
                except Prescription.DoesNotExist:
                    # Create new prescription
                    prescription = serializer.save()
                    response_serializer = PrescriptionDetailSerializer(prescription)
                    return Response({
                        'success': True,
                        'data': response_serializer.data,
                        'message': 'Prescription created successfully',
                        'timestamp': timezone.now().isoformat()
                    }, status=status.HTTP_201_CREATED)
            else:
                # Create new prescription without consultation/patient check
                prescription = serializer.save()
                response_serializer = PrescriptionDetailSerializer(prescription)
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

    @extend_schema(
        request=PrescriptionUpdateSerializer,
        responses={200: PrescriptionSerializer},
        description="Update prescription"
    )
    def update(self, request, pk=None):
        """Update prescription"""
        prescription = self.get_object()
        serializer = self.get_serializer(prescription, data=request.data, partial=True)
        if serializer.is_valid():
            prescription = serializer.save()
            response_serializer = PrescriptionDetailSerializer(prescription)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Prescription updated successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid data provided',
                'details': serializer.errors
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='consultation/(?P<consultation_id>[^/.]+)')
    def by_consultation(self, request, consultation_id=None):
        """Get prescription for a specific consultation"""
        try:
            prescription = Prescription.objects.get(
                consultation_id=consultation_id,
                doctor=request.user
            )
            serializer = PrescriptionDetailSerializer(prescription)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Prescription retrieved successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        except Prescription.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Prescription not found for this consultation'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='patient/(?P<patient_id>[^/.]+)')
    def by_patient(self, request, patient_id=None):
        """List all prescriptions for a given patient"""
        prescriptions = self.get_queryset().filter(patient_id=patient_id)
        page = self.paginate_queryset(prescriptions)
        
        if page is not None:
            serializer = PrescriptionListSerializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Patient prescriptions retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = PrescriptionListSerializer(prescriptions, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Patient prescriptions retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """Finalize a prescription (mark as not draft)"""
        prescription = self.get_object()
        prescription.is_draft = False
        prescription.is_finalized = True
        prescription.save()
        
        serializer = PrescriptionDetailSerializer(prescription)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescription finalized successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def save_draft(self, request, pk=None):
        """Save prescription as draft"""
        prescription = self.get_object()
        prescription.is_draft = True
        prescription.is_finalized = False
        prescription.save()
        
        serializer = PrescriptionDetailSerializer(prescription)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Prescription saved as draft',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def drafts(self, request):
        """Get all draft prescriptions for the current user"""
        drafts = self.get_queryset().filter(is_draft=True)
        page = self.paginate_queryset(drafts)
        
        if page is not None:
            serializer = PrescriptionListSerializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Draft prescriptions retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = PrescriptionListSerializer(drafts, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Draft prescriptions retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def finalized(self, request):
        """Get all finalized prescriptions for the current user"""
        finalized = self.get_queryset().filter(is_finalized=True)
        page = self.paginate_queryset(finalized)
        
        if page is not None:
            serializer = PrescriptionListSerializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Finalized prescriptions retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = PrescriptionListSerializer(finalized, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Finalized prescriptions retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

class PrescriptionMedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for prescription medications"""
    serializer_class = PrescriptionMedicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter medications by prescription"""
        prescription_id = self.kwargs.get('prescription_pk')
        return PrescriptionMedication.objects.filter(prescription_id=prescription_id)

    def perform_create(self, serializer):
        """Create medication for prescription"""
        prescription_id = self.kwargs.get('prescription_pk')
        prescription = Prescription.objects.get(id=prescription_id)
        serializer.save(prescription=prescription)

class PrescriptionVitalSignsViewSet(viewsets.ModelViewSet):
    """ViewSet for prescription vital signs"""
    serializer_class = PrescriptionVitalSignsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter vital signs by prescription"""
        prescription_id = self.kwargs.get('prescription_pk')
        return PrescriptionVitalSigns.objects.filter(prescription_id=prescription_id)

    def perform_create(self, serializer):
        """Create vital signs for prescription"""
        prescription_id = self.kwargs.get('prescription_pk')
        prescription = Prescription.objects.get(id=prescription_id)
        serializer.save(prescription=prescription)

