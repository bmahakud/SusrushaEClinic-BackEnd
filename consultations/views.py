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
    Consultation, ConsultationSymptom, ConsultationDiagnosis,
    ConsultationVitalSigns, ConsultationAttachment, ConsultationNote,
    ConsultationReschedule
)
from .serializers import (
    ConsultationSerializer, ConsultationCreateSerializer, ConsultationUpdateSerializer,
    ConsultationDiagnosisSerializer, ConsultationDiagnosisCreateSerializer,
    ConsultationVitalSignsSerializer, ConsultationVitalSignsCreateSerializer,
    ConsultationAttachmentSerializer, ConsultationAttachmentCreateSerializer,
    ConsultationNoteSerializer, ConsultationNoteCreateSerializer,
    ConsultationSymptomSerializer, ConsultationSymptomCreateSerializer,
    ConsultationListSerializer, ConsultationSearchSerializer, ConsultationStatsSerializer,
    ConsultationDetailSerializer
)


class ConsultationPagination(PageNumberPagination):
    """Custom pagination for consultation lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConsultationViewSet(ModelViewSet):
    """ViewSet for consultation management"""
    queryset = Consultation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ConsultationPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__name', 'doctor__name', 'chief_complaint']
    ordering_fields = ['scheduled_at', 'created_at', 'status']
    ordering = ['-scheduled_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConsultationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ConsultationUpdateSerializer
        elif self.action == 'list':
            return ConsultationListSerializer
        elif self.action == 'retrieve':
            return ConsultationDetailSerializer
        return ConsultationSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = Consultation.objects.select_related('patient', 'doctor')
        
        if user.role == 'patient':
            # Patients can only see their own consultations
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            # Doctors can see consultations they are assigned to
            return queryset.filter(doctor=user)
        elif user.role in ['admin', 'superadmin']:
            # Admins can see all consultations
            return queryset
        
        return queryset.none()
    
    @extend_schema(
        responses={200: ConsultationSerializer},
        description="Get consultation by ID"
    )
    def retrieve(self, request, pk=None):
        """Get consultation by ID"""
        consultation = self.get_object()
        serializer = self.get_serializer(consultation)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        responses={200: ConsultationListSerializer(many=True)},
        description="List all consultations with pagination and filtering"
    )
    def list(self, request):
        """List consultations with pagination and filtering"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Consultations retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultations retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=ConsultationCreateSerializer,
        responses={201: ConsultationSerializer},
        description="Create consultation"
    )
    def create(self, request):
        """Create consultation"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            consultation = serializer.save()
            response_serializer = ConsultationSerializer(consultation)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Consultation created successfully',
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
    def start(self, request, pk=None):
        """Start consultation"""
        consultation = self.get_object()
        
        if consultation.status != 'scheduled':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Consultation can only be started if it is scheduled'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        consultation.status = 'in_progress'
        consultation.started_at = timezone.now()
        consultation.save()
        
        serializer = ConsultationSerializer(consultation)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation started successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete consultation"""
        consultation = self.get_object()
        
        if consultation.status != 'in_progress':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Consultation can only be completed if it is in progress'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        consultation.status = 'completed'
        consultation.ended_at = timezone.now()
        consultation.save()
        
        serializer = ConsultationSerializer(consultation)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation completed successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel consultation"""
        consultation = self.get_object()
        
        if consultation.status in ['completed', 'cancelled']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Cannot cancel a completed or already cancelled consultation'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        consultation.status = 'cancelled'
        consultation.save()
        
        serializer = ConsultationSerializer(consultation)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation cancelled successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class ConsultationDiagnosisViewSet(ModelViewSet):
    """ViewSet for consultation diagnosis"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get diagnosis for specific consultation"""
        consultation_id = self.kwargs.get('consultation_id')
        return ConsultationDiagnosis.objects.filter(consultation_id=consultation_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConsultationDiagnosisCreateSerializer
        return ConsultationDiagnosisSerializer


class ConsultationVitalSignsViewSet(ModelViewSet):
    """ViewSet for vital signs"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get vital signs for specific consultation"""
        consultation_id = self.kwargs.get('consultation_id')
        return ConsultationVitalSigns.objects.filter(consultation_id=consultation_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConsultationVitalSignsCreateSerializer
        return ConsultationVitalSignsSerializer


class ConsultationAttachmentViewSet(ModelViewSet):
    """ViewSet for consultation documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get documents for specific consultation"""
        consultation_id = self.kwargs.get('consultation_id')
        return ConsultationAttachment.objects.filter(consultation_id=consultation_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConsultationAttachmentCreateSerializer
        return ConsultationAttachmentSerializer


class ConsultationNoteViewSet(ModelViewSet):
    """ViewSet for consultation notes"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notes for specific consultation"""
        consultation_id = self.kwargs.get('consultation_id')
        queryset = ConsultationNote.objects.filter(consultation_id=consultation_id)
        
        # Filter private notes based on user role
        user = self.request.user
        if user.role == 'patient':
            # Patients can see non-private notes
            return queryset.filter(is_private=False)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConsultationNoteCreateSerializer
        return ConsultationNoteSerializer


class ConsultationSymptomViewSet(ModelViewSet):
    """ViewSet for consultation symptoms"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get symptoms for specific consultation"""
        consultation_id = self.kwargs.get('consultation_id')
        return ConsultationSymptom.objects.filter(consultation_id=consultation_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConsultationSymptomCreateSerializer
        return ConsultationSymptomSerializer


class ConsultationSearchView(APIView):
    """Search consultations with advanced filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='Search query'),
            OpenApiParameter('patient_id', OpenApiTypes.INT, description='Patient ID filter'),
            OpenApiParameter('doctor_id', OpenApiTypes.INT, description='Doctor ID filter'),
            OpenApiParameter('consultation_type', OpenApiTypes.STR, description='Consultation type'),
            OpenApiParameter('status', OpenApiTypes.STR, description='Status filter'),
            OpenApiParameter('payment_status', OpenApiTypes.STR, description='Payment status'),
            OpenApiParameter('date_from', OpenApiTypes.DATE, description='Start date filter'),
            OpenApiParameter('date_to', OpenApiTypes.DATE, description='End date filter'),
        ],
        responses={200: ConsultationListSerializer(many=True)},
        description="Search consultations with advanced filters"
    )
    def get(self, request):
        """Search consultations with advanced filters"""
        serializer = ConsultationSearchSerializer(data=request.query_params)
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
        queryset = Consultation.objects.select_related('patient', 'doctor')
        
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
                Q(chief_complaint__icontains=query)
            )
        
        if search_data.get('patient_id'):
            queryset = queryset.filter(patient_id=search_data['patient_id'])
        
        if search_data.get('doctor_id'):
            queryset = queryset.filter(doctor_id=search_data['doctor_id'])
        
        if search_data.get('consultation_type'):
            queryset = queryset.filter(consultation_type=search_data['consultation_type'])
        
        if search_data.get('status'):
            queryset = queryset.filter(status=search_data['status'])
        
        if search_data.get('payment_status'):
            queryset = queryset.filter(payment_status=search_data['payment_status'])
        
        if search_data.get('date_from'):
            queryset = queryset.filter(scheduled_at__date__gte=search_data['date_from'])
        
        if search_data.get('date_to'):
            queryset = queryset.filter(scheduled_at__date__lte=search_data['date_to'])
        
        # Paginate results
        paginator = ConsultationPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ConsultationListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Search results retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = ConsultationListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Search results retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class ConsultationStatsView(APIView):
    """Get consultation statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: ConsultationStatsSerializer},
        description="Get consultation statistics and analytics"
    )
    def get(self, request):
        """Get consultation statistics"""
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
        total_consultations = Consultation.objects.count()
        completed_consultations = Consultation.objects.filter(status='completed').count()
        cancelled_consultations = Consultation.objects.filter(status='cancelled').count()
        pending_consultations = Consultation.objects.filter(status='scheduled').count()
        
        # Consultation type distribution
        consultation_type_distribution = dict(
            Consultation.objects.values('consultation_type').annotate(
                count=Count('consultation_type')
            ).values_list('consultation_type', 'count')
        )
        
        # Average duration and rating
        completed_consultations_qs = Consultation.objects.filter(
            status='completed', started_at__isnull=False, ended_at__isnull=False
        )
        
        avg_duration = 0
        if completed_consultations_qs.exists():
            total_duration = sum([
                (c.ended_at - c.started_at).total_seconds() / 60
                for c in completed_consultations_qs
            ])
            avg_duration = total_duration / completed_consultations_qs.count()
        
        avg_rating = Consultation.objects.filter(
            rating__isnull=False
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Revenue stats
        total_revenue = Consultation.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('consultation_fee'))['total'] or 0
        
        revenue_stats = {
            'total_revenue': total_revenue,
            'average_consultation_fee': Consultation.objects.aggregate(
                avg_fee=Avg('consultation_fee')
            )['avg_fee'] or 0,
            'pending_payments': Consultation.objects.filter(
                payment_status='pending'
            ).aggregate(total=Sum('consultation_fee'))['total'] or 0
        }
        
        # Monthly trends (last 12 months)
        monthly_trends = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_consultations = Consultation.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            monthly_trends.append({
                'month': month_start.strftime('%Y-%m'),
                'consultations': month_consultations
            })
        
        stats_data = {
            'total_consultations': total_consultations,
            'completed_consultations': completed_consultations,
            'cancelled_consultations': cancelled_consultations,
            'pending_consultations': pending_consultations,
            'consultation_type_distribution': consultation_type_distribution,
            'average_duration': avg_duration,
            'average_rating': avg_rating,
            'revenue_stats': revenue_stats,
            'monthly_trends': monthly_trends
        }
        
        serializer = ConsultationStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class ConsultationPrescriptionView(APIView):
    """Get prescription for a specific consultation"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: 'PrescriptionSerializer'},
        description="Get prescription associated with a consultation"
    )
    def get(self, request, consultation_id):
        """Get prescription for consultation"""
        try:
            # Get consultation
            consultation = get_object_or_404(Consultation, id=consultation_id)
            
            # Check permissions
            user = request.user
            if user.role == 'patient' and consultation.patient != user:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': 'You can only view prescriptions for your own consultations'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_403_FORBIDDEN)
            
            if user.role == 'doctor' and consultation.doctor != user:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'PERMISSION_DENIED',
                        'message': 'You can only view prescriptions for consultations you conducted'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if prescription exists
            if not hasattr(consultation, 'prescription'):
                return Response({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': 'No prescription found for this consultation'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Import prescription serializer
            from prescriptions.serializers import PrescriptionSerializer
            
            prescription = consultation.prescription
            serializer = PrescriptionSerializer(prescription)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Prescription retrieved successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An error occurred while retrieving the prescription'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)