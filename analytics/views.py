from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, F
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from datetime import datetime, timedelta
import csv
import json

from authentication.models import User
from consultations.models import Consultation
from prescriptions.models import Prescription
from payments.models import Payment
from eclinic.models import Clinic
from .models import (
    UserAnalytics, ConsultationAnalytics, RevenueAnalytics,
    DoctorPerformanceAnalytics, ClinicPerformanceAnalytics, SystemPerformanceMetrics,
    UserActivityLog, PlatformMetrics
)
from .serializers import (
    UserAnalyticsSerializer, RevenueAnalyticsSerializer,
    DoctorPerformanceSerializer,
    PlatformMetricsSerializer, SystemPerformanceMetricsSerializer,
    DashboardStatsSerializer, UserGrowthSerializer,
    RevenueReportSerializer, ConsultationAnalyticsSerializer,
    GeographicAnalyticsSerializer, PerformanceMetricsSerializer,
    CustomReportSerializer, ExportRequestSerializer,
    AlertConfigSerializer, RealTimeMetricsSerializer
)


class AnalyticsPagination(PageNumberPagination):
    """Custom pagination for analytics lists"""
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserAnalyticsViewSet(ReadOnlyModelViewSet):
    """ViewSet for user analytics"""
    queryset = UserAnalytics.objects.all()
    serializer_class = UserAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AnalyticsPagination
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter analytics based on permissions"""
        if self.request.user.role not in ['admin', 'superadmin']:
            return UserAnalytics.objects.none()
        return super().get_queryset()


class RevenueAnalyticsViewSet(ReadOnlyModelViewSet):
    """ViewSet for revenue analytics"""
    queryset = RevenueAnalytics.objects.all()
    serializer_class = RevenueAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AnalyticsPagination
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter analytics based on permissions"""
        if self.request.user.role not in ['admin', 'superadmin']:
            return RevenueAnalytics.objects.none()
        return super().get_queryset()


