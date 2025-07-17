from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class DoctorProfile(models.Model):
    """Extended profile for doctors"""
    
    SPECIALTIES = [
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('endocrinology', 'Endocrinology'),
        ('gastroenterology', 'Gastroenterology'),
        ('general_medicine', 'General Medicine'),
        ('gynecology', 'Gynecology'),
        ('neurology', 'Neurology'),
        ('oncology', 'Oncology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('pulmonology', 'Pulmonology'),
        ('urology', 'Urology'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile'
    )
    
    # Professional Information
    license_number = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=200)
    specialization = models.CharField(max_length=50, choices=SPECIALTIES)
    sub_specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField()
    
    # Consultation Information
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    consultation_duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    
    # Ratings and Reviews
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Clinic Information
    clinic_name = models.CharField(max_length=200, blank=True)
    clinic_address = models.TextField(blank=True)
    
    # Online Consultation
    is_online_consultation_available = models.BooleanField(default=True)
    online_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Languages
    languages_spoken = models.JSONField(default=list, help_text="List of languages spoken")
    
    # Bio and Description
    bio = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_accepting_patients = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_profiles'
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
    
    def __str__(self):
        return f"Dr. {self.user.name} - {self.specialization}"
    
    @property
    def total_consultations(self):
        """Get total number of consultations"""
        return self.user.doctor_consultations.count()
    
    @property
    def completed_consultations(self):
        """Get number of completed consultations"""
        return self.user.doctor_consultations.filter(status='completed').count()


class DoctorSchedule(models.Model):
    """Weekly schedule for doctors"""
    
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='schedules'
    )
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    # Break times
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)
    break_reason = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_schedules'
        verbose_name = 'Doctor Schedule'
        verbose_name_plural = 'Doctor Schedules'
        unique_together = ['doctor', 'day_of_week']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.day_of_week} ({self.start_time}-{self.end_time})"


class DoctorSlot(models.Model):
    """Specific time slots for doctor availability (supports multiple slots per day, calendar/month view)"""
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'doctor_slots'
        verbose_name = 'Doctor Slot'
        verbose_name_plural = 'Doctor Slots'
        unique_together = ['doctor', 'date', 'start_time', 'end_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"{self.doctor.name} - {self.date} {self.start_time}-{self.end_time} ({status})"


class DoctorEducation(models.Model):
    """Education details for doctors"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='education'
    )
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    year_of_completion = models.PositiveIntegerField()
    grade_or_percentage = models.CharField(max_length=20, blank=True)
    
    # Document
    certificate = models.FileField(upload_to='doctor_certificates/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_education'
        verbose_name = 'Doctor Education'
        verbose_name_plural = 'Doctor Education'
        ordering = ['-year_of_completion']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.degree} from {self.institution}"


class DoctorExperience(models.Model):
    """Work experience for doctors"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='experience'
    )
    organization = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_experience'
        verbose_name = 'Doctor Experience'
        verbose_name_plural = 'Doctor Experience'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.doctor.name} - {self.position} at {self.organization}"


class DoctorReview(models.Model):
    """Reviews and ratings for doctors"""
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='given_reviews'
    )
    consultation = models.OneToOneField(
        'consultations.Consultation', 
        on_delete=models.CASCADE, 
        related_name='review',
        null=True, 
        blank=True
    )
    
    # Rating and Review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)
    
    # Specific ratings
    communication_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    treatment_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    punctuality_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    # Status
    is_approved = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_reviews'
        verbose_name = 'Doctor Review'
        verbose_name_plural = 'Doctor Reviews'
        unique_together = ['doctor', 'patient', 'consultation']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for Dr. {self.doctor.name} by {self.patient.name} - {self.rating}/5"


class DoctorDocument(models.Model):
    """Documents for doctor verification"""
    
    DOCUMENT_TYPES = [
        ('license', 'Medical License'),
        ('degree_certificate', 'Degree Certificate'),
        ('experience_certificate', 'Experience Certificate'),
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('other', 'Other'),
    ]
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_documents'
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='doctor_documents/')
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_doctor_documents'
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_documents'
        verbose_name = 'Doctor Document'
        verbose_name_plural = 'Doctor Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - Dr. {self.doctor.name}"

