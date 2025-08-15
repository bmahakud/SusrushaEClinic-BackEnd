from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from datetime import datetime, timedelta

from authentication.models import User
from .models import PatientProfile, MedicalRecord, PatientDocument, PatientNote
from .serializers import (
    PatientProfileSerializer, PatientProfileCreateSerializer,
    MedicalRecordSerializer, MedicalRecordCreateSerializer,
    PatientDocumentSerializer, PatientDocumentUploadSerializer,
    PatientNoteSerializer, PatientNoteCreateSerializer,
    PatientListSerializer, PatientSearchSerializer, PatientStatsSerializer
)
from consultations.models import Consultation
from consultations.serializers import ConsultationListSerializer


class PatientPagination(PageNumberPagination):
    """Custom pagination for patient lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PatientMedicalRecordsView(APIView):
    """View for patient to get their medical records"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('record_type', OpenApiTypes.STR, description='Filter by record type'),
            OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by field (e.g., -date_recorded)'),
            OpenApiParameter('page', OpenApiTypes.INT, description='Page number'),
            OpenApiParameter('page_size', OpenApiTypes.INT, description='Number of items per page'),
        ],
        responses={200: MedicalRecordSerializer(many=True)},
        description="Get medical records for the logged-in patient"
    )
    def get(self, request):
        """Get medical records for the logged-in patient"""
        # Check if user is a patient
        if request.user.role != 'patient':
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Only patients can access this endpoint'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get medical records for the patient
        queryset = MedicalRecord.objects.filter(patient=request.user).select_related('recorded_by')
        
        # Apply filters
        record_type = request.query_params.get('record_type')
        if record_type:
            queryset = queryset.filter(record_type=record_type)
        
        # Apply ordering
        ordering = request.query_params.get('ordering', '-date_recorded')
        queryset = queryset.order_by(ordering)
        
        # Apply pagination
        paginator = PatientPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = MedicalRecordSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = MedicalRecordSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Patient medical records retrieved successfully',
            'timestamp': timezone.now().isoformat()
        })


