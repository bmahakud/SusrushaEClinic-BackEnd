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
    ConsultationDetailSerializer, ConsultationCreateDynamicSerializer
)
from doctors.serializers import DoctorSlotSerializer


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
    ordering_fields = ['scheduled_date', 'scheduled_time', 'created_at', 'status']
    ordering = ['-scheduled_date', '-scheduled_time']
    
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
        queryset = Consultation.objects.select_related('patient', 'doctor', 'clinic')
        
        if user.role == 'patient':
            # Patients can only see their own consultations
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            # Doctors can see consultations they are assigned to
            return queryset.filter(doctor=user)
        elif user.role == 'admin':
            # Admins can only see consultations for their assigned clinic
            try:
                # Get the clinic that this admin is assigned to
                assigned_clinic = user.administered_clinic
                return queryset.filter(clinic=assigned_clinic)
            except:
                # If admin is not assigned to any clinic, return empty queryset
                return queryset.none()
        elif user.role == 'superadmin':
            # SuperAdmin can see all consultations
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

    @extend_schema(
        request=ConsultationCreateDynamicSerializer,
        responses={201: ConsultationSerializer},
        description="Create consultation with dynamic slots (no slot_id required)"
    )
    @action(detail=False, methods=['post'], url_path='create-dynamic')
    def create_dynamic(self, request):
        """Create consultation with dynamic slots (no slot_id required)"""
        from .serializers import ConsultationCreateDynamicSerializer
        
        serializer = ConsultationCreateDynamicSerializer(data=request.data)
        if serializer.is_valid():
            consultation = serializer.save()
            response_serializer = ConsultationSerializer(consultation)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Consultation created successfully with dynamic slot',
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

    @action(detail=False, methods=['get'], url_path='doctor/my-consultations')
    def doctor_consultations(self, request):
        """Get consultations for the logged-in doctor"""
        if request.user.role != 'doctor':
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Only doctors can access this endpoint'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get consultations for the logged-in doctor
        consultations = Consultation.objects.filter(
            doctor=request.user
        ).select_related('patient', 'doctor', 'clinic').order_by(
            'scheduled_date', 'scheduled_time'
        )
        
        # Apply status filter if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            consultations = consultations.filter(status=status_filter)
        
        # Apply date filter if provided
        date_filter = request.query_params.get('date')
        if date_filter:
            consultations = consultations.filter(scheduled_date=date_filter)
        
        serializer = ConsultationListSerializer(consultations, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Found {len(serializer.data)} consultations for doctor',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """Get available slots for consultation booking"""
        doctor_id = request.query_params.get('doctor_id')
        clinic_id = request.query_params.get('clinic_id')
        date = request.query_params.get('date')
        
        if not doctor_id or not clinic_id or not date:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': 'doctor_id, clinic_id, and date are required'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get available slots
        from doctors.models import DoctorSlot
        slots = DoctorSlot.objects.filter(
            doctor_id=doctor_id,
            clinic_id=clinic_id,
            date=date_obj,
            is_available=True,
            is_booked=False
        ).order_by('start_time')
        
        serializer = DoctorSlotSerializer(slots, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': f'Available slots for {date}',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def calculate_available_slots(self, request):
        """Calculate available slots dynamically based on doctor availability and clinic duration"""
        doctor_id = request.query_params.get('doctor_id')
        clinic_id = request.query_params.get('clinic_id')
        date = request.query_params.get('date')
        
        if not doctor_id or not clinic_id or not date:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': 'doctor_id, clinic_id, and date are required'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from datetime import datetime, timedelta
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE',
                    'message': 'Invalid date format. Use YYYY-MM-DD'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get doctor and clinic
            from doctors.models import DoctorSlot
            from eclinic.models import Clinic
            from authentication.models import User
            
            doctor = User.objects.get(id=doctor_id, role='doctor')
            clinic = Clinic.objects.get(id=clinic_id)
            
            # Get doctor's availability for the date
            available_slots = DoctorSlot.objects.filter(
                doctor=doctor,
                date=date_obj,
                is_available=True,
                is_booked=False
            ).order_by('start_time')
            
            # Get clinic consultation duration
            consultation_duration = clinic.consultation_duration  # in minutes
            
            calculated_slots = []
            
            for slot in available_slots:
                # Convert slot times to datetime for calculation
                slot_start = datetime.combine(date_obj, slot.start_time)
                slot_end = datetime.combine(date_obj, slot.end_time)
                
                current_time = slot_start
                
                # Generate consultation slots within this availability period
                while current_time < slot_end:
                    slot_end_time = current_time + timedelta(minutes=consultation_duration)
                    
                    # Don't create slot if it would exceed the availability period
                    if slot_end_time > slot_end:
                        break
                    
                    # Check if this calculated slot overlaps with any existing consultation
                    overlapping_consultation = Consultation.objects.filter(
                        doctor=doctor,
                        scheduled_date=date_obj,
                        status__in=['scheduled', 'in_progress']
                    ).filter(
                        scheduled_time__lt=slot_end_time.time(),
                        scheduled_time__gte=current_time.time()
                    ).first()
                    
                    if not overlapping_consultation:
                        calculated_slots.append({
                            'start_time': current_time.time().strftime('%H:%M'),
                            'end_time': slot_end_time.time().strftime('%H:%M'),
                            'duration_minutes': consultation_duration,
                            'clinic_name': clinic.name,
                            'doctor_name': doctor.name,
                            'is_available': True
                        })
                    
                    # Move to next slot
                    current_time = slot_end_time
            
            return Response({
                'success': True,
                'data': {
                    'slots': calculated_slots,
                    'clinic_duration': consultation_duration,
                    'date': date,
                    'doctor_name': doctor.name,
                    'clinic_name': clinic.name
                },
                'message': f'Calculated {len(calculated_slots)} available slots for {date}',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'DOCTOR_NOT_FOUND',
                    'message': 'Doctor not found'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)
        except Clinic.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'CLINIC_NOT_FOUND',
                    'message': 'Clinic not found'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'CALCULATION_ERROR',
                    'message': f'Error calculating slots: {str(e)}'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        elif user.role == 'admin':
            # Admins can only see consultations for their assigned clinic
            try:
                # Get the clinic that this admin is assigned to
                assigned_clinic = user.administered_clinic
                queryset = queryset.filter(clinic=assigned_clinic)
            except:
                # If admin is not assigned to any clinic, return empty queryset
                queryset = queryset.none()
        elif user.role == 'superadmin':
            # SuperAdmin can see all consultations
            pass
        else:
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
        user = request.user
        
        # Check permissions
        if user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Apply role-based filtering
        if user.role == 'admin':
            try:
                # Get the clinic that this admin is assigned to
                assigned_clinic = user.administered_clinic
                base_queryset = Consultation.objects.filter(clinic=assigned_clinic)
            except:
                # If admin is not assigned to any clinic, return empty stats
                base_queryset = Consultation.objects.none()
        else:
            # SuperAdmin can see all consultations
            base_queryset = Consultation.objects.all()
        
        # Calculate statistics
        total_consultations = base_queryset.count()
        completed_consultations = base_queryset.filter(status='completed').count()
        cancelled_consultations = base_queryset.filter(status='cancelled').count()
        pending_consultations = base_queryset.filter(status='scheduled').count()
        
        # Consultation type distribution
        consultation_type_distribution = dict(
            base_queryset.values('consultation_type').annotate(
                count=Count('consultation_type')
            ).values_list('consultation_type', 'count')
        )
        
        # Average duration and rating
        completed_consultations_qs = base_queryset.filter(
            status='completed', started_at__isnull=False, ended_at__isnull=False
        )
        
        avg_duration = 0
        if completed_consultations_qs.exists():
            total_duration = sum([
                (c.ended_at - c.started_at).total_seconds() / 60
                for c in completed_consultations_qs
            ])
            avg_duration = total_duration / completed_consultations_qs.count()
        
        avg_rating = base_queryset.filter(
            rating__isnull=False
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Revenue stats
        total_revenue = base_queryset.filter(
            payment_status='paid'
        ).aggregate(total=Sum('consultation_fee'))['total'] or 0
        
        revenue_stats = {
            'total_revenue': total_revenue,
            'average_consultation_fee': base_queryset.aggregate(
                avg_fee=Avg('consultation_fee')
            )['avg_fee'] or 0,
            'pending_payments': base_queryset.filter(
                payment_status='pending'
            ).aggregate(total=Sum('consultation_fee'))['total'] or 0
        }
        
        # Monthly trends (last 12 months)
        monthly_trends = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_consultations = base_queryset.filter(
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