class DoctorPerformanceViewSet(ReadOnlyModelViewSet):
    """ViewSet for doctor performance analytics"""
    queryset = DoctorPerformanceAnalytics.objects.all()
    serializer_class = DoctorPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AnalyticsPagination
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter analytics based on permissions"""
        user = self.request.user
        if user.role == 'doctor':
            return DoctorPerformanceAnalytics.objects.filter(doctor=user)
        elif user.role in ['admin', 'superadmin']:
            return super().get_queryset()
        return DoctorPerformanceAnalytics.objects.none()


class DashboardStatsView(APIView):
    """Get dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: DashboardStatsSerializer},
        description="Get dashboard statistics overview"
    )
    def get(self, request):
        """Get dashboard statistics"""
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
        
        today = timezone.now().date()
        
        # Calculate basic statistics
        total_users = User.objects.count()
        total_patients = User.objects.filter(role='patient').count()
        total_doctors = User.objects.filter(role='doctor').count()
        total_consultations = Consultation.objects.count()
        total_prescriptions = Prescription.objects.count()
        
        # Revenue statistics
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Today's statistics
        active_users_today = User.objects.filter(last_login__date=today).count()
        consultations_today = Consultation.objects.filter(created_at__date=today).count()
        revenue_today = Payment.objects.filter(
            status='completed', payment_date__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Growth metrics (compared to last month)
        last_month = today - timedelta(days=30)
        
        users_last_month = User.objects.filter(created_at__date__lte=last_month).count()
        consultations_last_month = Consultation.objects.filter(created_at__date__lte=last_month).count()
        revenue_last_month = Payment.objects.filter(
            status='completed', payment_date__date__lte=last_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        growth_metrics = {
            'user_growth': self._calculate_growth_rate(total_users, users_last_month),
            'consultation_growth': self._calculate_growth_rate(total_consultations, consultations_last_month),
            'revenue_growth': self._calculate_growth_rate(float(total_revenue), float(revenue_last_month))
        }
        
        stats_data = {
            'total_users': total_users,
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_consultations': total_consultations,
            'total_prescriptions': total_prescriptions,
            'total_revenue': float(total_revenue),
            'active_users_today': active_users_today,
            'consultations_today': consultations_today,
            'revenue_today': float(revenue_today),
            'growth_metrics': growth_metrics
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Dashboard statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    def _calculate_growth_rate(self, current, previous):
        """Calculate growth rate percentage"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)


class UserGrowthAnalyticsView(APIView):
    """Get user growth analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter('period', OpenApiTypes.STR, description='Period: day, week, month', default='month'),
            OpenApiParameter('days', OpenApiTypes.INT, description='Number of days to analyze', default=30),
        ],
        responses={200: UserGrowthSerializer(many=True)},
        description="Get user growth analytics"
    )
    def get(self, request):
        """Get user growth analytics"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        period = request.query_params.get('period', 'month')
        days = int(request.query_params.get('days', 30))
        
        # Generate growth data
        growth_data = []
        
        if period == 'day':
            for i in range(days):
                date = timezone.now().date() - timedelta(days=i)
                total_users = User.objects.filter(created_at__date__lte=date).count()
                new_users = User.objects.filter(created_at__date=date).count()
                
                user_type_breakdown = {
                    'patients': User.objects.filter(created_at__date=date, role='patient').count(),
                    'doctors': User.objects.filter(created_at__date=date, role='doctor').count(),
                    'admins': User.objects.filter(created_at__date=date, role__in=['admin', 'superadmin']).count()
                }
                
                growth_data.append({
                    'period': date.strftime('%Y-%m-%d'),
                    'total_users': total_users,
                    'new_users': new_users,
                    'growth_rate': 0.0,  # Calculate if needed
                    'user_type_breakdown': user_type_breakdown
                })
        
        elif period == 'month':
            for i in range(12):  # Last 12 months
                month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                
                total_users = User.objects.filter(created_at__lt=month_end).count()
                new_users = User.objects.filter(
                    created_at__gte=month_start, created_at__lt=month_end
                ).count()
                
                user_type_breakdown = {
                    'patients': User.objects.filter(
                        created_at__gte=month_start, created_at__lt=month_end, role='patient'
                    ).count(),
                    'doctors': User.objects.filter(
                        created_at__gte=month_start, created_at__lt=month_end, role='doctor'
                    ).count(),
                    'admins': User.objects.filter(
                        created_at__gte=month_start, created_at__lt=month_end, 
                        role__in=['admin', 'superadmin']
                    ).count()
                }
                
                growth_data.append({
                    'period': month_start.strftime('%Y-%m'),
                    'total_users': total_users,
                    'new_users': new_users,
                    'growth_rate': 0.0,
                    'user_type_breakdown': user_type_breakdown
                })
        
        serializer = UserGrowthSerializer(growth_data, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'User growth analytics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class ConsultationAnalyticsView(APIView):
    """Get consultation analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get consultation analytics"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Basic consultation statistics
        total_consultations = Consultation.objects.count()
        completed_consultations = Consultation.objects.filter(status='completed').count()
        cancelled_consultations = Consultation.objects.filter(status='cancelled').count()
        
        # Average duration
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
        
        # Consultation types distribution
        consultation_types = dict(
            Consultation.objects.values('consultation_type').annotate(
                count=Count('consultation_type')
            ).values_list('consultation_type', 'count')
        )
        
        # Peak hours analysis
        from django.db.models import Extract
        peak_hours = list(
            Consultation.objects.filter(started_at__isnull=False).annotate(
                hour=Extract('started_at', 'hour')
            ).values('hour').annotate(
                count=Count('hour')
            ).order_by('-count')[:5].values_list('hour', 'count')
        )
        
        # Doctor performance
        doctor_performance = list(
            Consultation.objects.filter(status='completed').values(
                'doctor__name'
            ).annotate(
                total_consultations=Count('id'),
                avg_rating=Avg('rating')
            ).order_by('-total_consultations')[:10]
        )
        
        analytics_data = {
            'total_consultations': total_consultations,
            'completed_consultations': completed_consultations,
            'cancelled_consultations': cancelled_consultations,
            'average_duration': avg_duration,
            'consultation_types': consultation_types,
            'peak_hours': peak_hours,
            'doctor_performance': doctor_performance
        }
        
        serializer = ConsultationAnalyticsSerializer(analytics_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Consultation analytics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class RevenueReportView(APIView):
    """Get revenue reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get revenue reports"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        period = request.query_params.get('period', 'month')
        
        # Calculate total revenue
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Revenue breakdown by payment type
        revenue_breakdown = dict(
            Payment.objects.filter(status='completed').values('payment_type').annotate(
                total=Sum('amount')
            ).values_list('payment_type', 'total')
        )
        
        # Top revenue sources (doctors)
        top_revenue_sources = list(
            Payment.objects.filter(
                status='completed', consultation__isnull=False
            ).values('consultation__doctor__name').annotate(
                total_revenue=Sum('amount')
            ).order_by('-total_revenue')[:10]
        )
        
        report_data = {
            'period': period,
            'total_revenue': float(total_revenue),
            'revenue_breakdown': {k: float(v) for k, v in revenue_breakdown.items()},
            'growth_rate': 0.0,  # Calculate if needed
            'top_revenue_sources': top_revenue_sources
        }
        
        serializer = RevenueReportSerializer(report_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Revenue report retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class GeographicAnalyticsView(APIView):
    """Get geographic analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get geographic analytics"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        # User distribution by city
        user_distribution = dict(
            User.objects.exclude(city__isnull=True).exclude(city='').values('city').annotate(
                count=Count('city')
            ).order_by('-count')[:20].values_list('city', 'count')
        )
        
        # Consultation distribution
        consultation_distribution = dict(
            Consultation.objects.filter(
                patient__city__isnull=False
            ).exclude(patient__city='').values('patient__city').annotate(
                count=Count('patient__city')
            ).order_by('-count')[:20].values_list('patient__city', 'count')
        )
        
        # Revenue distribution
        revenue_distribution = dict(
            Payment.objects.filter(
                status='completed', user__city__isnull=False
            ).exclude(user__city='').values('user__city').annotate(
                total=Sum('amount')
            ).order_by('-total')[:20].values_list('user__city', 'total')
        )
        
        # Top cities
        top_cities = list(user_distribution.keys())[:10]
        
        analytics_data = {
            'user_distribution': user_distribution,
            'consultation_distribution': consultation_distribution,
            'revenue_distribution': {k: float(v) for k, v in revenue_distribution.items()},
            'top_cities': top_cities,
            'growth_by_region': {}  # Implement if needed
        }
        
        serializer = GeographicAnalyticsSerializer(analytics_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Geographic analytics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class RealTimeMetricsView(APIView):
    """Get real-time metrics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get real-time metrics"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Real-time metrics
        active_users = User.objects.filter(last_login__gte=one_hour_ago).count()
        ongoing_consultations = Consultation.objects.filter(status='in_progress').count()
        pending_payments = Payment.objects.filter(status='pending').count()
        
        # System status (simplified)
        system_status = 'healthy'  # Implement actual health check
        
        # API calls per minute (mock data)
        api_calls_per_minute = 150  # Implement actual tracking
        
        # Error rate last hour
        error_rate_last_hour = 0.5  # Implement actual error tracking
        
        # Database connections (mock)
        database_connections = 25
        
        # Queue size (mock)
        queue_size = 10
        
        metrics_data = {
            'active_users': active_users,
            'ongoing_consultations': ongoing_consultations,
            'pending_payments': pending_payments,
            'system_status': system_status,
            'api_calls_per_minute': api_calls_per_minute,
            'error_rate_last_hour': error_rate_last_hour,
            'database_connections': database_connections,
            'queue_size': queue_size,
            'timestamp': now
        }
        
        serializer = RealTimeMetricsSerializer(metrics_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Real-time metrics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class CustomReportView(APIView):
    """Generate custom reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate custom report"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CustomReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid report parameters',
                    'details': serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        report_data = serializer.validated_data
        
        # Generate report based on type
        if report_data['report_type'] == 'user_growth':
            result = self._generate_user_growth_report(report_data)
        elif report_data['report_type'] == 'revenue':
            result = self._generate_revenue_report(report_data)
        elif report_data['report_type'] == 'consultation':
            result = self._generate_consultation_report(report_data)
        else:
            result = {'message': 'Report type not implemented yet'}
        
        return Response({
            'success': True,
            'data': result,
            'message': 'Custom report generated successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    def _generate_user_growth_report(self, params):
        """Generate user growth report"""
        # Implement user growth report logic
        return {'report_type': 'user_growth', 'data': []}
    
    def _generate_revenue_report(self, params):
        """Generate revenue report"""
        # Implement revenue report logic
        return {'report_type': 'revenue', 'data': []}
    
    def _generate_consultation_report(self, params):
        """Generate consultation report"""
        # Implement consultation report logic
        return {'report_type': 'consultation', 'data': []}


class ExportDataView(APIView):
    """Export data in various formats"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Export data"""
        if request.user.role not in ['admin', 'superadmin']:
            return Response({
                'success': False,
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'Insufficient permissions'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ExportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid export parameters',
                    'details': serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        export_data = serializer.validated_data
        
        # Generate export file
        if export_data['format'] == 'csv':
            response = self._export_csv(export_data)
        elif export_data['format'] == 'excel':
            response = self._export_excel(export_data)
        elif export_data['format'] == 'pdf':
            response = self._export_pdf(export_data)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'UNSUPPORTED_FORMAT',
                    'message': 'Export format not supported'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return response
    
    def _export_csv(self, params):
        """Export data as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{params["export_type"]}_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Sample', 'Data', 'Export'])
        writer.writerow(['Row 1', 'Data 1', 'Value 1'])
        
        return response
    
    def _export_excel(self, params):
        """Export data as Excel"""
        # Implement Excel export
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{params["export_type"]}_export.xlsx"'
        return response
    
    def _export_pdf(self, params):
        """Export data as PDF"""
        # Implement PDF export
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{params["export_type"]}_export.pdf"'
        return response





