from django.contrib import admin
from .models import (
    DoctorProfile, DoctorSchedule,
    DoctorEducation, DoctorExperience, DoctorReview, DoctorDocument, DoctorSlot
)


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'license_number', 'specialization', 'experience_years',
        'consultation_fee', 'is_verified', 'is_active', 'is_accepting_patients'
    ]
    list_filter = [
        'specialization', 'is_verified', 'is_active', 'is_accepting_patients'
    ]
    search_fields = [
        'user__name', 'user__phone_number', 'license_number', 'specialization'
    ]
    readonly_fields = [
        'rating', 'total_reviews', 'created_at', 'updated_at'
    ]
    fieldsets = (
        (None, {
            'fields': ('user', 'license_number', 'qualification', 'specialization', 'sub_specialization')
        }),
        ('Experience & Fees', {
            'fields': ('experience_years', 'consultation_fee', 'consultation_duration')
        }),
        ('Clinic Information', {
            'fields': ('clinic_name', 'clinic_address')
        }),
        ('Online Consultation', {
            'fields': ('is_online_consultation_available', 'online_consultation_fee')
        }),
        ('Bio & Languages', {
            'fields': ('bio', 'achievements', 'languages_spoken')
        }),
        ('Status & Verification', {
            'fields': ('is_verified', 'is_active', 'is_accepting_patients')
        }),
        ('Ratings & Reviews', {
            'fields': ('rating', 'total_reviews')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'doctor', 'day_of_week', 'start_time', 'end_time', 'is_available'
    ]
    list_filter = [
        'day_of_week', 'is_available'
    ]
    search_fields = [
        'doctor__user__name', 'day_of_week'
    ]
    ordering = [
        'doctor__user__name', 'day_of_week', 'start_time'
    ]
    readonly_fields = [
        'created_at', 'updated_at'
    ]


@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = [
        'doctor', 'degree', 'institution', 'year_of_completion', 'is_verified'
    ]
    list_filter = [
        'is_verified', 'year_of_completion'
    ]
    search_fields = [
        'doctor__user__name', 'degree', 'institution'
    ]
    ordering = [
        'doctor__user__name', '-year_of_completion'
    ]
    readonly_fields = [
        'created_at', 'updated_at'
    ]


@admin.register(DoctorExperience)
class DoctorExperienceAdmin(admin.ModelAdmin):
    list_display = [
        'doctor', 'organization', 'position', 'start_date', 'end_date', 'is_current'
    ]
    list_filter = [
        'is_current', 'organization'
    ]
    search_fields = [
        'doctor__user__name', 'organization', 'position'
    ]
    ordering = [
        'doctor__user__name', '-start_date'
    ]
    readonly_fields = [
        'created_at', 'updated_at'
    ]


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = [
        'doctor', 'patient', 'rating', 'review_text', 'is_approved', 'is_anonymous'
    ]
    list_filter = [
        'is_approved', 'is_anonymous', 'rating'
    ]
    search_fields = [
        'doctor__user__name', 'patient__user__name', 'review_text'
    ]
    ordering = [
        'doctor__user__name', '-created_at'
    ]
    readonly_fields = [
        'created_at', 'updated_at'
    ]


@admin.register(DoctorDocument)
class DoctorDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'doctor', 'document_type', 'title', 'is_verified', 'uploaded_at'
    ]
    list_filter = [
        'document_type', 'is_verified'
    ]
    search_fields = [
        'doctor__user__name', 'title', 'description'
    ]
    ordering = [
        'doctor__user__name', '-uploaded_at'
    ]
    readonly_fields = [
        'uploaded_at', 'updated_at'
    ]


admin.site.register(DoctorSlot)


