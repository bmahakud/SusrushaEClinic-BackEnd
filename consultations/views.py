from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
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
    ConsultationReschedule, ConsultationReceipt
)
from .serializers import (
    ConsultationSerializer, ConsultationCreateSerializer, ConsultationUpdateSerializer,
    ConsultationListSerializer, ConsultationDetailSerializer, ConsultationSearchSerializer,
    ConsultationStatsSerializer, ConsultationCreateDynamicSerializer,
    ConsultationDiagnosisSerializer, ConsultationDiagnosisCreateSerializer,
    ConsultationVitalSignsSerializer, ConsultationVitalSignsCreateSerializer,
    ConsultationAttachmentSerializer, ConsultationAttachmentCreateSerializer,
    ConsultationNoteSerializer, ConsultationNoteCreateSerializer,
    ConsultationRescheduleSerializer, ConsultationRescheduleCreateSerializer,
    ConsultationReceiptSerializer, ConsultationReceiptCreateSerializer
)
from doctors.serializers import DoctorSlotSerializer
from .services import WhatsAppNotificationService


class ConsultationPagination(PageNumberPagination):
    """Custom pagination for consultation lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IsAdminOrSuperAdmin(BasePermission):
    """Custom permission to allow only admin and superadmin"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class IsAdminWithClinicOrSuperAdmin(BasePermission):
    """Custom permission to allow admin with assigned clinic or superadmin"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'superadmin':
            return True
        
        if request.user.role == 'admin':
            # Check if admin has an assigned clinic
            try:
                return hasattr(request.user, 'administered_clinic') and request.user.administered_clinic is not None
            except:
                return False
        
        return False


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
            # Admins can see consultations for their assigned clinic
            try:
                # Get the clinic that this admin is assigned to
                assigned_clinic = user.administered_clinic
                if assigned_clinic:
                    return queryset.filter(clinic=assigned_clinic)
                else:
                    # If admin is not assigned to any clinic, they can see all consultations
                    # This is a fallback for admins without specific clinic assignments
                    return queryset
            except AttributeError:
                # If admin is not assigned to any clinic, they can see all consultations
                return queryset
            except Exception as e:
                # Log the error and return all consultations as fallback
                print(f"Error getting admin clinic: {e}")
                return queryset
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
        parameters=[
            OpenApiParameter('upcoming', OpenApiTypes.BOOL, description='Filter upcoming consultations only'),
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by status'),
            OpenApiParameter('payment_status', OpenApiTypes.STR, description='Filter by payment status'),
        ],
        responses={200: ConsultationListSerializer(many=True)},
        description="List all consultations with pagination and filtering"
    )
    def list(self, request):
        """List consultations with pagination and filtering"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter upcoming consultations
        upcoming_only = request.query_params.get('upcoming', '').lower() == 'true'
        if upcoming_only:
            from datetime import datetime, timedelta
            now = timezone.now()
            # Get consultations scheduled for today and future dates
            queryset = queryset.filter(
                scheduled_date__gte=now.date()
            ).filter(
                # For today's consultations, check if time hasn't passed
                Q(scheduled_date__gt=now.date()) |
                Q(scheduled_date=now.date(), scheduled_time__gte=now.time())
            )
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by payment status
        payment_status_filter = request.query_params.get('payment_status')
        if payment_status_filter:
            queryset = queryset.filter(payment_status=payment_status_filter)
        
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
        
        print(f"🔍 create_dynamic called with data: {request.data}")
        print(f"🔍 Using ConsultationCreateDynamicSerializer")
        
        serializer = ConsultationCreateDynamicSerializer(data=request.data)
        print(f"🔍 Serializer created: {serializer}")
        
        if serializer.is_valid():
            print(f"🔍 Serializer is valid")
            consultation = serializer.save()
            response_serializer = ConsultationSerializer(consultation)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Consultation created successfully with dynamic slot',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_201_CREATED)
        else:
            print(f"🔍 Serializer errors: {serializer.errors}")
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
            
            # Get clinic consultation duration
            consultation_duration = clinic.consultation_duration  # in minutes
            
            # OPTIMIZATION: Pre-fetch all existing consultations for this doctor and date
            # Use select_related to avoid N+1 queries and only fetch needed fields
            existing_consultations = Consultation.objects.filter(
                doctor=doctor,
                scheduled_date=date_obj,
                status__in=['scheduled', 'in_progress', 'confirmed']
            ).only('scheduled_time', 'duration')
            
            # OPTIMIZATION: Pre-fetch all booked slots for this doctor and date
            booked_slots = DoctorSlot.objects.filter(
                doctor=doctor,
                date=date_obj,
                is_booked=True
            ).only('start_time', 'end_time')
            
            # OPTIMIZATION: Create a set of blocked time ranges for fast lookup
            blocked_ranges = set()
            
            # Add consultation time ranges to blocked ranges
            for consultation in existing_consultations:
                start_time = consultation.scheduled_time
                end_time = (datetime.combine(date_obj, start_time) + 
                           timedelta(minutes=consultation.duration)).time()
                blocked_ranges.add((start_time, end_time))
            
            # Add booked slot time ranges to blocked ranges
            for slot in booked_slots:
                blocked_ranges.add((slot.start_time, slot.end_time))
            
            # Get doctor's availability for the date
            available_slots = DoctorSlot.objects.filter(
                doctor=doctor,
                date=date_obj,
                is_available=True,
                is_booked=False
            ).order_by('start_time')
            
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
                    
                    # OPTIMIZATION: Fast overlap check using pre-computed blocked ranges
                    slot_start_time = current_time.time()
                    slot_end_time_obj = slot_end_time.time()
                    
                    # Check if this slot overlaps with any blocked range
                    is_blocked = False
                    for blocked_start, blocked_end in blocked_ranges:
                        if (slot_start_time < blocked_end and slot_end_time_obj > blocked_start):
                            is_blocked = True
                            break
                    
                    if not is_blocked:
                        calculated_slots.append({
                            'start_time': slot_start_time.strftime('%H:%M'),
                            'end_time': slot_end_time_obj.strftime('%H:%M'),
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
    
    @action(detail=True, methods=['post'])
    def generate_receipt(self, request, pk=None):
        """Generate receipt for consultation"""
        consultation = self.get_object()
        
        try:
            # Check if receipt already exists
            existing_receipt = ConsultationReceipt.objects.filter(consultation=consultation).first()
            if existing_receipt:
                serializer = ConsultationReceiptSerializer(existing_receipt)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Receipt already exists',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            
            # Create new receipt
            receipt_data = {
                'consultation': consultation,
                'amount': consultation.consultation_fee,
                'payment_method': consultation.payment_method,
                'payment_status': consultation.payment_status,
                'issued_by': request.user
            }
            
            receipt_serializer = ConsultationReceiptCreateSerializer(data=receipt_data)
            if receipt_serializer.is_valid():
                receipt = receipt_serializer.save()
                response_serializer = ConsultationReceiptSerializer(receipt)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Receipt generated successfully',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid receipt data',
                        'details': receipt_serializer.errors
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'RECEIPT_GENERATION_ERROR',
                    'message': f'Error generating receipt: {str(e)}'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            consultation = Consultation.objects.get(id=consultation_id)
            
            # Check permissions
            user = request.user
            if user.role == 'patient' and consultation.patient != user:
                return Response({
                    'success': False,
                    'error': 'You can only view your own consultation prescriptions'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if user.role == 'doctor' and consultation.doctor != user:
                return Response({
                    'success': False,
                    'error': 'You can only view prescriptions for your consultations'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get prescription
            from prescriptions.models import Prescription
            try:
                prescription = Prescription.objects.get(consultation=consultation)
                from prescriptions.serializers import PrescriptionSerializer
                serializer = PrescriptionSerializer(prescription)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Prescription retrieved successfully',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            except Prescription.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No prescription found for this consultation'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Consultation.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Consultation not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ConsultationReceiptView(APIView):
    """Handle consultation receipt generation and retrieval"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={201: ConsultationReceiptSerializer},
        description="Generate receipt for consultation payment"
    )
    def post(self, request, consultation_id):
        """Generate receipt for consultation"""
        try:
            consultation = Consultation.objects.get(id=consultation_id)
            
            # Check permissions
            user = request.user
            if user.role == 'admin':
                # Admin can generate receipts for any consultation in their clinic
                if not hasattr(user, 'administered_clinic') or consultation.clinic != user.administered_clinic:
                    return Response({
                        'success': False,
                        'error': 'You can only generate receipts for consultations in your clinic'
                    }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == 'doctor' and consultation.doctor != user:
                return Response({
                    'success': False,
                    'error': 'You can only generate receipts for your consultations'
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == 'patient' and consultation.patient != user:
                return Response({
                    'success': False,
                    'error': 'You can only generate receipts for your consultations'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if receipt already exists
            from .models import ConsultationReceipt
            existing_receipt = ConsultationReceipt.objects.filter(consultation=consultation).first()
            if existing_receipt:
                response_serializer = ConsultationReceiptSerializer(existing_receipt)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Receipt already exists',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            
            # Create receipt data
            receipt_data = {
                'consultation': consultation,
                'amount': consultation.consultation_fee,
                'payment_method': consultation.payment_method or 'cash',
                'payment_status': consultation.payment_status,
                'issued_by': user
            }
            
            serializer = ConsultationReceiptCreateSerializer(data=receipt_data)
            if serializer.is_valid():
                receipt = serializer.save()
                response_serializer = ConsultationReceiptSerializer(receipt)
                return Response({
                    'success': True,
                    'data': response_serializer.data,
                    'message': 'Receipt generated successfully',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid receipt data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Consultation.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Consultation not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        responses={200: ConsultationReceiptSerializer},
        description="Get receipt for consultation"
    )
    def get(self, request, consultation_id):
        """Get receipt for consultation"""
        try:
            consultation = Consultation.objects.get(id=consultation_id)
            
            # Check permissions
            user = request.user
            if user.role == 'admin':
                if not hasattr(user, 'administered_clinic') or consultation.clinic != user.administered_clinic:
                    return Response({
                        'success': False,
                        'error': 'You can only view receipts for consultations in your clinic'
                    }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == 'doctor' and consultation.doctor != user:
                return Response({
                    'success': False,
                    'error': 'You can only view receipts for your consultations'
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == 'patient' and consultation.patient != user:
                return Response({
                    'success': False,
                    'error': 'You can only view receipts for your consultations'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get receipt
            from .models import ConsultationReceipt
            try:
                receipt = ConsultationReceipt.objects.get(consultation=consultation)
                serializer = ConsultationReceiptSerializer(receipt)
                return Response({
                    'success': True,
                    'data': serializer.data,
                    'message': 'Receipt retrieved successfully',
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_200_OK)
            except ConsultationReceipt.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'No receipt found for this consultation'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Consultation.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Consultation not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([])  # No authentication required for testing
def test_generate_receipt(request, consultation_id):
    """Test endpoint to generate receipt without authentication (development only)"""
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        
        # Check if receipt already exists
        existing_receipt = ConsultationReceipt.objects.filter(consultation=consultation).first()
        if existing_receipt:
            serializer = ConsultationReceiptSerializer(existing_receipt)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Receipt already exists',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
        
        # Create new receipt - try to get a superadmin user for issued_by
        try:
            issued_by_user = User.objects.filter(role='superadmin').first()
        except:
            issued_by_user = None
            
        receipt_data = {
            'consultation': consultation.id,
            'amount': consultation.consultation_fee,
            'payment_method': consultation.payment_method,
            'payment_status': consultation.payment_status,
            'issued_by': issued_by_user.id if issued_by_user else None
        }
        
        receipt_serializer = ConsultationReceiptCreateSerializer(data=receipt_data)
        if receipt_serializer.is_valid():
            receipt = receipt_serializer.save()
            response_serializer = ConsultationReceiptSerializer(receipt)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Receipt generated successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid receipt data',
                    'details': receipt_serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Consultation.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'CONSULTATION_NOT_FOUND',
                'message': f'Consultation with ID {consultation_id} not found'
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'RECEIPT_GENERATION_ERROR',
                'message': f'Error generating receipt: {str(e)}'
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # No authentication required for testing
def test_calculate_available_slots(request):
    """Test endpoint to calculate available slots without authentication (development only)"""
    try:
        doctor_id = request.query_params.get('doctor_id', 'DOC018')
        clinic_id = request.query_params.get('clinic_id', '1')
        date = request.query_params.get('date', '2025-08-04')
        
        from datetime import datetime, timedelta
        from doctors.models import DoctorSlot
        from eclinic.models import Clinic
        from authentication.models import User
        
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        doctor = User.objects.get(id=doctor_id, role='doctor')
        
        # Try to get clinic by ID first, then by name
        try:
            clinic = Clinic.objects.get(id=clinic_id)
        except (Clinic.DoesNotExist, ValueError):
            try:
                clinic = Clinic.objects.get(name=clinic_id)
            except Clinic.DoesNotExist:
                # Use a default clinic or create one
                clinic, created = Clinic.objects.get_or_create(
                    name='Default Clinic',
                    defaults={
                        'consultation_duration': 15,
                        'is_active': True
                    }
                )
        
        # Get clinic consultation duration
        consultation_duration = clinic.consultation_duration  # in minutes
        
        # OPTIMIZATION: Pre-fetch all existing consultations for this doctor and date
        existing_consultations = Consultation.objects.filter(
            doctor=doctor,
            scheduled_date=date_obj,
            status__in=['scheduled', 'in_progress', 'confirmed']
        ).only('scheduled_time', 'duration')
        
        # OPTIMIZATION: Pre-fetch all booked slots for this doctor and date
        booked_slots = DoctorSlot.objects.filter(
            doctor=doctor,
            date=date_obj,
            is_booked=True
        ).only('start_time', 'end_time')
        
        # OPTIMIZATION: Create a set of blocked time ranges for fast lookup
        blocked_ranges = set()
        
        # Add consultation time ranges to blocked ranges
        for consultation in existing_consultations:
            start_time = consultation.scheduled_time
            end_time = (datetime.combine(date_obj, start_time) + 
                       timedelta(minutes=consultation.duration)).time()
            blocked_ranges.add((start_time, end_time))
        
        # Add booked slot time ranges to blocked ranges
        for slot in booked_slots:
            blocked_ranges.add((slot.start_time, slot.end_time))
        
        # Get doctor's availability for the date
        available_slots = DoctorSlot.objects.filter(
            doctor=doctor,
            date=date_obj,
            is_available=True,
            is_booked=False
        ).order_by('start_time')
        
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
                
                # OPTIMIZATION: Fast overlap check using pre-computed blocked ranges
                slot_start_time = current_time.time()
                slot_end_time_obj = slot_end_time.time()
                
                # Check if this slot overlaps with any blocked range
                is_blocked = False
                for blocked_start, blocked_end in blocked_ranges:
                    if (slot_start_time < blocked_end and slot_end_time_obj > blocked_start):
                        is_blocked = True
                        break
                
                if not is_blocked:
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
                'clinic_name': clinic.name,
                'total_available_slots': len(calculated_slots)
            },
            'message': f'Calculated {len(calculated_slots)} available slots for {date}',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # No authentication required for testing
def test_consultation_list(request):
    """Test endpoint to list consultations without authentication (development only)"""
    try:
        from datetime import datetime, timedelta
        now = timezone.now()
        
        # Get all consultations
        consultations = Consultation.objects.select_related('patient', 'doctor', 'clinic').all()
        
        # Filter upcoming consultations if requested
        upcoming_only = request.query_params.get('upcoming', '').lower() == 'true'
        if upcoming_only:
            consultations = consultations.filter(
                scheduled_date__gte=now.date()
            ).filter(
                # For today's consultations, check if time hasn't passed
                Q(scheduled_date__gt=now.date()) |
                Q(scheduled_date=now.date(), scheduled_time__gte=now.time())
            )
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            consultations = consultations.filter(status=status_filter)
        
        # Filter by payment status
        payment_status_filter = request.query_params.get('payment_status')
        if payment_status_filter:
            consultations = consultations.filter(payment_status=payment_status_filter)
        
        # Serialize the consultations
        serializer = ConsultationListSerializer(consultations, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data),
            'message': 'Consultations retrieved successfully (test endpoint)',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # No authentication required for testing
def test_admin_consultation_access(request):
    """Test endpoint to check admin consultation access (development only)"""
    try:
        # Get all admin users and their consultation access
        admin_users = User.objects.filter(role='admin')
        admin_access_data = []
        
        for admin in admin_users:
            try:
                clinic = admin.administered_clinic
                clinic_info = {
                    'id': clinic.id,
                    'name': clinic.name
                } if clinic else None
                
                # Get consultations this admin can access
                if clinic:
                    consultations = Consultation.objects.filter(clinic=clinic)
                else:
                    # Admin without clinic can see all consultations
                    consultations = Consultation.objects.all()
                
                consultation_count = consultations.count()
                consultation_ids = list(consultations.values_list('id', flat=True)[:5])  # First 5 IDs
                
            except AttributeError:
                clinic_info = None
                consultations = Consultation.objects.all()
                consultation_count = consultations.count()
                consultation_ids = list(consultations.values_list('id', flat=True)[:5])
            
            admin_access_data.append({
                'user_id': admin.id,
                'name': admin.name,
                'email': admin.email,
                'phone': admin.phone,
                'role': admin.role,
                'assigned_clinic': clinic_info,
                'has_clinic': clinic_info is not None,
                'consultation_access': {
                    'total_consultations': consultation_count,
                    'sample_consultation_ids': consultation_ids,
                    'can_access_all': clinic_info is None
                }
            })
        
        return Response({
            'success': True,
            'data': {
                'admin_access_data': admin_access_data,
                'total_admins': len(admin_access_data)
            },
            'message': 'Admin consultation access check completed',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # No authentication required for testing
def test_admin_permissions(request):
    """Test endpoint to check admin permissions and clinic assignments (development only)"""
    try:
        # Get all admin users
        admin_users = User.objects.filter(role='admin')
        admin_data = []
        
        for admin in admin_users:
            try:
                clinic = admin.administered_clinic
                clinic_info = {
                    'id': clinic.id,
                    'name': clinic.name
                } if clinic else None
            except AttributeError:
                clinic_info = None
            
            admin_data.append({
                'user_id': admin.id,
                'name': admin.name,
                'email': admin.email,
                'phone': admin.phone,
                'role': admin.role,
                'assigned_clinic': clinic_info,
                'has_clinic': clinic_info is not None
            })
        
        # Get all superadmin users
        superadmin_users = User.objects.filter(role='superadmin')
        superadmin_data = []
        
        for superadmin in superadmin_users:
            superadmin_data.append({
                'user_id': superadmin.id,
                'name': superadmin.name,
                'email': superadmin.email,
                'phone': superadmin.phone,
                'role': superadmin.role
            })
        
        return Response({
            'success': True,
            'data': {
                'admin_users': admin_data,
                'superadmin_users': superadmin_data,
                'total_admins': len(admin_data),
                'total_superadmins': len(superadmin_data)
            },
            'message': 'Admin permissions check completed',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([])  # No authentication required for testing
def test_consultation_detail(request, consultation_id):
    """Test endpoint to view consultation details without authentication (development only)"""
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        serializer = ConsultationDetailSerializer(consultation)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation retrieved successfully (test endpoint)',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    except Consultation.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'CONSULTATION_NOT_FOUND',
                'message': f'Consultation with ID {consultation_id} not found'
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ERROR',
                'message': str(e)
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IsDoctor(BasePermission):
    """Custom permission to allow only doctors"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'doctor'


class DoctorConsultationViewSet(ModelViewSet):
    """ViewSet for doctor's consultation management"""
    serializer_class = ConsultationListSerializer
    permission_classes = [IsDoctor]
    pagination_class = ConsultationPagination

    def get_queryset(self):
        """Filter queryset to only include consultations for the logged-in doctor"""
        return Consultation.objects.filter(doctor=self.request.user).select_related('patient', 'clinic')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['add_note', 'get_notes']:
            return ConsultationNoteSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a consultation"""
        consultation = self.get_object()
        if consultation.status != 'scheduled':
            return Response(
                {'error': 'Consultation can only be started if it is scheduled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        consultation.status = 'in_progress'
        consultation.save()
        return Response(self.get_serializer(consultation).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a consultation"""
        consultation = self.get_object()
        if consultation.status != 'in_progress':
            return Response(
                {'error': 'Consultation can only be completed if it is in progress.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        consultation.status = 'completed'
        consultation.save()
        return Response(self.get_serializer(consultation).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a consultation"""
        consultation = self.get_object()
        if consultation.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel a completed or already cancelled consultation.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        consultation.status = 'cancelled'
        consultation.save()
        return Response(self.get_serializer(consultation).data)

    @action(detail=True, methods=['post'], url_path='notes')
    def add_note(self, request, pk=None):
        """Add a note to a consultation"""
        consultation = self.get_object()
        serializer = ConsultationNoteCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(consultation=consultation, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='notes')
    def get_notes(self, request, pk=None):
        """Get notes for a consultation"""
        consultation = self.get_object()
        notes = ConsultationNote.objects.filter(consultation=consultation)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming consultations for the logged-in doctor"""
        upcoming_consultations = self.get_queryset().filter(
            status='scheduled',
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date', 'scheduled_time')
        
        page = self.paginate_queryset(upcoming_consultations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(upcoming_consultations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed consultations for the logged-in doctor"""
        completed_consultations = self.get_queryset().filter(status='completed').order_by('-scheduled_date', '-scheduled_time')
        
        page = self.paginate_queryset(completed_consultations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(completed_consultations, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_whatsapp_notification(request):
    """Test endpoint for WhatsApp notifications"""
    try:
        consultation_id = request.data.get('consultation_id')
        if not consultation_id:
            return Response(
                {'error': 'consultation_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consultation = Consultation.objects.get(id=consultation_id)
        whatsapp_service = WhatsAppNotificationService()
        
        # Test doctor notification
        doctor_result = whatsapp_service.send_doctor_appointment_notification(consultation)
        
        # Test patient notification
        patient_result = whatsapp_service.send_patient_appointment_confirmation(consultation)
        
        return Response({
            'success': True,
            'doctor_notification_sent': doctor_result,
            'patient_notification_sent': patient_result,
            'consultation_id': consultation_id,
            'doctor_name': consultation.doctor.name,
            'patient_name': consultation.patient.name
        })
        
    except Consultation.DoesNotExist:
        return Response(
            {'error': 'Consultation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )