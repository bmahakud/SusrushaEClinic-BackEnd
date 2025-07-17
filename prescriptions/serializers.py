from rest_framework import serializers
from .models import Prescription

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            'id', 'doctor', 'patient', 'issued_date', 'header', 'footer', 'text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'issued_date', 'created_at', 'updated_at']



