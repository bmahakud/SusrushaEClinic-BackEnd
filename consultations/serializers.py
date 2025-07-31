from rest_framework import serializers
from authentication.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile
from .models import (
    Consultation, ConsultationSymptom, ConsultationDiagnosis,
    ConsultationVitalSigns, ConsultationAttachment, ConsultationNote,
    ConsultationReschedule
)

class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer for consultation"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_meeting_link = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'patient', 'doctor', 'patient_name', 'doctor_name',
            'consultation_type', 'scheduled_date', 'scheduled_time', 'duration',
            'status', 'doctor_notes', 'patient_notes', 'payment_status', 
            'consultation_fee', 'is_paid', 'created_at', 'updated_at',
            'doctor_meeting_link', 'booked_slot',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_doctor_meeting_link(self, obj):
        if hasattr(obj, 'doctor') and hasattr(obj.doctor, 'doctor_profile') and hasattr(obj.doctor.doctor_profile, 'meeting_link'):
            return obj.doctor.doctor_profile.meeting_link
        return None


class ConsultationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultation"""
    slot_id = serializers.IntegerField(write_only=True, help_text="ID of the doctor slot to book")
    
    class Meta:
        model = Consultation
        fields = [
            'patient', 'doctor', 'consultation_type', 'scheduled_date',
            'scheduled_time', 'duration', 'chief_complaint', 'symptoms',
            'consultation_fee', 'slot_id'
        ]
    
    def create(self, validated_data):
        """Create consultation and book the slot"""
        slot_id = validated_data.pop('slot_id')
        
        # Get the slot and validate it's available
        from doctors.models import DoctorSlot
        try:
            slot = DoctorSlot.objects.get(id=slot_id)
        except DoctorSlot.DoesNotExist:
            raise serializers.ValidationError("Invalid slot ID")
        
        if not slot.is_available or slot.is_booked:
            raise serializers.ValidationError("This slot is not available for booking")
        
        # Set consultation data from slot
        validated_data['scheduled_date'] = slot.date
        validated_data['scheduled_time'] = slot.start_time
        validated_data['duration'] = slot.clinic.consultation_duration
        validated_data['clinic'] = slot.clinic
        validated_data['status'] = 'scheduled'
        validated_data['payment_status'] = 'pending'
        
        # Create the consultation
        consultation = super().create(validated_data)
        
        # Book the slot
        slot.is_booked = True
        slot.booked_consultation = consultation
        slot.save()
        
        return consultation

    def validate(self, data):
        slot_id = data.get('slot_id')
        if not slot_id:
            raise serializers.ValidationError("Slot ID is required")
        
        # Validate slot exists and is available
        from doctors.models import DoctorSlot
        try:
            slot = DoctorSlot.objects.get(id=slot_id)
        except DoctorSlot.DoesNotExist:
            raise serializers.ValidationError("Invalid slot ID")
        
        if not slot.is_available or slot.is_booked:
            raise serializers.ValidationError("This slot is not available for booking")
        
        # Validate doctor matches slot
        if data.get('doctor') and data['doctor'] != slot.doctor:
            raise serializers.ValidationError("Doctor does not match the selected slot")
        
        return data


class ConsultationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating consultation"""
    
    class Meta:
        model = Consultation
        fields = [
            'consultation_type', 'scheduled_date', 'scheduled_time', 'duration',
            'status', 'doctor_notes', 'patient_notes', 'payment_status'
        ]


class ConsultationSymptomSerializer(serializers.ModelSerializer):
    """Serializer for consultation symptom"""
    
    class Meta:
        model = ConsultationSymptom
        fields = ['id', 'consultation', 'symptom', 'severity', 'notes']
        read_only_fields = ['id']


class ConsultationSymptomCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultation symptom"""
    
    class Meta:
        model = ConsultationSymptom
        fields = ['symptom', 'severity', 'notes']
    
    def create(self, validated_data):
        """Create symptom for consultation"""
        consultation_id = self.context['view'].kwargs.get('consultation_id')
        validated_data['consultation_id'] = consultation_id
        return super().create(validated_data)


class ConsultationDiagnosisSerializer(serializers.ModelSerializer):
    """Serializer for consultation diagnosis"""
    
    class Meta:
        model = ConsultationDiagnosis
        fields = ['id', 'consultation', 'diagnosis', 'notes']
        read_only_fields = ['id']


class ConsultationDiagnosisCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultation diagnosis"""
    
    class Meta:
        model = ConsultationDiagnosis
        fields = ['diagnosis', 'notes']
    
    def create(self, validated_data):
        """Create diagnosis for consultation"""
        consultation_id = self.context['view'].kwargs.get('consultation_id')
        validated_data['consultation_id'] = consultation_id
        return super().create(validated_data)


class ConsultationVitalSignsSerializer(serializers.ModelSerializer):
    """Serializer for vital signs"""
    
    class Meta:
        model = ConsultationVitalSigns
        fields = [
            'id', 'consultation', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
            'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'height', 'bmi', 'blood_glucose', 'notes', 'recorded_at'
        ]
        read_only_fields = ['id', 'recorded_at']


class ConsultationVitalSignsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vital signs"""
    
    class Meta:
        model = ConsultationVitalSigns
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 'temperature',
            'respiratory_rate', 'oxygen_saturation', 'weight', 'height', 'bmi', 'blood_glucose', 'notes'
        ]
    
    def create(self, validated_data):
        """Create vital signs for consultation"""
        consultation_id = self.context['view'].kwargs.get('consultation_id')
        validated_data['consultation_id'] = consultation_id
        return super().create(validated_data)


class ConsultationAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for consultation attachments"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    
    class Meta:
        model = ConsultationAttachment
        fields = [
            'id', 'consultation', 'attachment_type', 'title', 'description',
            'file', 'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


class ConsultationAttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultation attachments"""
    
    class Meta:
        model = ConsultationAttachment
        fields = ['attachment_type', 'title', 'description', 'file']
    
    def create(self, validated_data):
        """Create attachment for consultation"""
        consultation_id = self.context['view'].kwargs.get('consultation_id')
        uploaded_by = self.context['request'].user
        
        validated_data['consultation_id'] = consultation_id
        validated_data['uploaded_by'] = uploaded_by
        return super().create(validated_data)


class ConsultationNoteSerializer(serializers.ModelSerializer):
    """Serializer for consultation notes"""
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    
    class Meta:
        model = ConsultationNote
        fields = [
            'id', 'consultation', 'note_type', 'content',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ConsultationNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultation notes"""
    
    class Meta:
        model = ConsultationNote
        fields = ['note_type', 'content']
    
    def create(self, validated_data):
        """Create note for consultation"""
        consultation_id = self.context['view'].kwargs.get('consultation_id')
        created_by = self.context['request'].user
        
        validated_data['consultation_id'] = consultation_id
        validated_data['created_by'] = created_by
        return super().create(validated_data)


class ConsultationRescheduleSerializer(serializers.ModelSerializer):
    """Serializer for consultation reschedule"""
    
    class Meta:
        model = ConsultationReschedule
        fields = [
            'id', 'consultation', 'old_date', 'old_time',
            'new_date', 'new_time', 'reason', 'requested_by', 'created_at'
        ]
        read_only_fields = ['id', 'requested_by', 'created_at']


class ConsultationRescheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating consultation reschedule"""
    
    class Meta:
        model = ConsultationReschedule
        fields = [
            'new_consultation_date', 'new_start_time',
            'new_end_time', 'reason'
        ]
    
    def create(self, validated_data):
        """Create reschedule for consultation"""
        consultation_id = self.context['view'].kwargs.get('consultation_id')
        rescheduled_by = self.context['request'].user
        
        validated_data['consultation_id'] = consultation_id
        validated_data['rescheduled_by'] = rescheduled_by
        return super().create(validated_data)


class ConsultationListSerializer(serializers.ModelSerializer):
    """Serializer for consultation list view"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_meeting_link = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'patient', 'doctor', 'patient_name', 'doctor_name',
            'consultation_type', 'scheduled_date', 'scheduled_time', 'duration',
            'status', 'payment_status', 'consultation_fee', 'is_paid', 'created_at',
            'doctor_meeting_link',
        ]
        read_only_fields = ['id', 'created_at']

    def get_doctor_meeting_link(self, obj):
        if hasattr(obj, 'doctor') and hasattr(obj.doctor, 'doctor_profile') and hasattr(obj.doctor.doctor_profile, 'meeting_link'):
            return obj.doctor.doctor_profile.meeting_link
        return None


class ConsultationSearchSerializer(serializers.Serializer):
    """Serializer for consultation search"""
    query = serializers.CharField(max_length=200, required=False)
    patient_id = serializers.IntegerField(required=False)
    doctor_id = serializers.IntegerField(required=False)
    consultation_type = serializers.ChoiceField(
        choices=Consultation._meta.get_field('consultation_type').choices,
        required=False
    )
    status = serializers.ChoiceField(
        choices=Consultation._meta.get_field('status').choices,
        required=False
    )
    payment_status = serializers.ChoiceField(
        choices=Consultation._meta.get_field('payment_status').choices,
        required=False
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    
    def validate(self, attrs):
        """Validate search parameters"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError('date_from cannot be greater than date_to')
        
        return attrs


class ConsultationStatsSerializer(serializers.Serializer):
    """Serializer for consultation statistics"""
    total_consultations = serializers.IntegerField()
    scheduled_consultations = serializers.IntegerField()
    completed_consultations = serializers.IntegerField()
    cancelled_consultations = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    consultation_trends = serializers.ListField()
    doctor_consultation_stats = serializers.DictField()


class ConsultationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for consultation with related data"""
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_meeting_link = serializers.SerializerMethodField(read_only=True)
    recorded_symptoms = ConsultationSymptomSerializer(many=True, read_only=True)
    diagnoses = ConsultationDiagnosisSerializer(many=True, read_only=True)
    vital_signs = ConsultationVitalSignsSerializer(many=True, read_only=True)
    attachments = ConsultationAttachmentSerializer(many=True, read_only=True)
    notes = ConsultationNoteSerializer(many=True, read_only=True)
    reschedules = ConsultationRescheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'patient', 'doctor', 'patient_name', 'doctor_name',
            'consultation_type', 'scheduled_date', 'scheduled_time', 'duration',
            'chief_complaint', 'symptoms', 'status',
            'actual_start_time', 'actual_end_time', 'consultation_fee',
            'is_paid', 'payment_method', 'payment_status', 'is_follow_up',
            'parent_consultation', 'follow_up_required', 'follow_up_date',
            'doctor_notes', 'patient_notes', 'prescription_given',
            'cancelled_by', 'cancellation_reason', 'cancelled_at',
            'recorded_symptoms', 'diagnoses', 'vital_signs', 'attachments', 'notes', 'reschedules',
            'created_at', 'updated_at',
            'doctor_meeting_link',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_doctor_meeting_link(self, obj):
        if hasattr(obj, 'doctor') and hasattr(obj.doctor, 'doctor_profile') and hasattr(obj.doctor.doctor_profile, 'meeting_link'):
            return obj.doctor.doctor_profile.meeting_link
        return None



