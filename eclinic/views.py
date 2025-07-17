from rest_framework import status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
from .models import Clinic
from .serializers import ClinicSerializer, ClinicCreateSerializer, ClinicStatsSerializer
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class ClinicPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ClinicViewSet(ModelViewSet):
    queryset = Clinic.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ClinicPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'city', 'specialties']
    ordering_fields = ['created_at', 'name', 'city']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ClinicCreateSerializer
        return ClinicSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Clinic.objects.all()
        if user.role == 'admin':
            return queryset.filter(admin=user)
        elif user.role in ['superadmin']:
            return queryset
        else:
            return queryset.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    def perform_update(self, serializer):
        serializer.save()


class ClinicServiceViewSet(ModelViewSet):
    """ViewSet for clinic service management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get services for specific clinic"""
        clinic_id = self.kwargs.get('clinic_id')
        return ClinicService.objects.filter(clinic_id=clinic_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ClinicServiceCreateSerializer
        return ClinicServiceSerializer


class ClinicInventoryViewSet(ModelViewSet):
    """ViewSet for clinic inventory management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get inventory for specific clinic"""
        clinic_id = self.kwargs.get('clinic_id')
        return ClinicInventory.objects.filter(clinic_id=clinic_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ClinicInventoryCreateSerializer
        return ClinicInventorySerializer


class ClinicAppointmentViewSet(ModelViewSet):
    """ViewSet for clinic appointment management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get appointments for specific clinic"""
        clinic_id = self.kwargs.get('clinic_id')
        user = self.request.user
        queryset = ClinicAppointment.objects.filter(clinic_id=clinic_id).select_related(
            'patient', 'doctor', 'clinic'
        )
        
        # Filter based on user role
        if user.role == 'patient':
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            return queryset.filter(doctor=user)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ClinicAppointmentCreateSerializer
        return ClinicAppointmentSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, clinic_id=None, pk=None):
        """Confirm appointment"""
        appointment = self.get_object()
        
        if appointment.status != 'scheduled':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Only scheduled appointments can be confirmed'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = 'confirmed'
        appointment.save()
        
        serializer = ClinicAppointmentSerializer(appointment)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Appointment confirmed successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, clinic_id=None, pk=None):
        """Cancel appointment"""
        appointment = self.get_object()
        
        if appointment.status in ['completed', 'cancelled']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Cannot cancel completed or already cancelled appointment'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = 'cancelled'
        appointment.save()
        
        serializer = ClinicAppointmentSerializer(appointment)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Appointment cancelled successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class ClinicReviewViewSet(ModelViewSet):
    """ViewSet for clinic review management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reviews for specific clinic"""
        clinic_id = self.kwargs.get('clinic_id')
        return ClinicReview.objects.filter(clinic_id=clinic_id).select_related('patient', 'clinic')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ClinicReviewCreateSerializer
        return ClinicReviewSerializer


