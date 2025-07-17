from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from datetime import datetime, timedelta

from authentication.models import User
from .models import (
    DoctorProfile, DoctorEducation, DoctorExperience, 
    DoctorDocument, DoctorAvailability, DoctorSchedule, DoctorReview
)
from .serializers import (
    DoctorProfileSerializer, DoctorProfileCreateSerializer,
    DoctorEducationSerializer, DoctorExperienceSerializer,
    DoctorDocumentSerializer, DoctorAvailabilitySerializer,
    DoctorScheduleSerializer, DoctorReviewSerializer,
    DoctorListSerializer, DoctorSearchSerializer, DoctorStatsSerializer,
    DoctorScheduleCreateSerializer, DoctorAvailabilityCreateSerializer
)


class DoctorPagination(PageNumberPagination):
    """Custom pagination for doctor lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class DoctorProfileViewSet(ModelViewSet):
    """ViewSet for doctor profile management"""
    queryset = DoctorProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DoctorPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__name', 'specialization', 'qualification']
    ordering_fields = ['created_at', 'user__name', 'rating', 'consultation_fee']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DoctorProfileCreateSerializer
        elif self.action == 'list':
            return DoctorListSerializer
        return DoctorProfileSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = DoctorProfile.objects.select_related('user')
        
        if user.role == 'doctor':
            # Doctors can only see their own profile
            return queryset.filter(user=user)
        elif user.role == 'patient':
            # Patients can see all verified and active doctors
            return queryset.filter(is_verified=True, is_active=True)
        elif user.role in ['admin', 'superadmin']:
            # Admins can see all doctors
            return queryset
        
        return queryset.filter(is_verified=True, is_active=True)
    
    @extend_schema(
        responses={200: DoctorProfileSerializer},
        description="Get doctor profile by ID"
    )
    def retrieve(self, request, pk=None):
        """Get doctor profile by ID"""
        doctor = self.get_object()
        serializer = DoctorProfileSerializer(doctor)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Doctor profile retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        responses={200: DoctorListSerializer(many=True)},
        description="List all doctors with pagination and filtering"
    )
    def list(self, request):
        """List doctors with pagination and filtering"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Doctors retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Doctors retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=DoctorProfileCreateSerializer,
        responses={201: DoctorProfileSerializer},
        description="Create doctor profile"
    )
    def create(self, request):
        """Create doctor profile"""
        # Check if doctor profile already exists
        if hasattr(request.user, 'doctor_profile'):
            return Response({
                'success': False,
                'error': {
                    'code': 'PROFILE_EXISTS',
                    'message': 'Doctor profile already exists'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            doctor_profile = serializer.save()
            response_serializer = DoctorProfileSerializer(doctor_profile)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Doctor profile created successfully',
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


class DoctorEducationViewSet(ModelViewSet):
    """ViewSet for doctor education"""
    serializer_class = DoctorEducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get education records for specific doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorEducation.objects.filter(doctor_id=doctor_id)
    
    def perform_create(self, serializer):
        """Create education record for doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        serializer.save(doctor_id=doctor_id)


class DoctorExperienceViewSet(ModelViewSet):
    """ViewSet for doctor experience"""
    serializer_class = DoctorExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get experience records for specific doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorExperience.objects.filter(doctor_id=doctor_id)
    
    def perform_create(self, serializer):
        """Create experience record for doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        serializer.save(doctor_id=doctor_id)


class DoctorDocumentViewSet(ModelViewSet):
    """ViewSet for doctor documents"""
    serializer_class = DoctorDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get documents for specific doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorDocument.objects.filter(doctor_id=doctor_id)
    
    def perform_create(self, serializer):
        """Create document for doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        serializer.save(doctor_id=doctor_id, uploaded_by=self.request.user)


class DoctorAvailabilityViewSet(ModelViewSet):
    """ViewSet for doctor availability"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get availability for specific doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorAvailability.objects.filter(doctor_id=doctor_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DoctorAvailabilityCreateSerializer
        return DoctorAvailabilitySerializer


class DoctorScheduleViewSet(ModelViewSet):
    """ViewSet for doctor schedule"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get schedule for specific doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        queryset = DoctorSchedule.objects.filter(doctor_id=doctor_id)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('date', 'start_time')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DoctorScheduleCreateSerializer
        return DoctorScheduleSerializer


class DoctorReviewViewSet(ModelViewSet):
    """ViewSet for doctor reviews"""
    serializer_class = DoctorReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reviews for specific doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorReview.objects.filter(doctor_id=doctor_id, is_approved=True)
    
    def perform_create(self, serializer):
        """Create review for doctor"""
        doctor_id = self.kwargs.get('doctor_id')
        serializer.save(doctor_id=doctor_id, patient=self.request.user)


class DoctorSearchView(APIView):
    """Search doctors with advanced filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='Search query'),
            OpenApiParameter('specialization', OpenApiTypes.STR, description='Specialization filter'),
            OpenApiParameter('min_experience', OpenApiTypes.INT, description='Minimum experience years'),
            OpenApiParameter('max_experience', OpenApiTypes.INT, description='Maximum experience years'),
            OpenApiParameter('min_fee', OpenApiTypes.NUMBER, description='Minimum consultation fee'),
            OpenApiParameter('max_fee', OpenApiTypes.NUMBER, description='Maximum consultation fee'),
            OpenApiParameter('consultation_type', OpenApiTypes.STR, description='Consultation type'),
            OpenApiParameter('rating_min', OpenApiTypes.NUMBER, description='Minimum rating'),
            OpenApiParameter('is_verified', OpenApiTypes.BOOL, description='Verified doctors only'),
            OpenApiParameter('city', OpenApiTypes.STR, description='City filter'),
        ],
        responses={200: DoctorListSerializer(many=True)},
        description="Search doctors with advanced filters"
    )
    def get(self, request):
        """Search doctors with advanced filters"""
        serializer = DoctorSearchSerializer(data=request.query_params)
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
        queryset = DoctorProfile.objects.select_related('user').filter(is_active=True)
        
        # Apply search filters
        search_data = serializer.validated_data
        
        if search_data.get('query'):
            query = search_data['query']
            queryset = queryset.filter(
                Q(user__name__icontains=query) |
                Q(specialization__icontains=query) |
                Q(qualification__icontains=query) |
                Q(sub_specialization__icontains=query)
            )
        
        if search_data.get('specialization'):
            queryset = queryset.filter(specialization__icontains=search_data['specialization'])
        
        if search_data.get('sub_specialization'):
            queryset = queryset.filter(sub_specialization__icontains=search_data['sub_specialization'])
        
        if search_data.get('min_experience'):
            # Calculate based on experience records
            min_exp = search_data['min_experience']
            queryset = queryset.filter(experience_years__gte=min_exp)
        
        if search_data.get('max_experience'):
            max_exp = search_data['max_experience']
            queryset = queryset.filter(experience_years__lte=max_exp)
        
        if search_data.get('min_fee'):
            queryset = queryset.filter(consultation_fee__gte=search_data['min_fee'])
        
        if search_data.get('max_fee'):
            queryset = queryset.filter(consultation_fee__lte=search_data['max_fee'])
        
        if search_data.get('rating_min'):
            queryset = queryset.filter(rating__gte=search_data['rating_min'])
        
        if search_data.get('is_verified'):
            queryset = queryset.filter(is_verified=search_data['is_verified'])
        
        # Note: emergency_available field removed as it doesn't exist in the model
        
        if search_data.get('consultation_type'):
            consultation_type = search_data['consultation_type']
            if consultation_type == 'online':
                queryset = queryset.filter(is_online_consultation_available=True)
            elif consultation_type == 'in_person':
                queryset = queryset.filter(is_accepting_patients=True)
        
        if search_data.get('city'):
            queryset = queryset.filter(user__city__icontains=search_data['city'])
        
        if search_data.get('state'):
            queryset = queryset.filter(user__state__icontains=search_data['state'])
        
        # Paginate results
        paginator = DoctorPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = DoctorListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Search results retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = DoctorListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Search results retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class DoctorStatsView(APIView):
    """Get doctor statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: DoctorStatsSerializer},
        description="Get doctor statistics and analytics"
    )
    def get(self, request):
        """Get doctor statistics"""
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
        total_doctors = DoctorProfile.objects.count()
        verified_doctors = DoctorProfile.objects.filter(is_verified=True).count()
        active_doctors = DoctorProfile.objects.filter(is_active=True).count()
        
        # Specialization distribution
        specialization_distribution = dict(
            DoctorProfile.objects.values('specialization').annotate(
                count=Count('specialization')
            ).values_list('specialization', 'count')
        )
        
        # Experience distribution
        experience_ranges = {
            '0-2': 0, '3-5': 0, '6-10': 0, '11-15': 0, '16-20': 0, '20+': 0
        }
        
        for doctor in DoctorProfile.objects.all():
            exp = doctor.experience_years or 0
            if exp <= 2:
                experience_ranges['0-2'] += 1
            elif exp <= 5:
                experience_ranges['3-5'] += 1
            elif exp <= 10:
                experience_ranges['6-10'] += 1
            elif exp <= 15:
                experience_ranges['11-15'] += 1
            elif exp <= 20:
                experience_ranges['16-20'] += 1
            else:
                experience_ranges['20+'] += 1
        
        # Average consultation fee
        avg_fee = DoctorProfile.objects.aggregate(
            avg_fee=Avg('consultation_fee')
        )['avg_fee'] or 0
        
        # Top rated doctors
        top_rated = list(
            DoctorProfile.objects.filter(
                rating__gte=4.0
            ).order_by('-rating')[:10].values(
                'user__name', 'specialization', 'rating'
            )
        )
        
        # Consultation stats
        from consultations.models import Consultation
        consultation_stats = {
            'total_consultations': Consultation.objects.count(),
            'avg_consultations_per_doctor': Consultation.objects.count() / max(total_doctors, 1),
            'consultation_completion_rate': 0  # Calculate based on your business logic
        }
        
        stats_data = {
            'total_doctors': total_doctors,
            'verified_doctors': verified_doctors,
            'active_doctors': active_doctors,
            'specialization_distribution': specialization_distribution,
            'experience_distribution': experience_ranges,
            'average_consultation_fee': avg_fee,
            'top_rated_doctors': top_rated,
            'consultation_stats': consultation_stats
        }
        
        serializer = DoctorStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Doctor statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

