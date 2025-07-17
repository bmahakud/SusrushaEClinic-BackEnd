from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Prescription
from .serializers import PrescriptionSerializer
from django.db import models

class IsDoctorOrPatientOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_superuser or request.user.is_staff:
            return True
        # Doctor can edit/view, patient can view
        if request.user == obj.doctor:
            return True
        if request.method in permissions.SAFE_METHODS and request.user == obj.patient:
            return True
        return False

class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrPatientOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # Admin sees all, doctor sees their prescriptions, patient sees their own
        if user.is_superuser or user.is_staff:
            return Prescription.objects.all()
        return Prescription.objects.filter(
            models.Q(doctor=user) | models.Q(patient=user)
        )

    def perform_create(self, serializer):
        user = self.request.user
        # Admin can set doctor, otherwise doctor is request.user
        if user.is_superuser or user.is_staff:
            serializer.save()
        else:
            serializer.save(doctor=user)

    @action(detail=False, methods=['get'], url_path='patient/(?P<patient_id>[^/.]+)')
    def by_patient(self, request, patient_id=None):
        # List all prescriptions for a given patient (for patient profile)
        prescriptions = Prescription.objects.filter(patient_id=patient_id)
        serializer = self.get_serializer(prescriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch', 'put'], url_path='admin-update-header-footer', permission_classes=[permissions.IsAdminUser])
    def admin_update_header_footer(self, request, pk=None):
        # Admin can update header/footer for any prescription
        prescription = self.get_object()
        serializer = self.get_serializer(prescription, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