class PatientProfileViewSet(ModelViewSet):
    """ViewSet for patient profile management"""
    queryset = PatientProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PatientPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['blood_group']
    search_fields = ['user__name', 'user__phone', 'user__email']
    ordering_fields = ['created_at', 'user__name', 'date_of_birth']
    ordering = ['-created_at']
    
    def get_object(self):
        """Override to handle patient profile ID lookup"""
        patient_id = self.kwargs.get('pk')
        try:
            # First try to find patient profile by its own ID (integer)
            if patient_id.isdigit():
                patient_profile = PatientProfile.objects.get(id=int(patient_id))
                self.check_object_permissions(self.request, patient_profile)
                return patient_profile
        except (PatientProfile.DoesNotExist, ValueError):
            pass
        
        try:
            # If not found by ID, try to find by user ID (string)
            patient_profile = PatientProfile.objects.get(user__id=patient_id)
            self.check_object_permissions(self.request, patient_profile)
            return patient_profile
        except PatientProfile.DoesNotExist:
            from django.http import Http404
            raise Http404("Patient profile not found")
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PatientProfileCreateSerializer
        elif self.action == 'list':
            return PatientListSerializer
        return PatientProfileSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role and custom filters"""
        user = self.request.user
        queryset = PatientProfile.objects.select_related('user')
        
        if user.role == 'patient':
            # Patients can only see their own profile
            return queryset.filter(user=user)
        elif user.role == 'doctor':
            # Doctors can see patients they have consulted
            return queryset.filter(
                user__patient_consultations__doctor=user
            ).distinct()
        elif user.role in ['admin', 'superadmin']:
            # Admins can see all patients
            pass
        else:
            return queryset.none()
        
        # Apply custom filters
        city = self.request.query_params.get('city')
        state = self.request.query_params.get('state')
        gender = self.request.query_params.get('gender')
        age_min = self.request.query_params.get('age_min')
        age_max = self.request.query_params.get('age_max')
        
        if city:
            queryset = queryset.filter(user__city__icontains=city)
        
        if state:
            queryset = queryset.filter(user__state__icontains=state)
        
        if gender:
            queryset = queryset.filter(user__gender=gender)
        
        # Apply age filters
        if age_min or age_max:
            today = timezone.now().date()
            
            if age_min:
                max_birth_date = today - timedelta(days=int(age_min) * 365)
                queryset = queryset.filter(user__date_of_birth__lte=max_birth_date)
            
            if age_max:
                min_birth_date = today - timedelta(days=(int(age_max) + 1) * 365)
                queryset = queryset.filter(user__date_of_birth__gte=min_birth_date)
        
        return queryset
    
    @extend_schema(
        responses={200: PatientProfileSerializer},
        description="Get patient profile by ID"
    )
    def retrieve(self, request, pk=None):
        """Get patient profile by ID"""
        patient = self.get_object()
        serializer = PatientProfileSerializer(patient)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Patient profile retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        responses={200: PatientListSerializer(many=True)},
        description="List all patients with pagination and filtering"
    )
    def list(self, request):
        """List patients with pagination and filtering"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=PatientProfileCreateSerializer,
        responses={201: PatientProfileSerializer},
        description="Create patient profile"
    )
    def create(self, request):
        """Create patient profile"""
        # Check if patient profile already exists
        if hasattr(request.user, 'patient_profile'):
            return Response({
                'success': False,
                'error': {
                    'code': 'PROFILE_EXISTS',
                    'message': 'Patient profile already exists'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            patient_profile = serializer.save()
            response_serializer = PatientProfileSerializer(patient_profile)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Patient profile created successfully',
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
        request=PatientProfileSerializer,
        responses={200: PatientProfileSerializer},
        description="Update patient profile"
    )
    def update(self, request, pk=None):
        """Update patient profile"""
        patient = self.get_object()
        serializer = PatientProfileSerializer(patient, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Patient profile updated successfully',
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

    @extend_schema(
        responses={200: dict, 404: dict},
        description="Delete patient profile"
    )
    def destroy(self, request, pk=None):
        """Delete patient profile"""
        try:
            patient = self.get_object()
            patient.delete()
            return Response({
                'success': True,
                'data': {
                    'patient_id': str(patient.id),
                    'user_id': str(patient.user.id),
                    'status': 'deleted'
                },
                'message': 'Patient profile deleted successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'DELETE_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientMedicalRecordViewSet(ModelViewSet):
    """ViewSet for patient medical records"""
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PatientPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['date_recorded', 'created_at']
    ordering = ['-date_recorded']
    
    def get_queryset(self):
        """Get medical records for specific patient"""
        patient_id = self.kwargs.get('patient_id')
        return MedicalRecord.objects.filter(patient_id=patient_id).select_related('recorded_by')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return MedicalRecordCreateSerializer
        return MedicalRecordSerializer
    
    @extend_schema(
        responses={200: MedicalRecordSerializer(many=True)},
        description="List medical records for a patient"
    )
    def list(self, request, patient_id=None):
        """List medical records for a patient"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Medical records retrieved successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'LIST_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        request=MedicalRecordCreateSerializer,
        responses={201: MedicalRecordSerializer},
        description="Create medical record for a patient"
    )
    def create(self, request, patient_id=None):
        """Create medical record for a patient"""
        try:
            # Check if patient exists
            from authentication.models import User
            patient = User.objects.filter(id=patient_id, role='patient').first()
            if not patient:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'PATIENT_NOT_FOUND',
                        'message': 'Patient not found'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                medical_record = serializer.save(patient_id=patient_id)
                response_serializer = MedicalRecordSerializer(medical_record)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Medical record created successfully',
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
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'CREATE_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        responses={200: dict, 404: dict},
        description="Delete medical record"
    )
    def destroy(self, request, pk=None, patient_id=None):
        """Delete medical record"""
        try:
            medical_record = self.get_object()
            medical_record.delete()
            return Response({
                'success': True,
                'data': {
                    'medical_record_id': str(medical_record.id),
                    'status': 'deleted'
                },
                'message': 'Medical record deleted successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'DELETE_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientDocumentViewSet(ModelViewSet):
    """ViewSet for patient documents"""
    serializer_class = PatientDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PatientPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'document_type']
    ordering_fields = ['uploaded_at', 'document_type']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        """Get documents for specific patient"""
        patient_id = self.kwargs.get('patient_id')
        return PatientDocument.objects.filter(patient_id=patient_id).select_related('verified_by')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PatientDocumentUploadSerializer
        return PatientDocumentSerializer
    
    @extend_schema(
        responses={200: PatientDocumentSerializer(many=True)},
        description="List documents for a patient"
    )
    def list(self, request, patient_id=None):
        """List documents for a patient"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Documents retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=PatientDocumentUploadSerializer,
        responses={201: PatientDocumentSerializer},
        description="Upload document for a patient"
    )
    def create(self, request, patient_id=None):
        """Upload document for a patient"""
        try:
            # Check if patient exists
            from authentication.models import User
            patient = User.objects.filter(id=patient_id, role='patient').first()
            if not patient:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'PATIENT_NOT_FOUND',
                        'message': 'Patient not found'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                document = serializer.save()
                response_serializer = PatientDocumentSerializer(document)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Document uploaded successfully',
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
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'UPLOAD_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        responses={200: dict, 404: dict},
        description="Delete patient document"
    )
    def destroy(self, request, pk=None, patient_id=None):
        """Delete patient document"""
        try:
            document = self.get_object()
            document.delete()
            return Response({
                'success': True,
                'data': {
                    'document_id': str(document.id),
                    'status': 'deleted'
                },
                'message': 'Patient document deleted successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'DELETE_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientNoteViewSet(ModelViewSet):
    """ViewSet for patient notes"""
    serializer_class = PatientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PatientPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['note']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get notes for specific patient"""
        patient_id = self.kwargs.get('patient_id')
        queryset = PatientNote.objects.filter(patient_id=patient_id).select_related('created_by')
        
        # Filter private notes based on user role
        user = self.request.user
        if user.role == 'patient':
            # Patients can see all notes
            return queryset
        elif user.role == 'doctor':
            # Doctors can see non-private notes and their own notes
            return queryset.filter(Q(is_private=False) | Q(created_by=user))
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PatientNoteCreateSerializer
        return PatientNoteSerializer

    @extend_schema(
        responses={200: PatientNoteSerializer(many=True)},
        description="List notes for a patient"
    )
    def list(self, request, patient_id=None):
        """List notes for a patient"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Patient notes retrieved successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'LIST_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        request=PatientNoteCreateSerializer,
        responses={201: PatientNoteSerializer},
        description="Create note for a patient"
    )
    def create(self, request, patient_id=None):
        """Create note for a patient"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            note = serializer.save()
            response_serializer = PatientNoteSerializer(note)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Patient note created successfully',
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
        responses={200: dict, 404: dict},
        description="Delete patient note"
    )
    def destroy(self, request, pk=None, patient_id=None):
        """Delete patient note"""
        try:
            note = self.get_object()
            note.delete()
            return Response({
                'success': True,
                'data': {
                    'note_id': str(note.id),
                    'status': 'deleted'
                },
                'message': 'Patient note deleted successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'DELETE_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientConsultationView(APIView):
    """View for fetching patient consultations"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by consultation status'),
            OpenApiParameter('doctor', OpenApiTypes.STR, description='Filter by doctor ID'),
            OpenApiParameter('date_from', OpenApiTypes.DATE, description='Filter from date (YYYY-MM-DD)'),
            OpenApiParameter('date_to', OpenApiTypes.DATE, description='Filter to date (YYYY-MM-DD)'),
            OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by field (e.g., -created_at)'),
            OpenApiParameter('page', OpenApiTypes.INT, description='Page number'),
            OpenApiParameter('page_size', OpenApiTypes.INT, description='Number of items per page'),
        ],
        responses={200: ConsultationListSerializer(many=True)},
        description="Get consultations for a specific patient"
    )
    def get(self, request, patient_id=None):
        """Get consultations for a specific patient"""
        try:
            # Check if patient exists
            from authentication.models import User
            patient = User.objects.filter(id=patient_id, role='patient').first()
            if not patient:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'PATIENT_NOT_FOUND',
                        'message': 'Patient not found'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get consultations for the patient
            queryset = Consultation.objects.filter(patient=patient).select_related(
                'doctor', 'patient', 'clinic'
            )
            
            # Apply filters
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            doctor_filter = request.query_params.get('doctor')
            if doctor_filter:
                queryset = queryset.filter(doctor_id=doctor_filter)
            
            date_from = request.query_params.get('date_from')
            if date_from:
                try:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                    queryset = queryset.filter(scheduled_at__date__gte=date_from)
                except ValueError:
                    return Response({
                        'success': False,
                        'error': {
                            'code': 'INVALID_DATE_FORMAT',
                            'message': 'Invalid date format. Use YYYY-MM-DD'
                        },
                        'timestamp': timezone.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            date_to = request.query_params.get('date_to')
            if date_to:
                try:
                    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                    queryset = queryset.filter(scheduled_at__date__lte=date_to)
                except ValueError:
                    return Response({
                        'success': False,
                        'error': {
                            'code': 'INVALID_DATE_FORMAT',
                            'message': 'Invalid date format. Use YYYY-MM-DD'
                        },
                        'timestamp': timezone.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Apply ordering
            ordering = request.query_params.get('ordering', '-created_at')
            queryset = queryset.order_by(ordering)
            
            # Apply pagination
            paginator = PatientPagination()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                serializer = ConsultationListSerializer(page, many=True)
                return paginator.get_paginated_response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Patient consultations retrieved successfully',
                    'timestamp': timezone.now().isoformat()
                })
            
            serializer = ConsultationListSerializer(queryset, many=True)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Patient consultations retrieved successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'FETCH_ERROR',
                    'message': str(e)
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientSearchView(APIView):
    """Search patients with advanced filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='Search query'),
            OpenApiParameter('gender', OpenApiTypes.STR, description='Gender filter'),
            OpenApiParameter('blood_group', OpenApiTypes.STR, description='Blood group filter'),
            OpenApiParameter('age_min', OpenApiTypes.INT, description='Minimum age'),
            OpenApiParameter('age_max', OpenApiTypes.INT, description='Maximum age'),
            OpenApiParameter('city', OpenApiTypes.STR, description='City filter'),
            OpenApiParameter('state', OpenApiTypes.STR, description='State filter'),
        ],
        responses={200: PatientListSerializer(many=True)},
        description="Search patients with advanced filters"
    )
    def get(self, request):
        """Search patients with advanced filters"""
        serializer = PatientSearchSerializer(data=request.query_params)
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
        queryset = PatientProfile.objects.select_related('user')
        
        # Apply role-based filtering
        user = request.user
        if user.role == 'doctor':
            queryset = queryset.filter(
                user__patient_consultations__doctor=user
            ).distinct()
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
                Q(user__name__icontains=query) |
                Q(user__phone__icontains=query) |
                Q(user__email__icontains=query)
            )
        
        if search_data.get('gender'):
            queryset = queryset.filter(gender=search_data['gender'])
        
        if search_data.get('blood_group'):
            queryset = queryset.filter(blood_group=search_data['blood_group'])
        
        if search_data.get('city'):
            queryset = queryset.filter(user__city__icontains=search_data['city'])
        
        if search_data.get('state'):
            queryset = queryset.filter(user__state__icontains=search_data['state'])
        
        # Apply age filters
        if search_data.get('age_min') or search_data.get('age_max'):
            today = timezone.now().date()
            
            if search_data.get('age_min'):
                max_birth_date = today - timedelta(days=search_data['age_min'] * 365)
                queryset = queryset.filter(date_of_birth__lte=max_birth_date)
            
            if search_data.get('age_max'):
                min_birth_date = today - timedelta(days=(search_data['age_max'] + 1) * 365)
                queryset = queryset.filter(date_of_birth__gte=min_birth_date)
        
        # Paginate results
        paginator = PatientPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = PatientListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Search results retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = PatientListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Search results retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class PatientStatsView(APIView):
    """Get patient statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: PatientStatsSerializer},
        description="Get patient statistics and analytics"
    )
    def get(self, request):
        """Get patient statistics"""
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
        total_patients = PatientProfile.objects.count()
        
        # New patients this month
        this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_patients_this_month = PatientProfile.objects.filter(
            created_at__gte=this_month
        ).count()
        
        # Active patients (had consultation in last 6 months)
        six_months_ago = timezone.now() - timedelta(days=180)
        active_patients = PatientProfile.objects.filter(
            user__patient_consultations__created_at__gte=six_months_ago
        ).distinct().count()
        
        # Gender distribution
        gender_distribution = dict(
            PatientProfile.objects.values('user__gender').annotate(
                count=Count('user__gender')
            ).values_list('user__gender', 'count')
        )
        
        # Age distribution
        today = timezone.now().date()
        age_ranges = {
            '0-18': 0, '19-30': 0, '31-45': 0, '46-60': 0, '60+': 0
        }
        
        for patient in PatientProfile.objects.filter(user__date_of_birth__isnull=False):
            age = (today - patient.user.date_of_birth).days // 365
            if age <= 18:
                age_ranges['0-18'] += 1
            elif age <= 30:
                age_ranges['19-30'] += 1
            elif age <= 45:
                age_ranges['31-45'] += 1
            elif age <= 60:
                age_ranges['46-60'] += 1
            else:
                age_ranges['60+'] += 1
        
        # Blood group distribution
        blood_group_distribution = dict(
            PatientProfile.objects.values('blood_group').annotate(
                count=Count('blood_group')
            ).values_list('blood_group', 'count')
        )
        
        # Top cities
        top_cities = list(
            User.objects.filter(role='patient').values('city').annotate(
                count=Count('city')
            ).order_by('-count')[:10].values_list('city', 'count')
        )
        
        # Consultation stats
        from consultations.models import Consultation
        consultation_stats = {
            'total_consultations': Consultation.objects.count(),
            'avg_consultations_per_patient': Consultation.objects.count() / max(total_patients, 1),
            'consultation_completion_rate': 0  # Calculate based on your business logic
        }
        
        stats_data = {
            'total_patients': total_patients,
            'new_patients_this_month': new_patients_this_month,
            'active_patients': active_patients,
            'gender_distribution': gender_distribution,
            'age_distribution': age_ranges,
            'blood_group_distribution': blood_group_distribution,
            'top_cities': top_cities,
            'consultation_stats': consultation_stats
        }
        
        serializer = PatientStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Patient statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

