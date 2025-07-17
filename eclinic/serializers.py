from rest_framework import serializers
from django.utils import timezone
from django.db import models
from authentication.models import User
from .models import (
    Clinic, ClinicService, ClinicInventory,
    ClinicAppointment, ClinicReview, ClinicDocument
)


class ClinicSerializer(serializers.ModelSerializer):
    admin = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'clinic_type', 'description',
            'phone', 'email', 'website',
            'street', 'city', 'state', 'pincode', 'country',
            'latitude', 'longitude', 'operating_hours',
            'specialties', 'services', 'facilities',
            'registration_number', 'license_number', 'accreditation',
            'logo', 'cover_image', 'gallery_images',
            'is_active', 'is_verified', 'accepts_online_consultations',
            'admin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']

class ClinicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = [
            'name', 'clinic_type', 'description',
            'phone', 'email', 'website',
            'street', 'city', 'state', 'pincode', 'country',
            'latitude', 'longitude', 'operating_hours',
            'specialties', 'services', 'facilities',
            'registration_number', 'license_number', 'accreditation',
            'logo', 'cover_image', 'gallery_images',
            'is_active', 'accepts_online_consultations',
        ]

    def create(self, validated_data):
        # Set admin from context (request.user)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['admin'] = request.user
        return super().create(validated_data)


class ClinicServiceSerializer(serializers.ModelSerializer):
    """Serializer for clinic service"""
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = ClinicService
        fields = [
            'id', 'clinic', 'clinic_name', 'name', 'category', 'description',
            'base_price', 'price_range_min', 'price_range_max', 'is_available',
            'requires_appointment', 'estimated_duration', 'preparation_required',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clinic service"""
    
    class Meta:
        model = ClinicService
        fields = [
            'name', 'category', 'description', 'base_price', 'price_range_min',
            'price_range_max', 'is_available', 'requires_appointment',
            'estimated_duration', 'preparation_required'
        ]
    
    def create(self, validated_data):
        """Create clinic service"""
        clinic_id = self.context['view'].kwargs.get('clinic_id')
        validated_data['clinic_id'] = clinic_id
        return super().create(validated_data)


class ClinicInventorySerializer(serializers.ModelSerializer):
    """Serializer for clinic inventory"""
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = ClinicInventory
        fields = [
            'id', 'clinic', 'clinic_name', 'item_name', 'category',
            'description', 'brand', 'model_number', 'current_stock',
            'minimum_stock', 'maximum_stock', 'unit', 'unit_cost',
            'selling_price', 'batch_number', 'expiry_date', 'supplier_name',
            'supplier_contact', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicInventoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clinic inventory"""
    
    class Meta:
        model = ClinicInventory
        fields = [
            'item_name', 'category', 'description', 'brand', 'model_number',
            'current_stock', 'minimum_stock', 'maximum_stock', 'unit', 'unit_cost',
            'selling_price', 'batch_number', 'expiry_date', 'supplier_name',
            'supplier_contact', 'is_active'
        ]
    
    def create(self, validated_data):
        """Create clinic inventory item"""
        clinic_id = self.context['view'].kwargs.get('clinic_id')
        validated_data['clinic_id'] = clinic_id
        return super().create(validated_data)


class ClinicAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for clinic appointment"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = ClinicAppointment
        fields = [
            'id', 'clinic', 'patient', 'doctor', 'clinic_name',
            'patient_name', 'doctor_name', 'appointment_date',
            'appointment_time', 'status', 'reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicAppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clinic appointment"""
    
    class Meta:
        model = ClinicAppointment
        fields = [
            'doctor', 'appointment_date', 'appointment_time', 'reason'
        ]
    
    def create(self, validated_data):
        """Create clinic appointment"""
        clinic_id = self.context['view'].kwargs.get('clinic_id')
        patient = self.context['request'].user
        
        validated_data['clinic_id'] = clinic_id
        validated_data['patient'] = patient
        validated_data['status'] = 'scheduled'
        
        return super().create(validated_data)


class ClinicReviewSerializer(serializers.ModelSerializer):
    """Serializer for clinic review"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = ClinicReview
        fields = [
            'id', 'clinic', 'patient', 'clinic_name', 'patient_name',
            'overall_rating', 'cleanliness_rating', 'staff_rating',
            'facilities_rating', 'wait_time_rating', 'review_text', 
            'is_anonymous', 'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']


class ClinicReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clinic review"""
    
    class Meta:
        model = ClinicReview
        fields = [
            'overall_rating', 'cleanliness_rating', 'staff_rating',
            'facilities_rating', 'wait_time_rating', 'review_text', 'is_anonymous'
        ]
    
    def create(self, validated_data):
        """Create clinic review"""
        clinic_id = self.context['view'].kwargs.get('clinic_id')
        patient = self.context['request'].user
        
        validated_data['clinic_id'] = clinic_id
        validated_data['patient'] = patient
        validated_data['is_approved'] = True
        
        return super().create(validated_data)


class ClinicDocumentSerializer(serializers.ModelSerializer):
    """Serializer for clinic document"""
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    
    class Meta:
        model = ClinicDocument
        fields = [
            'id', 'clinic', 'clinic_name', 'document_type', 'title',
            'description', 'file', 'uploaded_by', 'uploaded_by_name',
            'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'updated_at']


class ClinicDocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating clinic document"""
    
    class Meta:
        model = ClinicDocument
        fields = ['document_type', 'title', 'description', 'file']
    
    def create(self, validated_data):
        """Create clinic document"""
        clinic_id = self.context['view'].kwargs.get('clinic_id')
        uploaded_by = self.context['request'].user
        
        validated_data['clinic_id'] = clinic_id
        validated_data['uploaded_by'] = uploaded_by
        
        return super().create(validated_data)


class ClinicListSerializer(serializers.ModelSerializer):
    """Serializer for clinic list view"""
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    total_doctors = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'clinic_type', 'description', 'admin_name',
            'phone', 'email', 'street', 'city', 'state', 'country',
            'total_doctors', 'average_rating', 'is_verified', 'is_active',
            'accepts_online_consultations', 'accepts_walk_ins', 'created_at'
        ]
        read_only_fields = ['id', 'total_doctors', 'average_rating', 'created_at']
    
    def get_total_doctors(self, obj):
        """Get total number of doctors in clinic"""
        return obj.doctors.filter(is_active=True).count()
    
    def get_average_rating(self, obj):
        """Get average rating of clinic"""
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(avg=models.Avg('overall_rating'))['avg'], 2)
        return 0


class ClinicSearchSerializer(serializers.Serializer):
    """Serializer for clinic search"""
    query = serializers.CharField(max_length=200, required=False)
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    specialization = serializers.CharField(max_length=100, required=False)
    service = serializers.CharField(max_length=100, required=False)
    is_verified = serializers.BooleanField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    radius_km = serializers.FloatField(required=False, default=10)
    
    def validate(self, attrs):
        """Validate search parameters"""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        if (latitude is not None and longitude is None) or (latitude is None and longitude is not None):
            raise serializers.ValidationError('Both latitude and longitude must be provided for location-based search')
        
        return attrs


class ClinicStatsSerializer(serializers.Serializer):
    """Serializer for clinic statistics"""
    total_clinics = serializers.IntegerField()
    verified_clinics = serializers.IntegerField()
    active_clinics = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    total_doctors = serializers.IntegerField()
    total_services = serializers.IntegerField()
    city_distribution = serializers.DictField()
    specialization_distribution = serializers.DictField()
    monthly_registrations = serializers.ListField()
    average_rating = serializers.FloatField()

