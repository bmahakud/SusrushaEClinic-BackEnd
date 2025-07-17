from rest_framework import serializers
from django.utils import timezone
from authentication.models import User
from .models import PatientProfile, MedicalRecord, PatientDocument, PatientNote


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for patient profile"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    date_of_birth = serializers.DateField(source='user.date_of_birth', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'user_name', 'user_phone', 'user_email',
            'date_of_birth', 'gender', 'blood_group',
            'allergies', 'chronic_conditions', 'current_medications',
            'insurance_provider', 'insurance_policy_number', 'insurance_expiry',
            'preferred_language',
            'created_at', 'updated_at', 'age'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class PatientProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating patient profile"""
    
    class Meta:
        model = PatientProfile
        fields = [
            'blood_group',
            'allergies', 'chronic_conditions', 'current_medications',
            'insurance_provider', 'insurance_policy_number', 'insurance_expiry',
            'preferred_language'
        ]
    
    def create(self, validated_data):
        """Create patient profile for authenticated user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for medical records"""
    recorded_by_name = serializers.CharField(source='recorded_by.name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'record_type',
            'title', 'description', 'date_recorded', 'document',
            'recorded_by', 'recorded_by_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating medical records"""
    
    class Meta:
        model = MedicalRecord
        fields = [
            'record_type', 'title', 'description', 'date_recorded', 'document'
        ]
    
    def create(self, validated_data):
        """Create medical record for patient"""
        patient_id = self.context['view'].kwargs.get('patient_id')
        doctor = self.context['request'].user
        
        validated_data['patient_id'] = patient_id
        validated_data['recorded_by'] = doctor
        return super().create(validated_data)


class PatientDocumentSerializer(serializers.ModelSerializer):
    """Serializer for patient documents"""
    
    class Meta:
        model = PatientDocument
        fields = [
            'id', 'patient', 'document_type', 'title', 'description',
            'file',
            'is_verified', 'verified_by', 'verified_at',
            'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'updated_at']
    
    def get_file_size_mb(self, obj):
        """Get file size in MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return 0


class PatientDocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading patient documents"""
    
    class Meta:
        model = PatientDocument
        fields = [
            'document_type', 'title', 'description', 'file'
        ]
    
    def create(self, validated_data):
        """Create patient document"""
        patient_id = self.context['view'].kwargs.get('patient_id')
        uploaded_by = self.context['request'].user
        
        validated_data['patient_id'] = patient_id
        validated_data['uploaded_by'] = uploaded_by
        
        # Set file size
        if 'file' in validated_data and validated_data['file']:
            validated_data['file_size'] = validated_data['file'].size
        
        return super().create(validated_data)


class PatientNoteSerializer(serializers.ModelSerializer):
    """Serializer for patient notes"""
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    
    class Meta:
        model = PatientNote
        fields = [
            'id', 'patient', 'note',
            'is_private', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class PatientNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating patient notes"""
    
    class Meta:
        model = PatientNote
        fields = ['note', 'is_private']
    
    def create(self, validated_data):
        """Create patient note"""
        patient_id = self.context['view'].kwargs.get('patient_id')
        created_by = self.context['request'].user
        
        validated_data['patient_id'] = patient_id
        validated_data['created_by'] = created_by
        return super().create(validated_data)


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer for patient list view"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    date_of_birth = serializers.DateField(source='user.date_of_birth', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    age = serializers.ReadOnlyField()
    total_consultations = serializers.SerializerMethodField()
    last_consultation_date = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'user_name', 'user_phone', 'user_email',
            'date_of_birth', 'gender', 'blood_group', 'age',
            'total_consultations', 'last_consultation_date',
            'created_at'
        ]
    
    def get_total_consultations(self, obj):
        """Get total number of consultations"""
        return obj.user.patient_consultations.count()
    
    def get_last_consultation_date(self, obj):
        """Get last consultation date"""
        last_consultation = obj.user.patient_consultations.order_by('-created_at').first()
        if last_consultation:
            return last_consultation.created_at
        return None


class PatientSearchSerializer(serializers.Serializer):
    """Serializer for patient search"""
    query = serializers.CharField(max_length=200, required=False)
    gender = serializers.ChoiceField(
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        required=False
    )
    blood_group = serializers.ChoiceField(
        choices=[
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
        ],
        required=False
    )
    age_min = serializers.IntegerField(min_value=0, max_value=150, required=False)
    age_max = serializers.IntegerField(min_value=0, max_value=150, required=False)
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    
    def validate(self, attrs):
        """Validate search parameters"""
        min_age = attrs.get('age_min')
        max_age = attrs.get('age_max')
        if min_age and max_age and min_age > max_age:
            raise serializers.ValidationError('age_min cannot be greater than age_max')
        return attrs


class PatientStatsSerializer(serializers.Serializer):
    """Serializer for patient statistics"""
    total_patients = serializers.IntegerField()
    new_patients_this_month = serializers.IntegerField()
    active_patients = serializers.IntegerField()
    gender_distribution = serializers.DictField()
    age_distribution = serializers.DictField()
    blood_group_distribution = serializers.DictField()
    top_cities = serializers.ListField()
    consultation_stats = serializers.DictField()

