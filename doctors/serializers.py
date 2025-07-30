from rest_framework import serializers
from django.utils import timezone
import pytz
from authentication.models import User
from .models import (
    DoctorProfile, DoctorEducation, DoctorExperience, 
    DoctorDocument, DoctorSchedule, DoctorReview, DoctorSlot
)
from utils.signed_urls import get_signed_media_url


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for doctor profile"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    experience_years = serializers.ReadOnlyField()
    meeting_link = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.SerializerMethodField()
    # Note: Using 'rating' field from model instead of 'average_rating'
    
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'user_name', 'user_phone', 'user_email',
            'profile_picture',
            'license_number', 'qualification', 'specialization', 'sub_specialization',
            'experience_years', 'consultation_fee', 'online_consultation_fee',
            'languages_spoken', 'bio', 'achievements',
            'is_verified', 'consultation_duration',
            'is_online_consultation_available', 'is_active',
            'rating', 'total_reviews', 'clinic_name', 'clinic_address',
            'is_accepting_patients', 'date_of_birth', 'date_of_anniversary',
            'created_at', 'updated_at', 'meeting_link'
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'rating', 'total_reviews', 'created_at', 'updated_at']

    def get_meeting_link(self, obj):
        return obj.meeting_link
    
    def get_profile_picture(self, obj):
        """Generate signed URL for profile picture"""
        if obj.user.profile_picture:
            return get_signed_media_url(str(obj.user.profile_picture))
        return None


class DoctorProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating doctor profile"""
    
    class Meta:
        model = DoctorProfile
        fields = [
            'license_number', 'qualification', 'specialization', 'sub_specialization',
            'consultation_fee', 'online_consultation_fee', 'languages_spoken',
            'bio', 'achievements', 'consultation_duration',
            'is_online_consultation_available', 'clinic_name', 'clinic_address',
            'date_of_birth', 'date_of_anniversary'
        ]
    
    def create(self, validated_data):
        """Create doctor profile for authenticated user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class DoctorEducationSerializer(serializers.ModelSerializer):
    """Serializer for doctor education"""
    
    class Meta:
        model = DoctorEducation
        fields = [
            'id', 'doctor', 'degree', 'institution', 'year_of_completion',
            'grade_or_percentage', 'certificate', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']


class DoctorExperienceSerializer(serializers.ModelSerializer):
    """Serializer for doctor experience"""
    
    class Meta:
        model = DoctorExperience
        fields = [
            'id', 'doctor', 'organization', 'position',
            'start_date', 'end_date', 'is_current', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorDocumentSerializer(serializers.ModelSerializer):
    """Serializer for doctor documents"""
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.name', read_only=True)
    
    class Meta:
        model = DoctorDocument
        fields = [
            'id', 'doctor', 'doctor_name', 'document_type', 'title', 'description',
            'file', 'is_verified', 'verified_by', 'verified_by_name', 'verified_at',
            'verification_notes', 'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_by', 'verified_at', 'uploaded_at', 'updated_at']


class DoctorScheduleSerializer(serializers.ModelSerializer):
    """Serializer for doctor schedule"""
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'id', 'doctor', 'day_of_week', 'start_time', 'end_time',
            'is_available', 'break_start_time', 'break_end_time',
            'break_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorReviewSerializer(serializers.ModelSerializer):
    """Serializer for doctor reviews"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    class Meta:
        model = DoctorReview
        fields = [
            'id', 'doctor', 'patient', 'patient_name', 'consultation',
            'rating', 'communication_rating', 'treatment_rating',
            'punctuality_rating', 'review_text', 'is_anonymous',
            'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'patient', 'is_approved', 'created_at']


class DoctorListSerializer(serializers.ModelSerializer):
    """Serializer for doctor list view (now includes all fields for superadmin dashboard)"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    experience_years = serializers.ReadOnlyField()
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'user_name', 'user_phone', 'user_email',
            'profile_picture',
            'license_number', 'qualification', 'specialization', 'sub_specialization',
            'experience_years', 'consultation_fee', 'online_consultation_fee',
            'languages_spoken', 'bio', 'achievements',
            'is_verified', 'consultation_duration',
            'is_online_consultation_available', 'is_active',
            'rating', 'total_reviews', 'clinic_name', 'clinic_address',
            'is_accepting_patients', 'date_of_birth', 'date_of_anniversary',
            'created_at', 'updated_at'
        ]
    
    def get_profile_picture(self, obj):
        """Generate signed URL for profile picture"""
        if obj.user.profile_picture:
            return get_signed_media_url(str(obj.user.profile_picture))
        return None


class DoctorSearchSerializer(serializers.Serializer):
    """Serializer for doctor search"""
    query = serializers.CharField(max_length=200, required=False)
    specialization = serializers.CharField(max_length=100, required=False)
    sub_specialization = serializers.CharField(max_length=100, required=False)
    min_experience = serializers.IntegerField(min_value=0, required=False)
    max_experience = serializers.IntegerField(min_value=0, required=False)
    min_fee = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
    max_fee = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
    languages = serializers.ListField(child=serializers.CharField(), required=False)
    consultation_type = serializers.ChoiceField(
        choices=[('in_person', 'In Person'), ('online', 'Online'), ('both', 'Both')],
        required=False
    )
    rating_min = serializers.DecimalField(max_digits=3, decimal_places=1, min_value=0, max_value=5, required=False)
    is_verified = serializers.BooleanField(required=False)
    # Note: emergency_available field removed as it doesn't exist in the model
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    
    def validate(self, attrs):
        """Validate search parameters"""
        min_exp = attrs.get('min_experience')
        max_exp = attrs.get('max_experience')
        min_fee = attrs.get('min_fee')
        max_fee = attrs.get('max_fee')
        
        if min_exp and max_exp and min_exp > max_exp:
            raise serializers.ValidationError('min_experience cannot be greater than max_experience')
        
        if min_fee and max_fee and min_fee > max_fee:
            raise serializers.ValidationError('min_fee cannot be greater than max_fee')
        
        return attrs


class DoctorStatsSerializer(serializers.Serializer):
    """Serializer for doctor statistics"""
    total_doctors = serializers.IntegerField()
    active_doctors = serializers.IntegerField()
    new_this_month = serializers.IntegerField()
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    verified_doctors = serializers.IntegerField()
    specialization_distribution = serializers.DictField()
    experience_distribution = serializers.DictField()
    average_consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    top_rated_doctors = serializers.ListField()
    consultation_stats = serializers.DictField()


class DoctorScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating doctor schedule"""
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'day_of_week', 'start_time', 'end_time', 'is_available',
            'break_start_time', 'break_end_time', 'break_reason'
        ]
    
    def create(self, validated_data):
        """Create schedule for doctor"""
        doctor_id = self.context['view'].kwargs.get('doctor_id')
        doctor = User.objects.get(id=doctor_id)
        validated_data['doctor'] = doctor
        return super().create(validated_data)


class DoctorSlotSerializer(serializers.ModelSerializer):
    """Serializer for doctor slots (multiple slots per day)"""
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = DoctorSlot
        fields = [
            'id', 'doctor', 'date', 'start_time', 'end_time', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']

    def create(self, validated_data):
        doctor_id = self.context['view'].kwargs.get('doctor_id')
        doctor = User.objects.get(id=doctor_id)
        validated_data['doctor'] = doctor
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ist = pytz.timezone('Asia/Kolkata')
        for field in ['created_at', 'updated_at']:
            if data.get(field):
                dt = getattr(instance, field)
                if timezone.is_aware(dt):
                    data[field] = dt.astimezone(ist).isoformat()
        return data

    def validate(self, data):
        # Get doctor from context since it's read-only in the serializer
        doctor_id = self.context['view'].kwargs.get('doctor_id')
        if not doctor_id:
            raise serializers.ValidationError("Doctor ID is required")
        
        try:
            doctor = User.objects.get(id=doctor_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Doctor not found")
        
        date = data['date']
        start_time = data['start_time']
        end_time = data['end_time']

        from consultations.models import Consultation
        # Check for overlapping consultations
        overlapping = Consultation.objects.filter(
            doctor=doctor,
            scheduled_date=date,
            status__in=['scheduled', 'in_progress']
        ).filter(
            scheduled_time__lt=end_time,
        ).exclude(
            scheduled_time__gte=end_time
        )

        if overlapping.exists():
            raise serializers.ValidationError("This doctor already has a consultation in this time slot.")

        return data

