import os
import hashlib
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from PIL import Image as PILImage
from datetime import datetime
import math


class ProfessionalPrescriptionPDFGenerator:
    """Generate professional prescription PDFs with modern design"""
    
    def __init__(self, prescription, header_image_path=None, footer_image_path=None):
        self.prescription = prescription
        self.header_image_path = header_image_path
        self.footer_image_path = footer_image_path
        self.buffer = BytesIO()
        self.page_width, self.page_height = A4
        
        # Color scheme
        self.primary_color = colors.HexColor('#2E86AB')  # Professional blue
        self.secondary_color = colors.HexColor('#A23B72')  # Purple accent
        self.accent_color = colors.HexColor('#F18F01')  # Orange accent
        self.light_gray = colors.HexColor('#F8F9FA')
        self.dark_gray = colors.HexColor('#495057')
        self.success_green = colors.HexColor('#28A745')
        self.warning_orange = colors.HexColor('#FFC107')
        
    def _add_header(self, canvas_obj, doc):
        """Add professional header to the PDF"""
        canvas_obj.saveState()
        
        # Header background with gradient effect
        header_height = 140
        
        # Main header background
        canvas_obj.setFillColor(self.primary_color)
        canvas_obj.rect(0, self.page_height - header_height, self.page_width, header_height, fill=True, stroke=False)
        
        # Logo area (left side)
        logo_width = 120
        logo_height = 80
        logo_x = 50
        logo_y = self.page_height - 110
        
        # Draw logo placeholder or actual logo
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(logo_x, logo_y + 30, "SUSHRUSA")
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(logo_x, logo_y + 15, "eClinic")
        
        # Clinic information (center)
        clinic_x = logo_x + logo_width + 50
        clinic_y = self.page_height - 80
        
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont("Helvetica-Bold", 18)
        canvas_obj.drawString(clinic_x, clinic_y + 20, "SUSHRUSA eCLINIC")
        
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.drawString(clinic_x, clinic_y, "🏥 Professional Healthcare Services")
        canvas_obj.drawString(clinic_x, clinic_y - 15, "📞 +91-12345-67890 | 📧 info@sushrusa.com")
        canvas_obj.drawString(clinic_x, clinic_y - 30, "📍 123 Health Street, Medical District, City - 123456")
        canvas_obj.drawString(clinic_x, clinic_y - 45, "🆔 Reg. No: MH/MED/2024/123456 | GST: 27ABCDE1234F1Z5")
        
        # Prescription label (right side)
        label_x = self.page_width - 200
        label_y = self.page_height - 80
        
        # Prescription label background
        canvas_obj.setFillColor(self.secondary_color)
        canvas_obj.roundRect(label_x, label_y - 20, 150, 60, radius=10, fill=True, stroke=False)
        
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(label_x + 10, label_y + 15, "PRESCRIPTION")
        
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(label_x + 10, label_y, f"Date: {self.prescription.issued_date.strftime('%d/%m/%Y')}")
        canvas_obj.drawString(label_x + 10, label_y - 15, f"Time: {self.prescription.issued_time.strftime('%H:%M')}")
        
        # Add decorative line
        canvas_obj.setStrokeColor(colors.white)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(50, self.page_height - header_height + 10, self.page_width - 50, self.page_height - header_height + 10)
        
        canvas_obj.restoreState()
    
    def _add_footer(self, canvas_obj, doc):
        """Add professional footer to the PDF"""
        canvas_obj.saveState()
        
        footer_height = 100
        footer_y = 0
        
        # Footer background
        canvas_obj.setFillColor(self.light_gray)
        canvas_obj.rect(0, footer_y, self.page_width, footer_height, fill=True, stroke=False)
        
        # Footer content
        canvas_obj.setFillColor(self.dark_gray)
        canvas_obj.setFont("Helvetica", 9)
        
        # Left side - Emergency info
        canvas_obj.drawString(50, footer_y + 70, "🚨 EMERGENCY CONTACT")
        canvas_obj.drawString(50, footer_y + 55, "📞 108 (Ambulance) | 🏥 Emergency: +91-98765-43210")
        
        # Center - Validity info
        center_x = self.page_width / 2
        canvas_obj.drawString(center_x - 100, footer_y + 70, "📋 PRESCRIPTION VALIDITY")
        canvas_obj.drawString(center_x - 100, footer_y + 55, "⏰ Valid for 30 days from date of issue")
        canvas_obj.drawString(center_x - 100, footer_y + 40, "🔄 Refill available with doctor's approval")
        
        # Right side - Digital signature
        canvas_obj.drawString(self.page_width - 200, footer_y + 70, "👨‍⚕️ DIGITAL SIGNATURE")
        canvas_obj.drawString(self.page_width - 200, footer_y + 55, f"Dr. {self.prescription.doctor.name}")
        canvas_obj.drawString(self.page_width - 200, footer_y + 40, f"Reg. No: {getattr(self.prescription.doctor, 'registration_number', 'N/A')}")
        
        # Bottom line
        canvas_obj.setStrokeColor(self.primary_color)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(50, footer_y + 25, self.page_width - 50, footer_y + 25)
        
        # Copyright
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(center_x - 80, footer_y + 10, "© 2024 Sushrusa eClinic. All rights reserved.")
        
        canvas_obj.restoreState()
    
    def _create_info_section(self, title, data, styles):
        """Create a formatted information section"""
        content = []
        
        # Section title
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            textColor=self.primary_color,
            fontName='Helvetica-Bold'
        )
        content.append(Paragraph(title, title_style))
        
        # Create table for data
        if data:
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), self.light_gray),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
            ]))
            content.append(table)
        
        content.append(Spacer(1, 15))
        return content
    
    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return "N/A"
        
        today = datetime.now().date()
        age = today.year - date_of_birth.year
        if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
            age -= 1
        return f"{age} years"
    
    def generate_pdf(self):
        """Generate the complete professional prescription PDF"""
        # Create the PDF document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=160,  # Space for header
            bottomMargin=120  # Space for footer
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'PrescriptionTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=25,
            alignment=TA_CENTER,
            textColor=self.primary_color,
            fontName='Helvetica-Bold'
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=self.secondary_color,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        )
        
        # Build content
        content = []
        
        # Main title
        content.append(Paragraph("MEDICAL PRESCRIPTION", title_style))
        content.append(Spacer(1, 20))
        
        # Patient and Doctor Information
        patient_data = [
            ['Patient Name:', self.prescription.patient.name or 'N/A'],
            ['Patient ID:', f'PAT{str(self.prescription.patient.id).zfill(6)}'],
            ['Age/Gender:', f"{self._calculate_age(getattr(self.prescription.patient, 'date_of_birth', None))} / {getattr(self.prescription.patient, 'gender', 'N/A')}"],
            ['Phone:', getattr(self.prescription.patient, 'phone', 'N/A')],
            ['Email:', getattr(self.prescription.patient, 'email', 'N/A')],
        ]
        
        doctor_data = [
            ['Doctor Name:', self.prescription.doctor.name or 'N/A'],
            ['Doctor ID:', f'DOC{str(self.prescription.doctor.id).zfill(6)}'],
            ['Specialization:', getattr(self.prescription.doctor, 'specialization', 'General Medicine')],
            ['Registration No:', getattr(self.prescription.doctor, 'registration_number', 'N/A')],
            ['Phone:', getattr(self.prescription.doctor, 'phone', 'N/A')],
        ]
        
        # Create patient-doctor table
        patient_doctor_data = []
        for i in range(max(len(patient_data), len(doctor_data))):
            row = []
            if i < len(patient_data):
                row.extend(patient_data[i])
            else:
                row.extend(['', ''])
            if i < len(doctor_data):
                row.extend(doctor_data[i])
            else:
                row.extend(['', ''])
            patient_doctor_data.append(row)
        
        # Add headers
        patient_doctor_data.insert(0, ['PATIENT INFORMATION', '', 'DOCTOR INFORMATION', ''])
        
        patient_doctor_table = Table(patient_doctor_data, colWidths=[2*inch, 2.5*inch, 2*inch, 2.5*inch])
        patient_doctor_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, self.primary_color),
            ('BACKGROUND', (0, 0), (1, 0), self.primary_color),
            ('BACKGROUND', (2, 0), (3, 0), self.primary_color),
            ('BACKGROUND', (0, 1), (0, -1), self.light_gray),
            ('BACKGROUND', (2, 1), (2, -1), self.light_gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
        ]))
        content.append(patient_doctor_table)
        content.append(Spacer(1, 20))
        
        # Consultation Information
        if self.prescription.consultation:
            consultation_data = [
                ['Consultation ID:', f'CON{str(self.prescription.consultation.id).zfill(6)}'],
                ['Consultation Date:', self.prescription.consultation.scheduled_date.strftime('%d/%m/%Y')],
                ['Consultation Time:', self.prescription.consultation.scheduled_time.strftime('%H:%M')],
                ['Consultation Type:', getattr(self.prescription.consultation, 'consultation_type', 'General')],
                ['Chief Complaint:', getattr(self.prescription.consultation, 'chief_complaint', 'N/A')],
            ]
            content.extend(self._create_info_section("CONSULTATION DETAILS", consultation_data, styles))
        
        # Vital Signs
        if hasattr(self.prescription, 'vital_signs') and self.prescription.vital_signs:
            vital_signs = self.prescription.vital_signs
            vital_data = []
            
            if vital_signs.pulse:
                vital_data.append(['Pulse Rate:', f"{vital_signs.pulse} bpm"])
            if vital_signs.blood_pressure_systolic and vital_signs.blood_pressure_diastolic:
                vital_data.append(['Blood Pressure:', f"{vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic} mmHg"])
            if vital_signs.temperature:
                vital_data.append(['Temperature:', f"{vital_signs.temperature}°C"])
            if vital_signs.weight:
                vital_data.append(['Weight:', f"{vital_signs.weight} kg"])
            if vital_signs.height:
                vital_data.append(['Height:', f"{vital_signs.height} cm"])
            if vital_signs.respiratory_rate:
                vital_data.append(['Respiratory Rate:', f"{vital_signs.respiratory_rate} /min"])
            if vital_signs.oxygen_saturation:
                vital_data.append(['Oxygen Saturation:', f"{vital_signs.oxygen_saturation}%"])
            if vital_signs.blood_sugar_fasting:
                vital_data.append(['Fasting Blood Sugar:', f"{vital_signs.blood_sugar_fasting} mg/dL"])
            if vital_signs.blood_sugar_postprandial:
                vital_data.append(['Postprandial Blood Sugar:', f"{vital_signs.blood_sugar_postprandial} mg/dL"])
            if vital_signs.hba1c:
                vital_data.append(['HbA1c:', f"{vital_signs.hba1c}%"])
            
            if vital_data:
                content.extend(self._create_info_section("VITAL SIGNS", vital_data, styles))
        
        # Diagnosis
        if self.prescription.primary_diagnosis or self.prescription.patient_previous_history:
            content.append(Paragraph("DIAGNOSIS", section_style))
            
            diagnosis_text = ""
            if self.prescription.primary_diagnosis:
                diagnosis_text += f"<b>Primary:</b> {self.prescription.primary_diagnosis}"
            if self.prescription.patient_previous_history:
                if diagnosis_text:
                    diagnosis_text += "<br/>"
                diagnosis_text += f"<b>Patient History:</b> {self.prescription.patient_previous_history}"
            if self.prescription.clinical_classification:
                if diagnosis_text:
                    diagnosis_text += "<br/>"
                diagnosis_text += f"<b>Clinical Classification:</b> {self.prescription.clinical_classification}"
            
            content.append(Paragraph(diagnosis_text, normal_style))
            content.append(Spacer(1, 15))
        
        # Medications
        if self.prescription.medications.exists():
            content.append(Paragraph("PRESCRIBED MEDICATIONS", section_style))
            
            med_headers = ['S.No.', 'Medicine Name', 'Composition', 'Dosage (M-A-N)', 'Frequency', 'Duration', 'Special Instructions']
            med_data = [med_headers]
            
            for idx, medication in enumerate(self.prescription.medications.all().order_by('order'), 1):
                dosage = f"{medication.morning_dose}-{medication.afternoon_dose}-{medication.evening_dose}"
                
                duration = ""
                if medication.duration_days:
                    duration = f"{medication.duration_days} days"
                elif medication.duration_weeks:
                    duration = f"{medication.duration_weeks} weeks"
                elif medication.duration_months:
                    duration = f"{medication.duration_months} months"
                elif medication.is_continuous:
                    duration = "Continue as advised"
                
                instructions = medication.special_instructions or medication.get_timing_display()
                if medication.custom_timing:
                    instructions += f" ({medication.custom_timing})"
                
                med_data.append([
                    str(idx),
                    medication.medicine_name,
                    medication.composition or 'N/A',
                    dosage,
                    medication.get_frequency_display(),
                    duration,
                    instructions
                ])
            
            med_table = Table(med_data, colWidths=[0.5*inch, 1.8*inch, 1.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
            med_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.primary_color),
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # S.No. center aligned
            ]))
            content.append(med_table)
            content.append(Spacer(1, 15))
        
        # Instructions Section
        instructions_content = []
        
        if self.prescription.general_instructions:
            instructions_content.append(f"<b>General Instructions:</b> {self.prescription.general_instructions}")
        
        if self.prescription.fluid_intake:
            instructions_content.append(f"<b>Fluid Intake:</b> {self.prescription.fluid_intake}")
        
        if self.prescription.diet_instructions:
            instructions_content.append(f"<b>Diet Instructions:</b> {self.prescription.diet_instructions}")
        
        if self.prescription.lifestyle_advice:
            instructions_content.append(f"<b>Lifestyle Advice:</b> {self.prescription.lifestyle_advice}")
        
        if instructions_content:
            content.append(Paragraph("PATIENT INSTRUCTIONS", section_style))
            for instruction in instructions_content:
                content.append(Paragraph(instruction, normal_style))
            content.append(Spacer(1, 15))
        
        # Follow-up
        if self.prescription.next_visit or self.prescription.follow_up_notes:
            content.append(Paragraph("FOLLOW-UP PLAN", section_style))
            
            follow_up_text = ""
            if self.prescription.next_visit:
                follow_up_text += f"<b>Next Visit:</b> {self.prescription.next_visit}"
            if self.prescription.follow_up_notes:
                if follow_up_text:
                    follow_up_text += "<br/>"
                follow_up_text += f"<b>Follow-up Notes:</b> {self.prescription.follow_up_notes}"
            
            content.append(Paragraph(follow_up_text, normal_style))
            content.append(Spacer(1, 15))
        
        # Prescription Status
        status_text = "FINALIZED" if self.prescription.is_finalized else "DRAFT"
        status_color = self.success_green if self.prescription.is_finalized else self.warning_orange
        
        status_style = ParagraphStyle(
            'StatusStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=status_color,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        content.append(Paragraph(f"PRESCRIPTION STATUS: {status_text}", status_style))
        content.append(Spacer(1, 20))
        
        # Build the PDF with header and footer
        doc.build(content, onFirstPage=self._add_header, onLaterPages=self._add_header)
        
        # Get the PDF data
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_data
    
    def generate_and_save(self, user):
        """Generate PDF and save to PrescriptionPDF model"""
        from .models import PrescriptionPDF
        
        # Generate PDF
        pdf_data = self.generate_pdf()
        
        # Calculate checksum
        checksum = hashlib.md5(pdf_data).hexdigest()
        
        # Create PrescriptionPDF instance
        pdf_instance = PrescriptionPDF(
            prescription=self.prescription,
            generated_by=user,
            file_size=len(pdf_data),
            checksum=checksum
        )
        
        # Save header and footer images if provided
        if self.header_image_path:
            pdf_instance.header_image = self.header_image_path
        if self.footer_image_path:
            pdf_instance.footer_image = self.footer_image_path
        
        # Save the PDF file
        filename = f"prescription_{self.prescription.id}_v{pdf_instance.version_number or 1}.pdf"
        pdf_instance.pdf_file.save(
            filename,
            BytesIO(pdf_data),
            save=False
        )
        
        pdf_instance.save()
        
        return pdf_instance


def generate_prescription_pdf(prescription, user, header_image_path=None, footer_image_path=None):
    """Utility function to generate professional prescription PDF"""
    generator = ProfessionalPrescriptionPDFGenerator(
        prescription=prescription,
        header_image_path=header_image_path,
        footer_image_path=footer_image_path
    )
    return generator.generate_and_save(user)