from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Prescription(models.Model):
    """Main prescription model"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.CharField(max_length=20, primary_key=True, unique=True, editable=False)
    consultation = models.OneToOneField(
        'consultations.Consultation', 
        on_delete=models.CASCADE, 
        related_name='prescription'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='prescribed_prescriptions'
    )
    
    # Prescription Details
    diagnosis = models.TextField()
    symptoms = models.TextField(blank=True)
    general_instructions = models.TextField(blank=True)
    
    # New fields for formatted prescription
    header = models.TextField(blank=True, help_text="Header section for eClinic info", default="Sushrusa eClinic\n123 Health Street, City\nPhone: +91-12345-67890\nEmail: info@sushrusa.com\nReg. No: 123456")
    body = models.TextField(blank=True, help_text="Main prescription body (diagnosis, medicines, etc.)")
    footer = models.TextField(blank=True, help_text="Footer section for eClinic info", default="Thank you for choosing Sushrusa eClinic.\nFor emergencies, call 108.\nThis prescription is valid for 30 days from the date of issue.\n---\nDoctor's digital signature.")
    
    # Validity
    issued_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
    
    # Digital signature and verification
    digital_signature = models.TextField(blank=True, help_text="Digital signature hash")
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=20, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Generate prescription ID
            last_prescription = Prescription.objects.order_by('id').last()
            if last_prescription:
                last_number = int(last_prescription.id[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.id = f"PRE{new_number:03d}"
        
        # Set default valid_until to 30 days from issue date
        if not self.valid_until:
            self.valid_until = timezone.now().date() + timezone.timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Prescription {self.id} - {self.patient.name} by Dr. {self.doctor.name}"
    
    @property
    def is_expired(self):
        """Check if prescription is expired"""
        return timezone.now().date() > self.valid_until
    
    @property
    def days_remaining(self):
        """Get days remaining for prescription validity"""
        if self.is_expired:
            return 0
        return (self.valid_until - timezone.now().date()).days
    
    @property
    def total_medications(self):
        """Get total number of medications in prescription"""
        return self.medications.count()


class Medication(models.Model):
    """Individual medication in a prescription"""
    
    DOSAGE_FORMS = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('patch', 'Patch'),
        ('other', 'Other'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('every_4_hours', 'Every 4 Hours'),
        ('every_6_hours', 'Every 6 Hours'),
        ('every_8_hours', 'Every 8 Hours'),
        ('every_12_hours', 'Every 12 Hours'),
        ('as_needed', 'As Needed'),
        ('before_meals', 'Before Meals'),
        ('after_meals', 'After Meals'),
        ('at_bedtime', 'At Bedtime'),
        ('custom', 'Custom'),
    ]
    
    TIMING_CHOICES = [
        ('before_food', 'Before Food'),
        ('after_food', 'After Food'),
        ('with_food', 'With Food'),
        ('empty_stomach', 'Empty Stomach'),
        ('anytime', 'Anytime'),
    ]
    
    prescription = models.ForeignKey(
        Prescription, 
        on_delete=models.CASCADE, 
        related_name='medications'
    )
    
    # Medication Details
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    strength = models.CharField(max_length=50, help_text="e.g., 500mg, 10ml")
    dosage_form = models.CharField(max_length=20, choices=DOSAGE_FORMS, default='tablet')
    
    # Dosage Instructions
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet, 5ml")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    custom_frequency = models.CharField(max_length=100, blank=True, help_text="For custom frequency")
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES, default='after_food')
    
    # Duration
    duration_days = models.PositiveIntegerField(help_text="Duration in days")
    total_quantity = models.CharField(max_length=50, help_text="Total quantity to be dispensed")
    
    # Special Instructions
    special_instructions = models.TextField(blank=True)
    side_effects_warning = models.TextField(blank=True)
    
    # Substitution
    substitution_allowed = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_medications'
        verbose_name = 'Medication'
        verbose_name_plural = 'Medications'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} - {self.strength} ({self.prescription.id})"
    
    @property
    def display_frequency(self):
        """Get display-friendly frequency"""
        if self.frequency == 'custom':
            return self.custom_frequency
        return self.get_frequency_display()


class MedicationReminder(models.Model):
    """Medication reminders for patients"""
    
    medication = models.ForeignKey(
        Medication, 
        on_delete=models.CASCADE, 
        related_name='reminders'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='medication_reminders'
    )
    
    # Reminder Settings
    reminder_times = models.JSONField(default=list, help_text="List of reminder times")
    is_active = models.BooleanField(default=True)
    
    # Notification Preferences
    sms_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medication_reminders'
        verbose_name = 'Medication Reminder'
        verbose_name_plural = 'Medication Reminders'
        unique_together = ['medication', 'patient']
    
    def __str__(self):
        return f"Reminder for {self.medication.name} - {self.patient.name}"


class MedicationAdherence(models.Model):
    """Track medication adherence"""
    
    ADHERENCE_STATUS = [
        ('taken', 'Taken'),
        ('missed', 'Missed'),
        ('delayed', 'Delayed'),
        ('skipped', 'Skipped'),
    ]
    
    medication = models.ForeignKey(
        Medication, 
        on_delete=models.CASCADE, 
        related_name='adherence_records'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='medication_adherence'
    )
    
    # Adherence Details
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    actual_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ADHERENCE_STATUS)
    notes = models.TextField(blank=True)
    
    # Side effects
    side_effects_experienced = models.BooleanField(default=False)
    side_effects_description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'medication_adherence'
        verbose_name = 'Medication Adherence'
        verbose_name_plural = 'Medication Adherence'
        unique_together = ['medication', 'patient', 'scheduled_date', 'scheduled_time']
        ordering = ['-scheduled_date', '-scheduled_time']
    
    def __str__(self):
        return f"{self.medication.name} - {self.scheduled_date} ({self.status})"


class PrescriptionTemplate(models.Model):
    """Templates for commonly prescribed medications"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='prescription_templates'
    )
    
    # Template Details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=200, help_text="Medical condition this template is for")
    
    # Template Data
    template_data = models.JSONField(help_text="JSON data containing medication details")
    
    # Usage
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_templates'
        verbose_name = 'Prescription Template'
        verbose_name_plural = 'Prescription Templates'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} - Dr. {self.doctor.name}"


