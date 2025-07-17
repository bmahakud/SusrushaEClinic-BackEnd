from rest_framework import serializers
from django.utils import timezone
from authentication.models import User
from .models import (
    Prescription, Medication, MedicationReminder, 
    PrescriptionAttachment, PrescriptionNote
)

class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for prescription"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    consultation_id = serializers.CharField(source='consultation.id', read_only=True)
    total_medications = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'doctor', 'consultation', 'patient_name', 
            'doctor_name', 'consultation_id', 'diagnosis', 'symptoms', 
            'general_instructions', 'header', 'body', 'footer', 'issued_date', 'valid_until', 'status',
            'follow_up_required', 'follow_up_date', 'follow_up_instructions',
            'digital_signature', 'is_verified', 'verification_code',
            'total_medications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_medications', 'issued_date', 'created_at', 'updated_at']
    
    def get_total_medications(self, obj):
        """Get total number of medications in prescription"""
        return obj.medications.count()


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating prescription"""
    
    class Meta:
        model = Prescription
        fields = [
            'patient', 'consultation', 'diagnosis', 'symptoms',
            'general_instructions', 'header', 'body', 'footer', 'valid_until', 'follow_up_required',
            'follow_up_date', 'follow_up_instructions'
        ]
    
    def create(self, validated_data):
        """Create prescription"""
        doctor = self.context['request'].user
        validated_data['doctor'] = doctor
        validated_data['status'] = 'active'
        return super().create(validated_data)


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for medication"""
    
    class Meta:
        model = Medication
        fields = [
            'id', 'prescription', 'name', 'generic_name', 'brand_name',
            'strength', 'dosage_form', 'dosage', 'frequency', 'custom_frequency',
            'timing', 'duration_days', 'total_quantity', 'special_instructions',
            'side_effects_warning', 'substitution_allowed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating medication"""
    
    class Meta:
        model = Medication
        fields = [
            'name', 'generic_name', 'brand_name', 'strength', 'dosage_form',
            'dosage', 'frequency', 'custom_frequency', 'timing', 'duration_days',
            'total_quantity', 'special_instructions', 'side_effects_warning',
            'substitution_allowed'
        ]
    
    def create(self, validated_data):
        """Create medication for prescription"""
        prescription_id = self.context['view'].kwargs.get('prescription_id')
        validated_data['prescription_id'] = prescription_id
        return super().create(validated_data)


class MedicationReminderSerializer(serializers.ModelSerializer):
    """Serializer for medication reminder"""
    medication_name = serializers.CharField(source='medication.name', read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    
    class Meta:
        model = MedicationReminder
        fields = [
            'id', 'patient', 'medication', 'patient_name', 'medication_name',
            'reminder_times', 'is_active', 'sms_enabled', 'email_enabled',
            'push_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicationReminderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating medication reminder"""
    
    class Meta:
        model = MedicationReminder
        fields = [
            'medication', 'reminder_times', 'is_active', 'sms_enabled',
            'email_enabled', 'push_enabled'
        ]
    
    def create(self, validated_data):
        """Create medication reminder"""
        patient = self.context['request'].user
        validated_data['patient'] = patient
        return super().create(validated_data)


class PrescriptionAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for prescription attachments"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    
    class Meta:
        model = PrescriptionAttachment
        fields = [
            'id', 'prescription', 'attachment_type', 'description',
            'file', 'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


class PrescriptionAttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating prescription attachments"""
    
    class Meta:
        model = PrescriptionAttachment
        fields = ['attachment_type', 'description', 'file']
    
    def create(self, validated_data):
        """Create attachment for prescription"""
        prescription_id = self.context['view'].kwargs.get('prescription_id')
        uploaded_by = self.context['request'].user
        
        validated_data['prescription_id'] = prescription_id
        validated_data['uploaded_by'] = uploaded_by
        return super().create(validated_data)


class PrescriptionNoteSerializer(serializers.ModelSerializer):
    """Serializer for prescription notes"""
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    
    class Meta:
        model = PrescriptionNote
        fields = [
            'id', 'prescription', 'note', 'is_patient_visible',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class PrescriptionNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating prescription notes"""
    
    class Meta:
        model = PrescriptionNote
        fields = ['note', 'is_patient_visible']
    
    def create(self, validated_data):
        """Create note for prescription"""
        prescription_id = self.context['view'].kwargs.get('prescription_id')
        created_by = self.context['request'].user
        
        validated_data['prescription_id'] = prescription_id
        validated_data['created_by'] = created_by
        return super().create(validated_data)


class PrescriptionListSerializer(serializers.ModelSerializer):
    """Serializer for prescription list view"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    total_medications = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'doctor', 'patient_name', 'doctor_name',
            'diagnosis', 'header', 'body', 'footer', 'total_medications', 'status', 'issued_date',
            'valid_until', 'follow_up_required', 'follow_up_date', 'created_at'
        ]
    
    def get_total_medications(self, obj):
        """Get total number of medications in prescription"""
        return obj.medications.count()


class PrescriptionSearchSerializer(serializers.Serializer):
    """Serializer for prescription search"""
    query = serializers.CharField(max_length=200, required=False)
    patient_id = serializers.IntegerField(required=False)
    doctor_id = serializers.IntegerField(required=False)
    consultation_id = serializers.CharField(max_length=20, required=False)
    prescription_number = serializers.CharField(max_length=50, required=False)
    status = serializers.ChoiceField(
        choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('expired', 'Expired')],
        required=False
    )
    is_digital = serializers.BooleanField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    medicine_name = serializers.CharField(max_length=200, required=False)
    
    def validate(self, attrs):
        """Validate search parameters"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError('date_from cannot be greater than date_to')
        
        return attrs


class PrescriptionStatsSerializer(serializers.Serializer):
    """Serializer for prescription statistics"""
    total_prescriptions = serializers.IntegerField()
    active_prescriptions = serializers.IntegerField()
    completed_prescriptions = serializers.IntegerField()
    digital_prescriptions = serializers.IntegerField()
    total_medications = serializers.IntegerField()
    most_prescribed_medicines = serializers.ListField()
    prescription_trends = serializers.ListField()
    doctor_prescription_stats = serializers.DictField()


class MedicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for medication with prescription info"""
    prescription_id = serializers.CharField(source='prescription.id', read_only=True)
    patient_name = serializers.CharField(source='prescription.patient.name', read_only=True)
    doctor_name = serializers.CharField(source='prescription.doctor.name', read_only=True)
    
    class Meta:
        model = Medication
        fields = [
            'id', 'prescription', 'prescription_id', 'patient_name', 'doctor_name',
            'name', 'generic_name', 'brand_name', 'strength', 'dosage_form',
            'dosage', 'frequency', 'custom_frequency', 'timing', 'duration_days',
            'total_quantity', 'special_instructions', 'side_effects_warning',
            'substitution_allowed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'prescription_id', 'patient_name', 'doctor_name', 'created_at', 'updated_at']



