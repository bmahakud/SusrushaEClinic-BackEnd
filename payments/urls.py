from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'', views.PaymentViewSet, basename='payment')
router.register(r'methods', views.PaymentMethodViewSet, basename='payment-method')
router.register(r'refunds', views.PaymentRefundViewSet, basename='payment-refund')
router.register(r'discounts', views.PaymentDiscountViewSet, basename='payment-discount')

urlpatterns = [
    # Payment search and statistics
    path('search/', views.PaymentSearchView.as_view(), name='payment-search'),
    path('stats/', views.PaymentStatsView.as_view(), name='payment-stats'),
    
    # Discount validation
    path('validate-discount/', views.DiscountValidationView.as_view(), name='validate-discount'),
    
    # Payment webhooks
    path('webhook/', views.PaymentWebhookView.as_view(), name='payment-webhook'),

    # Payment initiation (PhonePe etc.)
    path('initiate/', views.PaymentInitiateView.as_view(), name='payment-initiate'),
    # Include router URLs
    path('', include(router.urls)),
]

