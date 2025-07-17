from django.db import models
from django.conf import settings

class Prescription(models.Model):
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
    issued_date = models.DateField(auto_now_add=True)
    header = models.FileField(upload_to='prescription_headers/', blank=True, null=True)
    footer = models.FileField(upload_to='prescription_footers/', blank=True, null=True)  # Footer as file
    text = models.TextField(blank=True)    # Free text for doctor notes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor} on {self.issued_date}"


