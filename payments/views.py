from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from datetime import datetime, timedelta
import json

from authentication.models import User
from .models import (
    Payment, PaymentMethod, PaymentRefund, PaymentDiscount,
    PaymentTransaction
)
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer,
    PaymentMethodSerializer, PaymentMethodCreateSerializer,
    PaymentRefundSerializer, PaymentRefundCreateSerializer,
    PaymentDiscountSerializer, PaymentTransactionSerializer,
    PaymentListSerializer,
    PaymentSearchSerializer, PaymentStatsSerializer,
    PaymentProcessSerializer, DiscountValidationSerializer,
    PaymentWebhookSerializer
)


class PaymentPagination(PageNumberPagination):
    """Custom pagination for payment lists"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PaymentViewSet(ModelViewSet):
    """ViewSet for payment management"""
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaymentPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['transaction_id', 'patient__name', 'description']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = Payment.objects.select_related('patient', 'consultation')
        
        if user.role == 'patient':
            # Patients can only see their own payments
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            # Doctors can see payments for their consultations
            return queryset.filter(consultation__doctor=user)
        elif user.role in ['admin', 'superadmin']:
            # Admins can see all payments
            return queryset
        
        return queryset.none()
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process payment"""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Only pending payments can be processed'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PaymentProcessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid payment processing data',
                    'details': serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process payment based on gateway
        gateway = serializer.validated_data['gateway']
        
        try:
            # Here you would integrate with actual payment gateways
            # For demo purposes, we'll simulate the process
            
            if gateway == 'stripe':
                result = self._process_stripe_payment(payment, serializer.validated_data)
            elif gateway == 'razorpay':
                result = self._process_razorpay_payment(payment, serializer.validated_data)
            elif gateway == 'payu':
                result = self._process_payu_payment(payment, serializer.validated_data)
            else:
                raise ValueError(f"Unsupported gateway: {gateway}")
            
            # Update payment status based on result
            if result['success']:
                payment.status = 'completed'
                payment.processed_at = timezone.now()
                payment.gateway_transaction_id = result.get('transaction_id')
                payment.gateway_response = result.get('response', {})
            else:
                payment.status = 'failed'
                payment.gateway_response = result.get('error', {})
            
            payment.save()
            
            # Create transaction record
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='payment',
                amount=payment.amount,
                is_successful=result['success'],
                gateway_transaction_id=payment.gateway_transaction_id,
                gateway_response=payment.gateway_response,
            )
            
            response_serializer = PaymentSerializer(payment)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'payment_url': result.get('payment_url'),
                'message': 'Payment processed successfully' if result['success'] else 'Payment failed',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            payment.status = 'failed'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            
            return Response({
                'success': False,
                'error': {
                    'code': 'PAYMENT_PROCESSING_ERROR',
                    'message': f'Payment processing failed: {str(e)}'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_stripe_payment(self, payment, data):
        """Process payment via Stripe (mock implementation)"""
        # Mock Stripe payment processing
        import uuid
        return {
            'success': True,
            'transaction_id': f"stripe_{uuid.uuid4().hex[:16]}",
            'payment_url': f"https://checkout.stripe.com/pay/{uuid.uuid4().hex}",
            'response': {'status': 'succeeded', 'gateway': 'stripe'}
        }
    
    def _process_razorpay_payment(self, payment, data):
        """Process payment via Razorpay (mock implementation)"""
        # Mock Razorpay payment processing
        import uuid
        return {
            'success': True,
            'transaction_id': f"razorpay_{uuid.uuid4().hex[:16]}",
            'payment_url': f"https://api.razorpay.com/v1/checkout/{uuid.uuid4().hex}",
            'response': {'status': 'captured', 'gateway': 'razorpay'}
        }
    
    def _process_payu_payment(self, payment, data):
        """Process payment via PayU (mock implementation)"""
        # Mock PayU payment processing
        import uuid
        return {
            'success': True,
            'transaction_id': f"payu_{uuid.uuid4().hex[:16]}",
            'payment_url': f"https://secure.payu.in/_payment/{uuid.uuid4().hex}",
            'response': {'status': 'success', 'gateway': 'payu'}
        }
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Initiate payment refund"""
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': 'Only completed payments can be refunded'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PaymentRefundCreateSerializer(data=request.data)
        if serializer.is_valid():
            refund = serializer.save()
            
            # Process refund (mock implementation)
            refund.status = 'completed'
            refund.processed_at = timezone.now()
            refund.save()
            
            response_serializer = PaymentRefundSerializer(refund)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Refund processed successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid refund data',
                'details': serializer.errors
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_400_BAD_REQUEST)


class PaymentMethodViewSet(ModelViewSet):
    """ViewSet for payment method management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get payment methods for authenticated user"""
        return PaymentMethod.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PaymentMethodCreateSerializer
        return PaymentMethodSerializer
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default"""
        payment_method = self.get_object()
        
        # Remove default from other methods
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        
        # Set this method as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = PaymentMethodSerializer(payment_method)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Payment method set as default',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class PaymentRefundViewSet(ModelViewSet):
    """ViewSet for payment refund management"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get refunds based on user role"""
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return PaymentRefund.objects.all()
        else:
            return PaymentRefund.objects.filter(payment__patient=user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PaymentRefundCreateSerializer
        return PaymentRefundSerializer


class PaymentDiscountViewSet(ModelViewSet):
    """ViewSet for payment discount management"""
    queryset = PaymentDiscount.objects.all()
    serializer_class = PaymentDiscountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter discounts based on user role"""
        user = self.request.user
        if user.role in ['admin', 'superadmin']:
            return PaymentDiscount.objects.all()
        else:
            # Regular users can only see active discounts
            return PaymentDiscount.objects.filter(
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now()
            )


class PaymentSearchView(APIView):
    """Search payments with advanced filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Search payments with advanced filters"""
        serializer = PaymentSearchSerializer(data=request.query_params)
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
        queryset = Payment.objects.select_related('patient', 'consultation')
        
        # Apply role-based filtering
        user = request.user
        if user.role == 'patient':
            queryset = queryset.filter(patient=user)
        elif user.role == 'doctor':
            queryset = queryset.filter(consultation__doctor=user)
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
                Q(id__icontains=query) |
                Q(description__icontains=query)
            )
        
        if search_data.get('patient_id'):
            queryset = queryset.filter(patient_id=search_data['patient_id'])
        
        if search_data.get('consultation_id'):
            queryset = queryset.filter(consultation_id=search_data['consultation_id'])
        
        if search_data.get('payment_type'):
            queryset = queryset.filter(payment_type=search_data['payment_type'])
        
        if search_data.get('status'):
            queryset = queryset.filter(status=search_data['status'])
        
        if search_data.get('payment_method'):
            queryset = queryset.filter(payment_method__icontains=search_data['payment_method'])
        
        if search_data.get('amount_min'):
            queryset = queryset.filter(amount__gte=search_data['amount_min'])
        
        if search_data.get('amount_max'):
            queryset = queryset.filter(amount__lte=search_data['amount_max'])
        
        if search_data.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=search_data['date_from'])
        
        if search_data.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=search_data['date_to'])
        
        # Paginate results
        paginator = PaymentPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = PaymentListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'message': 'Search results retrieved successfully',
                'timestamp': timezone.now().isoformat()
            })
        
        serializer = PaymentListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Search results retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class PaymentStatsView(APIView):
    """Get payment statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get payment statistics"""
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
        total_payments = Payment.objects.count()
        successful_payments = Payment.objects.filter(status='completed').count()
        failed_payments = Payment.objects.filter(status='failed').count()
        pending_payments = Payment.objects.filter(status='pending').count()
        
        # Revenue calculations
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_refunds = PaymentRefund.objects.filter(status='completed').aggregate(
            total=Sum('refund_amount')
        )['total'] or 0
        
        # Payment method distribution
        payment_method_distribution = dict(
            Payment.objects.values('payment_method').annotate(
                count=Count('payment_method')
            ).values_list('payment_method', 'count')
        )
        
        # Monthly revenue (last 12 months)
        monthly_revenue = []
        for i in range(12):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            month_revenue = Payment.objects.filter(
                status='completed',
                processed_at__gte=month_start,
                processed_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_revenue.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': float(month_revenue)
            })
        
        # Average transaction amount
        avg_amount = Payment.objects.filter(status='completed').aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        stats_data = {
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
            'pending_payments': pending_payments,
            'total_revenue': float(total_revenue),
            'total_refunds': float(total_refunds),
            'payment_method_distribution': payment_method_distribution,
            'monthly_revenue': monthly_revenue,
            'average_transaction_amount': float(avg_amount)
        }
        
        serializer = PaymentStatsSerializer(stats_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Payment statistics retrieved successfully',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)


class DiscountValidationView(APIView):
    """Validate discount codes"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Validate discount code"""
        serializer = DiscountValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid discount validation data',
                    'details': serializer.errors
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        discount_code = serializer.validated_data['discount_code']
        amount = serializer.validated_data['amount']
        
        try:
            discount = PaymentDiscount.objects.get(
                code=discount_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now()
            )
            
            # Check minimum amount
            if discount.min_order_amount and amount < discount.min_order_amount:
                return Response({
                    'success': False,
                    'error': {
                        'code': 'MINIMUM_AMOUNT_NOT_MET',
                        'message': f'Minimum amount of {discount.min_order_amount} required'
                    },
                    'timestamp': timezone.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate discount amount
            if discount.discount_type == 'percentage':
                discount_amount = (amount * discount.discount_value) / 100
            else:  # fixed
                discount_amount = discount.discount_value
            
            # Apply maximum discount limit
            if discount.max_discount_amount:
                discount_amount = min(discount_amount, discount.max_discount_amount)
            
            final_amount = amount - discount_amount
            
            return Response({
                'success': True,
                'data': {
                    'discount': PaymentDiscountSerializer(discount).data,
                    'original_amount': float(amount),
                    'discount_amount': float(discount_amount),
                    'final_amount': float(final_amount)
                },
                'message': 'Discount code validated successfully',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except PaymentDiscount.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'INVALID_DISCOUNT_CODE',
                    'message': 'Invalid or expired discount code'
                },
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebhookView(APIView):
    """Handle payment gateway webhooks"""
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request):
        """Handle payment webhook"""
        serializer = PaymentWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid webhook data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        webhook_data = serializer.validated_data
        
        try:
            # Find payment by transaction ID
            payment = Payment.objects.get(
                gateway_transaction_id=webhook_data['gateway_transaction_id']
            )
            
            # Update payment status based on webhook
            if webhook_data['status'] in ['completed', 'succeeded', 'captured']:
                payment.status = 'completed'
                payment.processed_at = timezone.now()
            elif webhook_data['status'] in ['failed', 'declined']:
                payment.status = 'failed'
            
            payment.gateway_response = webhook_data.get('metadata', {})
            payment.save()
            
            # Create transaction record
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='webhook',
                amount=webhook_data.get('amount', payment.amount),
                is_successful=payment.status == 'completed',
                gateway_transaction_id=webhook_data['gateway_transaction_id'],
                gateway_response=webhook_data.get('metadata', {}),
            )
            
            return Response({
                'success': True,
                'message': 'Webhook processed successfully'
            }, status=status.HTTP_200_OK)
            
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Webhook processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