class ClinicDocumentViewSet(ModelViewSet):
    """ViewSet for clinic document management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get documents for specific clinic"""
        clinic_id = self.kwargs.get('clinic_id')
        return ClinicDocument.objects.filter(clinic_id=clinic_id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ClinicDocumentCreateSerializer
        return ClinicDocumentSerializer


class ClinicSearchView(APIView):
    """Search clinics with advanced filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('query', OpenApiTypes.STR, description='Search query'),
            OpenApiParameter('city', OpenApiTypes.STR, description='City filter'),
            OpenApiParameter('state', OpenApiTypes.STR, description='State filter'),
            OpenApiParameter('specialization', OpenApiTypes.STR, description='Specialization filter'),
            OpenApiParameter('service', OpenApiTypes.STR, description='Service filter'),
            OpenApiParameter('is_verified', OpenApiTypes.BOOL, description='Verified clinic filter'),
            OpenApiParameter('latitude', OpenApiTypes.FLOAT, description='Latitude for location search'),
            OpenApiParameter('longitude', OpenApiTypes.FLOAT, description='Longitude for location search'),
            OpenApiParameter('radius_km', OpenApiTypes.FLOAT, description='Search radius in kilometers'),
        ],
        responses={200: ClinicSerializer(many=True)},
        description="Search clinics with advanced filters"
    )
    def get(self, request):
        """Search clinics with advanced filters"""
        serializer = ClinicSearchSerializer(data=request.query_params)
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
        queryset = Clinic.objects.filter(is_active=True)
        
        # Apply role-based filtering
        user = request.user
        if user.role == 'patient':
            queryset = queryset.filter(is_verified=True)
        
        # Apply search filters
        search_data = serializer.validated_data
        
        if search_data.get('query'):
            query = search_data['query']
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(specialties__icontains=query)
            )
        
        if search_data.get('city'):
            queryset = queryset.filter(city__icontains=search_data['city'])
        
        if search_data.get('state'):
            queryset = queryset.filter(state__icontains=search_data['state'])
        
        if search_data.get('specialization'):
            queryset = queryset.filter(specialties__icontains=search_data['specialization'])
        
        if search_data.get('service'):
            queryset = queryset.filter(
                clinic_services__name__icontains=search_data['service']
            ).distinct()
        
        if search_data.get('is_verified') is not None:
            queryset = queryset.filter(is_verified=search_data['is_verified'])
        
        # Location-based search
        if search_data.get('latitude') and search_data.get('longitude'):
            lat = search_data['latitude']
            lng = search_data['longitude']
            radius = search_data.get('radius_km', 10)
            
            # Simple distance calculation (for more accuracy, use PostGIS)
            queryset = queryset.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ).extra(
                where=[
                    "6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude))) <= %s"
                ],
                params=[lat, lng, lat, radius]
            )
        
        # Paginate results
        paginator = ClinicPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ClinicSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Search results retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = ClinicSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Search results retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class ClinicStatsView(APIView):
    """Get clinic statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: ClinicStatsSerializer},
        description="Get clinic statistics and analytics"
    )
    def get(self, request):
        """Get clinic statistics"""
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
        total_clinics = Clinic.objects.count()
        verified_clinics = Clinic.objects.filter(is_verified=True).count()
        active_clinics = Clinic.objects.filter(is_active=True).count()
        total_appointments = ClinicAppointment.objects.count()
        total_services = ClinicService.objects.filter(is_available=True).count()
        
        # City distribution
        city_distribution = dict(
            Clinic.objects.values('city').annotate(
                count=Count('city')
            ).order_by('-count')[:10].values_list('city', 'count')
        )
        
        # Specialization distribution
        specialization_data = []
        for clinic in Clinic.objects.exclude(specialties__isnull=True).exclude(specialties=''):
            specialties = clinic.specialties
            for spec in specialties:
                specialization_data.append(spec.strip())
        
        from collections import Counter
        specialization_distribution = dict(Counter(specialization_data).most_common(10))
        
        # Monthly registrations (last 12 months)
        monthly_registrations = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_clinics = Clinic.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            monthly_registrations.append({
                'month': month_start.strftime('%Y-%m'),
                'registrations': month_clinics
            })
        
        # Average rating
        avg_rating = ClinicReview.objects.filter(is_approved=True).aggregate(
            avg=Avg('overall_rating')
        )['avg'] or 0
        
        stats_data = {
            'total_clinics': total_clinics,
            'verified_clinics': verified_clinics,
            'active_clinics': active_clinics,
            'total_appointments': total_appointments,
            'total_services': total_services,
            'city_distribution': city_distribution,
            'specialization_distribution': specialization_distribution,
            'monthly_registrations': monthly_registrations,
            'average_rating': round(avg_rating, 2)
        }
        
        serializer = ClinicStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Clinic statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class NearbyClinicView(APIView):
    """Find nearby clinics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('latitude', OpenApiTypes.FLOAT, description='User latitude', required=True),
            OpenApiParameter('longitude', OpenApiTypes.FLOAT, description='User longitude', required=True),
            OpenApiParameter('radius_km', OpenApiTypes.FLOAT, description='Search radius in kilometers', default=10),
            OpenApiParameter('specialization', OpenApiTypes.STR, description='Specialization filter'),
        ],
        responses={200: ClinicSerializer(many=True)},
        description="Find nearby clinics based on location"
    )
    def get(self, request):
        """Find nearby clinics"""
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = float(request.query_params.get('radius_km', 10))
        specialization = request.query_params.get('specialization')
        
        if not latitude or not longitude:
            return Response({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': 'Latitude and longitude are required'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lat = float(latitude)
            lng = float(longitude)
        except ValueError:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_COORDINATES',
                    'message': 'Invalid latitude or longitude'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find nearby clinics
        queryset = Clinic.objects.filter(
            is_active=True,
            is_verified=True,
            latitude__isnull=False,
            longitude__isnull=False
        ).extra(
            select={
                'distance': "6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))"
            },
            select_params=[lat, lng, lat],
            where=[
                "6371 * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude))) <= %s"
            ],
            params=[lat, lng, lat, radius_km],
            order_by=['distance']
        )
        
        # Apply specialization filter if provided
        if specialization:
            queryset = queryset.filter(specialties__icontains=specialization)
        
        serializer = ClinicSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Nearby clinics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)