class DrugInteraction(models.Model):
    """Drug interaction warnings"""
    
    SEVERITY_LEVELS = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('contraindicated', 'Contraindicated'),
    ]
    
    drug1 = models.CharField(max_length=200)
    drug2 = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    description = models.TextField()
    clinical_effect = models.TextField()
    management = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drug_interactions'
        verbose_name = 'Drug Interaction'
        verbose_name_plural = 'Drug Interactions'
        unique_together = ['drug1', 'drug2']
    
    def __str__(self):
        return f"{self.drug1} + {self.drug2} ({self.severity})"


class PrescriptionNote(models.Model):
    """Additional notes for prescriptions"""
    
    prescription = models.ForeignKey(
        Prescription, 
        on_delete=models.CASCADE, 
        related_name='notes'
    )
    note = models.TextField()
    is_patient_visible = models.BooleanField(default=True)
    
    # Author
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prescription_notes'
        verbose_name = 'Prescription Note'
        verbose_name_plural = 'Prescription Notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.prescription.id}"



class PrescriptionAttachment(models.Model):
    """Attachments for prescriptions"""
    
    ATTACHMENT_TYPES = [
        ("lab_report", "Lab Report"),
        ("imaging_scan", "Imaging Scan"),
        ("other", "Other"),
    ]
    
    prescription = models.ForeignKey(
        Prescription, 
        on_delete=models.CASCADE, 
        related_name="attachments"
    )
    file = models.FileField(upload_to="prescription_attachments/")
    attachment_type = models.CharField(max_length=50, choices=ATTACHMENT_TYPES, default="other")
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="uploaded_prescription_attachments"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "prescription_attachments"
        verbose_name = "Prescription Attachment"
        verbose_name_plural = "Prescription Attachments"
        ordering = ["-uploaded_at"]
    
    def __str__(self):
        return f"Attachment for {self.prescription.id} ({self.attachment_type})"


