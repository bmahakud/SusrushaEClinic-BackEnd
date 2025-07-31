from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from consultations.models import Consultation

class Prescription(models.Model):
    """Enhanced prescription model matching the comprehensive prescription structure"""
    
    # Basic Information
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        null=True,
        blank=True
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_as_doctor'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_as_patient'
    )
    
    # Prescription Details
    issued_date = models.DateField(auto_now_add=True)
    issued_time = models.TimeField(auto_now_add=True)
    
    # Patient Vitals (from consultation)
    pulse = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in bpm")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic BP")
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic BP")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in Celsius")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    
    # Diagnosis
    primary_diagnosis = models.TextField(blank=True, help_text="Primary diagnosis")
    secondary_diagnosis = models.TextField(blank=True, help_text="Secondary diagnosis")
    clinical_classification = models.TextField(blank=True, help_text="Clinical classification (e.g., NYHA Class)")
    
    # General Instructions
    general_instructions = models.TextField(blank=True, help_text="General medication instructions")
    fluid_intake = models.CharField(max_length=100, blank=True, help_text="Fluid intake instructions")
    diet_instructions = models.TextField(blank=True, help_text="Diet instructions")
    lifestyle_advice = models.TextField(blank=True, help_text="Lifestyle advice")
    
    # Follow-up
    next_visit = models.CharField(max_length=100, blank=True, help_text="Next visit instructions")
    follow_up_notes = models.TextField(blank=True, help_text="Follow-up notes")
    
    # Prescription Status
    is_draft = models.BooleanField(default=True, help_text="Whether prescription is in draft mode")
    is_finalized = models.BooleanField(default=False, help_text="Whether prescription is finalized")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']
        unique_together = ['consultation', 'doctor', 'patient']

    def __str__(self):
        return f"Prescription for {self.patient.name} by {self.doctor.name} on {self.issued_date}"

class PrescriptionMedication(models.Model):
    """Individual medications in a prescription"""
    
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('four_times_daily', 'Four Times Daily'),
        ('sos', 'SOS (As Needed)'),
        ('custom', 'Custom'),
    ]
    
    TIMING_CHOICES = [
        ('before_breakfast', 'Before Breakfast'),
        ('after_breakfast', 'After Breakfast'),
        ('before_lunch', 'Before Lunch'),
        ('after_lunch', 'After Lunch'),
        ('before_dinner', 'Before Dinner'),
        ('after_dinner', 'After Dinner'),
        ('bedtime', 'Bedtime'),
        ('empty_stomach', 'Empty Stomach'),
        ('with_food', 'With Food'),
        ('custom', 'Custom'),
    ]
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    
    # Medication Details
    medicine_name = models.CharField(max_length=200, help_text="Name of the medicine")
    composition = models.CharField(max_length=500, blank=True, help_text="Composition/ingredients")
    dosage_form = models.CharField(max_length=100, blank=True, help_text="Tablet, Syrup, Injection, etc.")
    
    # Dosage (Morning-Afternoon-Night format like 1-0-1)
    morning_dose = models.PositiveIntegerField(default=0, help_text="Morning dose")
    afternoon_dose = models.PositiveIntegerField(default=0, help_text="Afternoon dose")
    evening_dose = models.PositiveIntegerField(default=0, help_text="Evening dose")
    
    # Timing and Frequency
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once_daily')
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES, default='after_breakfast')
    custom_timing = models.CharField(max_length=200, blank=True, help_text="Custom timing instructions")
    
    # Duration
    duration_days = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in days")
    duration_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in weeks")
    duration_months = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in months")
    is_continuous = models.BooleanField(default=False, help_text="Continue indefinitely")
    
    # Special Instructions
    special_instructions = models.TextField(blank=True, help_text="Special instructions for this medication")
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    # Order
    order = models.PositiveIntegerField(default=0, help_text="Order of medication in prescription")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_medications'
        verbose_name = 'Prescription Medication'
        verbose_name_plural = 'Prescription Medications'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.medicine_name} - {self.prescription}"

class PrescriptionVitalSigns(models.Model):
    """Vital signs recorded during prescription"""
    
    prescription = models.OneToOneField(
        Prescription,
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    
    # Vital Signs
    pulse = models.PositiveIntegerField(null=True, blank=True, help_text="Pulse rate in bpm")
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text="Systolic BP")
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text="Diastolic BP")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Temperature in Celsius")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Respiratory rate per minute")
    oxygen_saturation = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Oxygen saturation percentage"
    )
    
    # Additional Vitals
    blood_sugar_fasting = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fasting blood sugar")
    blood_sugar_postprandial = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Postprandial blood sugar")
    hba1c = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="HbA1c percentage")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Additional notes about vital signs")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prescription_vital_signs'
        verbose_name = 'Prescription Vital Signs'
        verbose_name_plural = 'Prescription Vital Signs'

    def __str__(self):
        return f"Vital Signs for {self.prescription}"


