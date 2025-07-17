from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Consultation(models.Model):
    """Main consultation model"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    CONSULTATION_TYPES = [
        ('video_call', 'Video Call'),
    ]
    
    id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient_consultations'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_consultations'
    )
    
    # Scheduling Information
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPES, default='video_call')
    
    # Consultation Details
    chief_complaint = models.TextField(help_text="Main reason for consultation")
    symptoms = models.TextField(blank=True)
    
    # Status and Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Fees and Payment
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Follow-up
    is_follow_up = models.BooleanField(default=False)
    parent_consultation = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='follow_ups'
    )
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    # Notes and Observations
    doctor_notes = models.TextField(blank=True)
    patient_notes = models.TextField(blank=True)
    prescription_given = models.BooleanField(default=False)
    
    # Cancellation
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cancelled_consultations'
    )
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultations'
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Generate consultation ID
            last_consultation = Consultation.objects.order_by('id').last()
            if last_consultation:
                last_number = int(last_consultation.id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.id = f"CON{new_number:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Consultation {self.id} - {self.patient.name} with Dr. {self.doctor.name}"
    
    @property
    def scheduled_datetime(self):
        """Get scheduled datetime"""
        return timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
    
    @property
    def actual_duration(self):
        """Calculate actual duration in minutes"""
        if self.actual_start_time and self.actual_end_time:
            duration = self.actual_end_time - self.actual_start_time
            return int(duration.total_seconds() / 60)
        return None
    
    @property
    def is_upcoming(self):
        """Check if consultation is upcoming"""
        return self.scheduled_datetime > timezone.now() and self.status == 'scheduled'
    
    @property
    def is_overdue(self):
        """Check if consultation is overdue"""
        return self.scheduled_datetime < timezone.now() and self.status == 'scheduled'


class ConsultationSymptom(models.Model):
    """Symptoms recorded during consultation"""
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='recorded_symptoms'
    )
    symptom = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=[
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], default='mild')
    duration = models.CharField(max_length=100, blank=True, help_text="How long has this symptom persisted")
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_symptoms'
        verbose_name = 'Consultation Symptom'
        verbose_name_plural = 'Consultation Symptoms'
    
    def __str__(self):
        return f"{self.symptom} - {self.consultation.id}"


class ConsultationDiagnosis(models.Model):
    """Diagnoses made during consultation"""
    
    DIAGNOSIS_TYPES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('differential', 'Differential'),
        ('provisional', 'Provisional'),
    ]
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='diagnoses'
    )
    diagnosis = models.CharField(max_length=300)
    diagnosis_type = models.CharField(max_length=20, choices=DIAGNOSIS_TYPES, default='primary')
    icd_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code")
    notes = models.TextField(blank=True)
    confidence_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_diagnoses'
        verbose_name = 'Consultation Diagnosis'
        verbose_name_plural = 'Consultation Diagnoses'
    
    def __str__(self):
        return f"{self.diagnosis} - {self.consultation.id}"


class ConsultationVitalSigns(models.Model):
    """Vital signs recorded during consultation"""
    
    consultation = models.OneToOneField(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='vital_signs'
    )
    
    # Basic vitals
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="BPM")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Celsius")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Per minute")
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True, help_text="Percentage")
    
    # Physical measurements
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kg")
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Additional measurements
    blood_glucose = models.PositiveIntegerField(null=True, blank=True, help_text="mg/dL")
    notes = models.TextField(blank=True)
    
    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'consultation_vital_signs'
        verbose_name = 'Consultation Vital Signs'
        verbose_name_plural = 'Consultation Vital Signs'
    
    def __str__(self):
        return f"Vitals for {self.consultation.id}"
    
    def save(self, *args, **kwargs):
        # Calculate BMI if height and weight are provided
        if self.height and self.weight:
            height_m = self.height / 100  # Convert cm to meters
            self.bmi = self.weight / (height_m * height_m)
        super().save(*args, **kwargs)


class ConsultationAttachment(models.Model):
    """Files and documents attached to consultation"""
    
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('lab_report', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('xray', 'X-Ray'),
        ('scan', 'Scan'),
        ('other', 'Other'),
    ]
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file = models.FileField(upload_to='consultation_attachments/')
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES, default='document')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Uploaded by
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_attachments'
        verbose_name = 'Consultation Attachment'
        verbose_name_plural = 'Consultation Attachments'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.consultation.id}"


class ConsultationNote(models.Model):
    """Additional notes during consultation"""
    
    NOTE_TYPES = [
        ('general', 'General'),
        ('examination', 'Examination'),
        ('treatment', 'Treatment'),
        ('advice', 'Advice'),
        ('follow_up', 'Follow-up'),
    ]
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='notes'
    )
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general')
    content = models.TextField()
    
    # Author
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultation_notes'
        verbose_name = 'Consultation Note'
        verbose_name_plural = 'Consultation Notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.note_type} note for {self.consultation.id}"


class ConsultationReschedule(models.Model):
    """Track consultation reschedule history"""
    
    consultation = models.ForeignKey(
        Consultation, 
        on_delete=models.CASCADE, 
        related_name='reschedule_history'
    )
    old_date = models.DateField()
    old_time = models.TimeField()
    new_date = models.DateField()
    new_time = models.TimeField()
    reason = models.TextField()
    
    # Who requested the reschedule
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'consultation_reschedules'
        verbose_name = 'Consultation Reschedule'
        verbose_name_plural = 'Consultation Reschedules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reschedule for {self.consultation.id} - {self.old_date} to {self.new_date}"

