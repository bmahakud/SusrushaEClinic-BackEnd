import os
import hashlib
import tempfile
import glob
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from django.conf import settings
import requests
from urllib.parse import urlparse

class WPDFGenerator:
    def __init__(self, prescription, filename="w_generated.pdf", logo_path=None):
        self.prescription = prescription
        self.filename = filename
        self.buffer = BytesIO()
        self.c = canvas.Canvas(self.buffer, pagesize=A4)
        self.width, self.height = A4
        
        # Use the correct logo URL or provided logo path
        if logo_path and os.path.exists(logo_path):
            # Validate that the file is actually an image
            try:
                from PIL import Image
                with Image.open(logo_path) as img:
                    # If we can open it, it's a valid image
                    self.logo_path = logo_path
                    print(f"✅ Valid logo file found: {logo_path}")
            except Exception as e:
                print(f"❌ Invalid logo file {logo_path}: {e}")
                self.logo_path = None
        else:
            self.logo_path = None
        
        # Set up fallback logo URLs
        self.fallback_logo_urls = [
            "https://sushrusaeclinic.com/sushrusa_logo_1-Photoroom.png",
            "https://sushrusaeclinic.com/static/images/logo.png",
            "https://sushrusaeclinic.com/media/logo.png",
            "https://sushrusaeclinic.com/assets/logo.png"
        ]

        # Define colors based on image analysis
        self.line_color = colors.HexColor("#D3D3D3")  # Light gray for lines
        self.heading_color = colors.HexColor("#E17726") # Orange for headings (app theme)
        self.order_medicine_color = colors.HexColor("#E17726") # Orange for ORDER MEDICINE (app theme)

    def _download_logo(self, url):
        """Download logo from URL and save temporarily"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Create a temporary file with unique name
                import tempfile
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png', prefix='sushrusa_logo_')
                os.close(temp_fd)
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Logo downloaded successfully to: {temp_path}")
                return temp_path
        except Exception as e:
            print(f"❌ Error downloading logo from {url}: {e}")
        return None

    def _cleanup_temp_files(self):
        """Clean up temporary logo files"""
        try:
            import glob
            import tempfile
            temp_dir = tempfile.gettempdir()
            pattern = os.path.join(temp_dir, 'sushrusa_logo_*')
            for temp_file in glob.glob(pattern):
                try:
                    os.remove(temp_file)
                    print(f"🧹 Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    print(f"⚠️ Could not remove temporary file {temp_file}: {e}")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

    def _create_text_logo(self, center_x, center_y):
        """Create a professional text-based logo"""
        # Draw a simple logo box - Increased size to match larger image logo
        logo_width = 220
        logo_height = 85
        logo_x = center_x - (logo_width / 2)
        logo_y = center_y - 20
        
        # Draw logo background rectangle
        self.c.setFillColor(colors.white)
        self.c.setStrokeColor(colors.white)
        self.c.rect(logo_x, logo_y, logo_width, logo_height, fill=True, stroke=True)
        
        # Draw logo text - Increased font sizes for even larger logo
        self.c.setFillColor(colors.HexColor("#E17726"))  # Orange color
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawCentredString(center_x, center_y + 25, "SUSHRUSA")
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawCentredString(center_x, center_y + 8, "eCLINIC")
        self.c.setFont("Helvetica", 12)
        self.c.drawCentredString(center_x, center_y - 8, "Healthcare Platform")
        
        # Draw a simple icon (medical cross) - Increased size for even larger logo
        self.c.setFillColor(colors.HexColor("#E17726"))
        self.c.setStrokeColor(colors.HexColor("#E17726"))
        self.c.setLineWidth(4)
        
        # Draw medical cross
        cross_size = 15
        cross_x = center_x - (cross_size / 2)
        cross_y = center_y - 40
        
        # Vertical line
        self.c.line(cross_x + cross_size/2, cross_y, cross_x + cross_size/2, cross_y + cross_size)
        # Horizontal line
        self.c.line(cross_x, cross_y + cross_size/2, cross_x + cross_size, cross_y + cross_size/2)
        
        # Reset line width
        self.c.setLineWidth(1)

    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        if not date_of_birth:
            return "N/A"
        
        today = datetime.now().date()
        age = today.year - date_of_birth.year
        if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
            age -= 1
        return str(age)

    def _draw_header(self):
        # Header background bar
        header_height = 90
        self.c.setFillColor(colors.HexColor("#FFF3E0"))  # Light orange background
        self.c.rect(0, self.height - header_height, self.width, header_height, fill=True, stroke=False)
        self.c.setFillColor(colors.black)

        # Left side - Only clinic info, no logo
        logo_x = 40
        logo_y = self.height - 70
        # Removed logo from left side - only show clinic info

        # Clinic info (left, under logo)
        clinic_y = self.height - 30
        self.c.setFont("Helvetica-Bold", 12)
        self.c.setFillColor(colors.black)
        clinic_name = getattr(getattr(self.prescription.consultation, 'clinic', None), 'name', 'Online Healthcare Platform')
        self.c.drawString(logo_x, clinic_y, clinic_name)
        self.c.setFont("Helvetica", 9)
        clinic_addr = getattr(getattr(self.prescription.consultation, 'clinic', None), 'street', '')
        if clinic_addr:
            self.c.drawString(logo_x, clinic_y - 12, clinic_addr)
        clinic_phone = getattr(getattr(self.prescription.consultation, 'clinic', None), 'phone', '')
        if clinic_phone:
            self.c.drawString(logo_x, clinic_y - 24, f"Phone: {clinic_phone}")

        # Center: Larger logo positioned lower
        center_logo_x = self.width / 2 - 100  # Center the logo
        center_logo_y = self.height - 80  # Moved lower
        center_logo_width = 200  # Increased size
        center_logo_height = 80  # Increased size
        
        # Try to use the new logo in the center
        new_logo_path = "/home/tushar/Videos/sushrusa_backend/media_cdn/clinic_logos/sushrusa_logo_WB.png"
        if os.path.exists(new_logo_path):
            try:
                center_logo = ImageReader(new_logo_path)
                self.c.drawImage(center_logo, center_logo_x, center_logo_y, width=center_logo_width, height=center_logo_height, preserveAspectRatio=True, mask='auto')
                print(f"✅ Using new logo in center: {new_logo_path}")
            except Exception as e:
                print(f"Center logo image error: {e}")
                # Fallback to text if logo fails
                self.c.setFont("Helvetica-Bold", 18)
                self.c.setFillColor(colors.HexColor("#E17726"))  # Orange theme color
                self.c.drawCentredString(self.width / 2, self.height - 40, "E-PRESCRIPTION")
        else:
            # Fallback to text if logo doesn't exist
            self.c.setFont("Helvetica-Bold", 18)
            self.c.setFillColor(colors.HexColor("#E17726"))  # Orange theme color
            self.c.drawCentredString(self.width / 2, self.height - 40, "E-PRESCRIPTION")
        self.c.setFillColor(colors.black)

        # Right: Doctor info (removed registration number)
        right_x = self.width - 220
        right_y = self.height - 30
        self.c.setFont("Helvetica-Bold", 12)
        doctor_name = getattr(self.prescription.doctor, 'name', 'Doctor')
        self.c.drawRightString(self.width - 40, right_y, f"Dr. {doctor_name}")
        # Dynamic doctor details under name
        try:
            doctor_profile = self.prescription.doctor.doctor_profile
            qualifications = getattr(doctor_profile, 'qualification', getattr(self.prescription.doctor, 'qualifications', ''))
            specialization = getattr(doctor_profile, 'specialization', '')
            license_number = getattr(doctor_profile, 'license_number', '')
        except Exception:
            qualifications = getattr(self.prescription.doctor, 'qualifications', '')
            specialization = getattr(self.prescription.doctor, 'specialization', '')
            license_number = getattr(self.prescription.doctor, 'registration_number', '')
        self.c.setFont("Helvetica", 10)
        if qualifications:
            self.c.drawRightString(self.width - 40, right_y - 14, qualifications)
        if specialization or license_number:
            self.c.drawRightString(self.width - 40, right_y - 28, f"{specialization} | {license_number}".strip().strip('| ').strip())
        # Prescribed date
        try:
            prescribed_line = f"Prescribed on {self.prescription.issued_date.strftime('%d/%m/%Y')}"
            self.c.drawRightString(self.width - 40, right_y - 42, prescribed_line)
        except Exception:
            pass

        # Underline below header
        self.c.setStrokeColor(colors.HexColor("#E17726"))  # Orange theme color
        self.c.setLineWidth(2)
        self.c.line(30, self.height - header_height, self.width - 30, self.height - header_height)
        self.c.setLineWidth(1)

    def _draw_appointment_details(self):
        y_pos = self.height - 130 # Starting position after header
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(30, y_pos, "PATIENT DETAILS")
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)

        y_pos -= 20
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 9)
        
        # FIXED: Add proper labels with colons
        # Patient information with labels
        patient_age = self._calculate_age(getattr(self.prescription.patient, 'date_of_birth', None))
        patient_sex = getattr(self.prescription.patient, 'gender', 'N/A')
        patient_sex_short = 'MALE' if patient_sex == 'Male' else 'FEMALE' if patient_sex == 'Female' else 'N/A'
        
        self.c.drawString(30, y_pos, f"Patient Name: {self.prescription.patient.name} | {patient_sex_short} | {patient_age} yrs")
        self.c.drawString(self.width / 2 + 20, y_pos, f"Consult Date: {self.prescription.issued_date.strftime('%d/%m/%Y')} at {self.prescription.issued_time.strftime('%I:%M %p')}")

        y_pos -= 15
        # Removed email, keeping only mobile number
        patient_mobile = getattr(self.prescription.patient, 'mobile', '+918976358976')
        self.c.drawString(30, y_pos, f"Contact: {patient_mobile}")
        
        # Dynamic consultation type
        consultation_type = "Online"
        if hasattr(self.prescription, 'consultation') and self.prescription.consultation:
            consultation_type = self.prescription.consultation.get_consultation_type_display()
        self.c.drawString(self.width / 2 + 20, y_pos, f"Consult Type: {consultation_type}")

        y_pos -= 15
        # Dynamic UHID (using patient ID or mobile)
        uhid = getattr(self.prescription.patient, 'uhid', f"UHID{self.prescription.patient.id}")
        self.c.drawString(30, y_pos, f"UHID: {uhid}")

        y_pos -= 15
        # Dynamic appointment ID (using prescription ID)
        self.c.drawString(30, y_pos, f"Appt ID: {self.prescription.id}")

        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)

    def _draw_vital_signs(self):
        y_pos = self.height - 220 # Equal spacing from appointment details
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(30, y_pos, "VITAL SIGNS")
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)

        y_pos -= 20
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 9)
        
        # Collect all vital signs data
        vitals_data = []
        
        # From prescription model
        if self.prescription.pulse:
            vitals_data.append(f"Pulse: {self.prescription.pulse} bpm")
        if self.prescription.blood_pressure_systolic and self.prescription.blood_pressure_diastolic:
            vitals_data.append(f"Blood Pressure: {self.prescription.blood_pressure_systolic}/{self.prescription.blood_pressure_diastolic} mmHg")
        if self.prescription.temperature:
            vitals_data.append(f"Temperature: {self.prescription.temperature}°C")
        if self.prescription.weight:
            vitals_data.append(f"Weight: {self.prescription.weight} kg")
        if self.prescription.height:
            vitals_data.append(f"Height: {self.prescription.height} cm")
        
        # From consultation vital signs if available
        if hasattr(self.prescription, 'consultation') and self.prescription.consultation and hasattr(self.prescription.consultation, 'vital_signs'):
            consultation_vitals = self.prescription.consultation.vital_signs
            if consultation_vitals:
                if consultation_vitals.heart_rate and not any('Pulse' in v for v in vitals_data):
                    vitals_data.append(f"Pulse: {consultation_vitals.heart_rate} bpm")
                if consultation_vitals.blood_pressure_systolic and consultation_vitals.blood_pressure_diastolic and not any('Blood Pressure' in v for v in vitals_data):
                    vitals_data.append(f"Blood Pressure: {consultation_vitals.blood_pressure_systolic}/{consultation_vitals.blood_pressure_diastolic} mmHg")
                if consultation_vitals.temperature and not any('Temperature' in v for v in vitals_data):
                    vitals_data.append(f"Temperature: {consultation_vitals.temperature}°C")
                if consultation_vitals.weight and not any('Weight' in v for v in vitals_data):
                    vitals_data.append(f"Weight: {consultation_vitals.weight} kg")
                if consultation_vitals.height and not any('Height' in v for v in vitals_data):
                    vitals_data.append(f"Height: {consultation_vitals.height} cm")
                if consultation_vitals.bmi:
                    vitals_data.append(f"BMI: {consultation_vitals.bmi}")
                if consultation_vitals.respiratory_rate:
                    vitals_data.append(f"Respiratory Rate: {consultation_vitals.respiratory_rate} /min")
                if consultation_vitals.oxygen_saturation:
                    vitals_data.append(f"Oxygen Saturation: {consultation_vitals.oxygen_saturation}%")
                if consultation_vitals.blood_glucose:
                    vitals_data.append(f"Blood Glucose: {consultation_vitals.blood_glucose} mg/dL")
        
        # Display vital signs in two columns
        if vitals_data:
            left_column = vitals_data[:len(vitals_data)//2 + len(vitals_data)%2]
            right_column = vitals_data[len(vitals_data)//2 + len(vitals_data)%2:]
            
            for i, vital in enumerate(left_column):
                self.c.drawString(30, y_pos, vital)
                if i < len(right_column):
                    self.c.drawString(self.width / 2 + 20, y_pos, right_column[i])
                y_pos -= 15
        else:
            self.c.drawString(30, y_pos, "No vital signs recorded")

        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)

    def _draw_patient_history(self):
        """Draw patient medical history section"""
        y_pos = self.height - 310 # Equal spacing from vital signs
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(30, y_pos, "PATIENT MEDICAL HISTORY")
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)
        y_pos -= 20
        
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 10)
        if self.prescription.patient_previous_history:
            self.c.drawString(30, y_pos, f"Previous Medical History: {self.prescription.patient_previous_history}")
        else:
            self.c.drawString(30, y_pos, "No previous medical history recorded")
        y_pos -= 15
        
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)
        return y_pos

    def _draw_diagnosis(self):
        y_pos = self.height - 380 # Equal spacing from patient history
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(30, y_pos, "DIAGNOSIS / PROVISIONAL DIAGNOSIS")
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)

        y_pos -= 20
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 10)
        
        # Enhanced diagnosis display with separate sections
        diagnosis_sections = []
        
        # Primary Diagnosis
        if self.prescription.primary_diagnosis:
            diagnosis_sections.append(f"Primary Diagnosis: {self.prescription.primary_diagnosis}")
        
        # Clinical Classification
        if self.prescription.clinical_classification:
            diagnosis_sections.append(f"Clinical Classification: {self.prescription.clinical_classification}")
        
        # Display diagnosis sections
        if diagnosis_sections:
            for diagnosis in diagnosis_sections:
                self.c.drawString(30, y_pos, diagnosis)
                y_pos -= 15
        else:
            self.c.drawString(30, y_pos, "No diagnosis recorded")

        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)

    def _draw_medication(self):
        y_pos = self.height - 490 # Equal spacing from diagnosis
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(30, y_pos, "MEDICATIONS")
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)
        y_pos -= 25

        # Table headers
        headers = ["Name", "Strength", "Dosage", "Frequency", "Duration", "Instructions"]
        col_widths = [110, 70, 60, 70, 60, 140]
        x_positions = [30]
        for w in col_widths[:-1]:
            x_positions.append(x_positions[-1] + w)

        self.c.setFillColor(colors.HexColor("#f5f5f5"))
        self.c.rect(30, y_pos - 5, sum(col_widths), 20, fill=True, stroke=False)
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 10)
        for i, header in enumerate(headers):
            self.c.drawString(x_positions[i] + 2, y_pos + 8, header)
        y_pos -= 20

        # Medications rows
        medications = self.prescription.medications.all().order_by('order')
        if medications.exists():
            for idx, med in enumerate(medications):
                # Alternate row color
                if idx % 2 == 0:
                    self.c.setFillColor(colors.whitesmoke)
                else:
                    self.c.setFillColor(colors.HexColor("#e9f0fb"))
                self.c.rect(30, y_pos - 2, sum(col_widths), 18, fill=True, stroke=False)
                self.c.setFillColor(colors.black)
                self.c.setFont("Helvetica", 9)
                values = [
                    med.medicine_name or '',
                    med.composition or '',
                    f"{med.morning_dose}-{med.afternoon_dose}-{med.evening_dose}",
                    med.get_frequency_display() if hasattr(med, 'get_frequency_display') else med.frequency,
                    f"{med.duration_days or ''}d {med.duration_weeks or ''}w {med.duration_months or ''}m",
                    med.special_instructions or med.notes or ''
                ]
                for i, value in enumerate(values):
                    self.c.drawString(x_positions[i] + 2, y_pos + 4, str(value)[:22])
                y_pos -= 18
                if y_pos < 120:
                    self.c.showPage()
                    self._draw_header()
                    y_pos = self.height - 120
        else:
            self.c.setFillColor(colors.black)
            self.c.setFont("Helvetica", 9)
            self.c.drawString(30, y_pos, "No medications prescribed")
            y_pos -= 15

        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)
        
        # Draw investigation tests first
        y_pos = self._draw_investigation_tests(y_pos - 20)
        
        # Then draw advice and instructions
        self._draw_advice_instructions(y_pos)

    def _draw_doctor_signature(self):
        """Draw doctor signature for single page prescriptions"""
        # Position signature at bottom right
        signature_y = 150  # Above footer
        
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 9)
        self.c.drawString(self.width - 200, signature_y, f"Prescribed on {self.prescription.issued_date.strftime('%d/%m/%Y')}")
        
        # Get doctor profile information
        try:
            doctor_profile = self.prescription.doctor.doctor_profile
            doctor_qualifications = getattr(doctor_profile, 'qualification', 'MBBS')
            doctor_specialization = getattr(doctor_profile, 'specialization', 'Family Physician')
            license_number = getattr(doctor_profile, 'license_number', 'Reg.No. TSMC/FMR/15345')
            
            self.c.drawString(self.width - 200, signature_y - 15, doctor_qualifications)
            self.c.drawString(self.width - 200, signature_y - 30, f"{doctor_specialization} | {license_number}")
            
            # Draw doctor's signature image if available
            if doctor_profile.signature:
                try:
                    from reportlab.lib.utils import ImageReader
                    import requests
                    from io import BytesIO
                    
                    # Try to get signature from cloud storage
                    signature_url = doctor_profile.signature.url
                    
                    # Download signature from cloud storage
                    response = requests.get(signature_url, timeout=10)
                    if response.status_code == 200:
                        # Create image from bytes
                        signature_data = BytesIO(response.content)
                        signature_img = ImageReader(signature_data)
                        
                        # Calculate signature dimensions (maintain aspect ratio)
                        img_width, img_height = signature_img.getSize()
                        max_width = 120
                        max_height = 60
                        
                        # Scale to fit within bounds while maintaining aspect ratio
                        scale = min(max_width / img_width, max_height / img_height)
                        scaled_width = img_width * scale
                        scaled_height = img_height * scale
                        
                        # Position signature above the signature text
                        signature_x = self.width - 200
                        signature_y_pos = signature_y - 60
                        
                        self.c.drawImage(signature_img, signature_x, signature_y_pos, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
                        
                        # Add signature text below the image
                        self.c.setFont("Helvetica", 9)
                        self.c.drawString(signature_x, signature_y_pos - 20, "Doctor's Signature")
                        
                except Exception as e:
                    print(f"Error drawing doctor signature: {e}")
                    # Fallback to text signature
                    self.c.setFont("Helvetica-Bold", 12)
                    self.c.drawString(self.width - 200, signature_y - 60, "_________________")
                    self.c.setFont("Helvetica", 9)
                    self.c.drawString(self.width - 200, signature_y - 75, "Doctor's Signature")
            else:
                # No signature in profile - use text signature
                self.c.setFont("Helvetica-Bold", 12)
                self.c.drawString(self.width - 200, signature_y - 60, "_________________")
                self.c.setFont("Helvetica", 9)
                self.c.drawString(self.width - 200, signature_y - 75, "Doctor's Signature")
            
        except Exception as e:
            print(f"Error accessing doctor profile: {e}")
            # Fallback to basic signature
            self.c.drawString(self.width - 200, signature_y - 30, "MBBS")
            self.c.drawString(self.width - 200, signature_y - 45, "Family Physician | Reg.No. TSMC/FMR/15345")
            
            # Add signature line
            self.c.setFont("Helvetica-Bold", 12)
            self.c.drawString(self.width - 200, signature_y - 70, "_________________")
            self.c.setFont("Helvetica", 9)
            self.c.drawString(self.width - 200, signature_y - 85, "Doctor's Signature")

    def _draw_doctor_signature_page2(self):
        """Draw doctor signature for second page prescriptions"""
        # Position signature at center-right of page 2
        signature_y = self.height - 300
        
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 9)
        self.c.drawString(self.width - 200, signature_y, f"Prescribed on {self.prescription.issued_date.strftime('%d/%m/%Y')} by")
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(self.width - 200, signature_y - 15, f"Dr. {self.prescription.doctor.name}")
        self.c.setFont("Helvetica", 9)
        
        # Get doctor profile information
        try:
            doctor_profile = self.prescription.doctor.doctor_profile
            doctor_qualifications = getattr(doctor_profile, 'qualification', 'MBBS')
            doctor_specialization = getattr(doctor_profile, 'specialization', 'Family Physician')
            license_number = getattr(doctor_profile, 'license_number', 'Reg.No. TSMC/FMR/15345')
            
            self.c.drawString(self.width - 200, signature_y - 30, doctor_qualifications)
            self.c.drawString(self.width - 200, signature_y - 45, f"{doctor_specialization} | {license_number}")
            
            # Draw doctor's signature image if available
            if doctor_profile.signature:
                try:
                    from reportlab.lib.utils import ImageReader
                    import requests
                    from io import BytesIO
                    
                    # Try to get signature from cloud storage
                    signature_url = doctor_profile.signature.url
                    
                    # Download signature from cloud storage
                    response = requests.get(signature_url, timeout=10)
                    if response.status_code == 200:
                        # Create image from bytes
                        signature_data = BytesIO(response.content)
                        signature_img = ImageReader(signature_data)
                        
                        # Calculate signature dimensions (maintain aspect ratio)
                        img_width, img_height = signature_img.getSize()
                        max_width = 120
                        max_height = 60
                        
                        # Scale to fit within bounds while maintaining aspect ratio
                        scale = min(max_width / img_width, max_height / img_height)
                        scaled_width = img_width * scale
                        scaled_height = img_height * scale
                        
                        # Position signature above the signature text
                        signature_x = self.width - 200
                        signature_y_pos = signature_y - 60
                        
                        self.c.drawImage(signature_img, signature_x, signature_y_pos, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
                        
                        # Add signature text below the image
                        self.c.setFont("Helvetica", 9)
                        self.c.drawString(signature_x, signature_y_pos - 20, "Doctor's Signature")
                        
                except Exception as e:
                    print(f"Error drawing doctor signature: {e}")
                    # Fallback to text signature
                    self.c.setFont("Helvetica-Bold", 12)
                    self.c.drawString(self.width - 200, signature_y - 60, "_________________")
                    self.c.setFont("Helvetica", 9)
                    self.c.drawString(self.width - 200, signature_y - 75, "Doctor's Signature")
            else:
                # No signature in profile - use text signature
                self.c.setFont("Helvetica-Bold", 12)
                self.c.drawString(self.width - 200, signature_y - 60, "_________________")
                self.c.setFont("Helvetica", 9)
                self.c.drawString(self.width - 200, signature_y - 75, "Doctor's Signature")
            
        except Exception as e:
            print(f"Error accessing doctor profile: {e}")
            # Fallback to basic signature
            self.c.drawString(self.width - 200, signature_y - 30, "MBBS")
            self.c.drawString(self.width - 200, signature_y - 45, "Family Physician | Reg.No. TSMC/FMR/15345")
            
            # Add signature line
            self.c.setFont("Helvetica-Bold", 12)
            self.c.drawString(self.width - 200, signature_y - 70, "_________________")
            self.c.setFont("Helvetica", 9)
            self.c.drawString(self.width - 200, signature_y - 85, "Doctor's Signature")



    def _draw_advice_instructions(self, start_y_pos=None):
        # FIXED: Check if we need a page break before drawing advice
        if start_y_pos is None:
            y_pos = self.height - 580 # Equal spacing from medications (calculated dynamically)
        else:
            y_pos = start_y_pos
        
        # If we're too close to bottom, start new page
        if y_pos < 200:
            self.c.showPage()
            self._draw_header()  # Redraw header on new page
            y_pos = self.height - 200  # Reset position for new page
        
        self.c.setFillColor(self.heading_color)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(30, y_pos, "ADVICE/ INSTRUCTIONS")
        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)

        # Enhanced advice and instructions display
        y_pos -= 20
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica", 9)
        
        instructions_sections = []
        
        # General Instructions
        if self.prescription.general_instructions:
            instructions_sections.append(f"General Instructions: {self.prescription.general_instructions}")
        
        # Fluid Intake
        if self.prescription.fluid_intake:
            instructions_sections.append(f"Fluid Intake: {self.prescription.fluid_intake}")
        
        # Diet Instructions
        if self.prescription.diet_instructions:
            instructions_sections.append(f"Diet Instructions: {self.prescription.diet_instructions}")
        
        # Lifestyle Advice
        if self.prescription.lifestyle_advice:
            instructions_sections.append(f"Lifestyle Advice: {self.prescription.lifestyle_advice}")
        
        # Next Visit
        if self.prescription.next_visit:
            instructions_sections.append(f"Next Visit: {self.prescription.next_visit}")
        
        # Follow-up Notes
        if self.prescription.follow_up_notes:
            instructions_sections.append(f"Follow-up Notes: {self.prescription.follow_up_notes}")
        
        if instructions_sections:
            for instruction in instructions_sections:
                self.c.drawString(30, y_pos, instruction)
                y_pos -= 15
        else:
            self.c.drawString(30, y_pos, "General Instructions: Take regular medication as prescribed")
            y_pos -= 15

        self.c.setStrokeColor(self.line_color)
        self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)

    def _draw_investigation_tests(self, start_y_pos=None):
        """Draw investigation tests section"""
        if start_y_pos is None:
            y_pos = self.height - 580
        else:
            y_pos = start_y_pos
        
        # If we're too close to bottom, start new page
        if y_pos < 200:
            self.c.showPage()
            self._draw_header()  # Redraw header on new page
            y_pos = self.height - 200  # Reset position for new page
        
        # Get investigation tests for this prescription
        try:
            investigations = self.prescription.investigations.all().order_by('order')
            if investigations.exists():
                self.c.setFillColor(self.heading_color)
                self.c.setFont("Helvetica-Bold", 10)
                self.c.drawString(30, y_pos, "INVESTIGATION TESTS")
                self.c.setStrokeColor(self.line_color)
                self.c.line(30, y_pos - 5, self.width - 30, y_pos - 5)
                
                y_pos -= 35  # Increased margin from 20 to 35 for even better spacing
                self.c.setFillColor(colors.black)
                self.c.setFont("Helvetica", 9)
                
                # Draw investigation tests in a table format
                for idx, investigation in enumerate(investigations):
                    # Alternate row color
                    if idx % 2 == 0:
                        self.c.setFillColor(colors.whitesmoke)
                    else:
                        self.c.setFillColor(colors.HexColor("#e9f0fb"))
                    
                    # Draw row background
                    row_height = 25
                    self.c.rect(30, y_pos - 2, self.width - 60, row_height, fill=True, stroke=False)
                    self.c.setFillColor(colors.black)
                    
                    # Test name and category
                    test_name = investigation.test.name
                    category_name = investigation.test.category.name
                    priority = investigation.priority.upper()
                    
                    # Draw test information
                    self.c.setFont("Helvetica-Bold", 9)
                    self.c.drawString(35, y_pos + 15, f"{test_name}")
                    self.c.setFont("Helvetica", 8)
                    self.c.drawString(35, y_pos + 5, f"Category: {category_name}")
                    
                    # Priority and cost
                    self.c.setFont("Helvetica-Bold", 8)
                    self.c.drawString(self.width - 200, y_pos + 15, f"Priority: {priority}")
                    if investigation.test.estimated_cost:
                        self.c.drawString(self.width - 200, y_pos + 5, f"Cost: ₹{investigation.test.estimated_cost}")
                    
                    # Special instructions if any
                    if investigation.special_instructions:
                        self.c.setFont("Helvetica", 8)
                        self.c.drawString(35, y_pos - 5, f"Instructions: {investigation.special_instructions}")
                    
                    y_pos -= (row_height + 5)
                    
                    # Check if we need a page break
                    if y_pos < 120:
                        self.c.showPage()
                        self._draw_header()
                        y_pos = self.height - 120
                
                # Add line after investigations
                self.c.setStrokeColor(self.line_color)
                self.c.line(30, y_pos - 10, self.width - 30, y_pos - 10)
                
                return y_pos - 20  # Return the new y position
            else:
                return start_y_pos  # No investigations, return original position
                
        except Exception as e:
            print(f"Error drawing investigation tests: {e}")
            return start_y_pos  # Return original position on error

    def _draw_footer(self, page_num, total_pages):
        # Simplified footer with just blank space at bottom
        # Add blank space at bottom
        self.c.setFillColor(colors.white)
        self.c.rect(0, 0, self.width, 80, fill=True, stroke=False)

    def generate_pdf(self):
        # Single page prescription - everything on one page
        self._draw_header()
        self._draw_appointment_details()
        self._draw_vital_signs()
        self._draw_patient_history()
        self._draw_diagnosis()
        self._draw_medication()
        
        # Add footer and signature on same page
        self._draw_footer(1, 1)
        self._draw_doctor_signature()
        
        self.c.save()
        
        # Clean up temporary files
        self._cleanup_temp_files()
        
        # Get the PDF data from buffer
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
        
        # Save header image if provided
        if self.logo_path:
            pdf_instance.header_image = self.logo_path
        
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
    """Generate a professional prescription PDF using the WPDFGenerator design"""
    generator = WPDFGenerator(
        prescription=prescription,
        logo_path=header_image_path
    )
    return generator.generate_and_save(user)


def test_pdf_generator():
    """Test function to verify PDF generation works correctly"""
    try:
        # Create a mock prescription object for testing
        class MockPrescription:
            def __init__(self):
                self.id = "TEST001"
                self.patient = MockPatient()
                self.doctor = MockDoctor()
                self.consultation = MockConsultation()
                self.issued_date = datetime.now()
                self.issued_time = datetime.now()
                self.primary_diagnosis = "Test Diagnosis"
                self.general_instructions = "Test Instructions"
                self.medications = MockMedicationManager()
                self.pulse = 72
                self.blood_pressure_systolic = 120
                self.blood_pressure_diastolic = 80
                self.temperature = 98.6
                self.weight = 70
                self.height = 170
        
        class MockPatient:
            def __init__(self):
                self.name = "Test Patient"
                self.date_of_birth = datetime(1990, 1, 1)
                self.gender = "Male"
                self.email = "test@example.com"
                self.mobile = "+919876543210"
        
        class MockDoctor:
            def __init__(self):
                self.name = "Dr. Test Doctor"
                self.qualifications = "MBBS, MD"
                self.specialization = "General Medicine"
                self.registration_number = "Reg.No. TEST123"
                self.mobile = "+919876543211"
                self.email = "doctor@example.com"
        
        class MockConsultation:
            def __init__(self):
                self.chief_complaint = "Test complaint"
                self.clinic = None
        
        class MockMedicationManager:
            def all(self):
                return []
            def exists(self):
                return False
            def count(self):
                return 0
        
        class MockUser:
            def __init__(self):
                self.id = "USER001"
        
        # Test the generator
        mock_prescription = MockPrescription()
        mock_user = MockUser()
        
        # Test with no logo (should use text logo)
        print("🧪 Testing PDF generation with text logo...")
        generator = WPDFGenerator(mock_prescription)
        pdf_data = generator.generate_pdf()
        
        print("✅ PDF generation test successful!")
        print(f"📄 Generated PDF size: {len(pdf_data)} bytes")
        
        # Test with a real logo if we can create one
        try:
            test_logo_path = create_test_logo()
            if test_logo_path:
                print("🧪 Testing PDF generation with real logo...")
                generator_with_logo = WPDFGenerator(mock_prescription, logo_path=test_logo_path)
                pdf_data_with_logo = generator_with_logo.generate_pdf()
                print("✅ PDF generation with logo test successful!")
                print(f"📄 Generated PDF with logo size: {len(pdf_data_with_logo)} bytes")
                
                # Clean up test logo
                try:
                    os.remove(test_logo_path)
                    print(f"🧹 Cleaned up test logo: {test_logo_path}")
                except:
                    pass
        except Exception as e:
            print(f"⚠️ Logo test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
        return False


def create_test_logo():
    """Create a simple test logo file for testing purposes"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple logo image - Increased size to match even larger dimensions
        width, height = 360, 144
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple logo design
        # Background rectangle
        draw.rectangle([18, 18, width-18, height-18], outline='#E17726', width=5)
        
        # Text
        try:
            # Try to use a default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            # Fallback to default
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw text - Adjusted for even larger logo
        draw.text((width//2, 40), "SUSHRUSA", fill='#E17726', anchor='mm', font=font_large)
        draw.text((width//2, 70), "eCLINIC", fill='#E17726', anchor='mm', font=font_small)
        draw.text((width//2, 95), "Healthcare", fill='#E17726', anchor='mm', font=font_small)
        
        # Draw a simple medical cross - Even larger for bigger logo
        cross_size = 25
        cross_x = width - 50
        cross_y = height//2 - cross_size//2
        
        # Vertical line
        draw.line([cross_x + cross_size//2, cross_y, cross_x + cross_size//2, cross_y + cross_size], fill='#E17726', width=2)
        # Horizontal line
        draw.line([cross_x, cross_y + cross_size//2, cross_x + cross_size, cross_y + cross_size//2], fill='#E17726', width=2)
        
        # Save the logo
        logo_path = "test_logo.png"
        image.save(logo_path)
        print(f"✅ Test logo created: {logo_path}")
        return logo_path
        
    except Exception as e:
        print(f"❌ Failed to create test logo: {e}")
        return None


def generate_mobile_prescription_pdf(prescription, uploaded_image_path):
    """
    Generate a mobile prescription PDF with uploaded image at the bottom of vital signs
    """
    try:
        # Create PDF generator instance
        generator = WPDFGenerator(prescription, "mobile_prescription.pdf")
        
        # Generate the base PDF with all sections except the image
        pdf_path = generator.generate_pdf()
        
        # Now we need to add the uploaded image to the PDF
        # For now, we'll use the existing PDF generation and modify it to include the image
        # This is a simplified approach - in production, you might want to use a more sophisticated PDF manipulation library
        
        # Create a new PDF with the image
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from django.conf import settings
        import os
        
        # Create output path
        output_dir = os.path.join(settings.MEDIA_ROOT, "prescriptions", "pdfs", prescription.consultation_id)
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"mobile_prescription_{timestamp}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Create new PDF with image
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Draw the prescription content (simplified version for mobile)
        _draw_mobile_prescription_content(c, prescription, uploaded_image_path, width, height)
        
        c.save()
        
        return output_path
        
    except Exception as e:
        print(f"Error generating mobile PDF: {e}")
        raise e


def _draw_mobile_prescription_content(canvas, prescription, image_path, width, height):
    """
    Draw mobile prescription content with uploaded image
    """
    try:
        # Header
        canvas.setFillColor(colors.HexColor('#FFF3E0'))
        canvas.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        # Logo
        logo_path = os.path.join(settings.MEDIA_ROOT, "sushrusa_logo_1-Photoroom.png")
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            canvas.drawImage(logo, 30, height - 60, width=40, height=40)
        
        # Title
        canvas.setFillColor(colors.HexColor('#E17726'))
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(80, height - 45, "SUSHRUSA eCLINIC")
        canvas.drawString(80, height - 60, "PRESCRIPTION")
        
        # Doctor info
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.black)
        doctor = prescription.doctor
        canvas.drawString(30, height - 100, f"Dr. {doctor.get('name', 'N/A')}")
        canvas.drawString(30, height - 115, f"{doctor.get('qualification', 'MBBS')} | {doctor.get('specialization', 'General Medicine')}")
        canvas.drawString(30, height - 130, f"Registration: {doctor.get('registration_number', 'N/A')}")
        
        # Prescribed date
        canvas.drawString(width - 150, height - 100, f"Prescribed on {prescription.issued_date}")
        
        # Patient details
        y_pos = height - 180
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.HexColor('#E17726'))
        canvas.drawString(30, y_pos, "PATIENT DETAILS")
        
        y_pos -= 20
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.black)
        patient = prescription.patient
        canvas.drawString(30, y_pos, f"Name: {patient.get('name', 'N/A')}")
        y_pos -= 15
        canvas.drawString(30, y_pos, f"Age: {prescription.patient_age} years | Gender: {prescription.patient_gender}")
        y_pos -= 15
        canvas.drawString(30, y_pos, f"Mobile: {patient.get('phone', 'N/A')}")
        
        # Vital signs
        y_pos -= 30
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.HexColor('#E17726'))
        canvas.drawString(30, y_pos, "VITAL SIGNS")
        
        y_pos -= 20
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.black)
        
        vital_signs = prescription.vital_signs
        if vital_signs:
            if vital_signs.get('pulse'):
                canvas.drawString(30, y_pos, f"Pulse: {vital_signs.pulse} bpm")
                y_pos -= 15
            if vital_signs.get('blood_pressure_systolic') and vital_signs.get('blood_pressure_diastolic'):
                canvas.drawString(30, y_pos, f"Blood Pressure: {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic} mmHg")
                y_pos -= 15
            if vital_signs.get('temperature'):
                canvas.drawString(30, y_pos, f"Temperature: {vital_signs.temperature}°F")
                y_pos -= 15
            if vital_signs.get('weight'):
                canvas.drawString(30, y_pos, f"Weight: {vital_signs.weight} kg")
                y_pos -= 15
            if vital_signs.get('height'):
                canvas.drawString(30, y_pos, f"Height: {vital_signs.height} cm")
                y_pos -= 15
        
        # Add uploaded image at the bottom of vital signs
        y_pos -= 20
        try:
            # Check if image exists
            full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
            if os.path.exists(full_image_path):
                # Add image title
                canvas.setFont("Helvetica-Bold", 12)
                canvas.setFillColor(colors.HexColor('#E17726'))
                canvas.drawString(30, y_pos, "PRESCRIPTION IMAGE")
                y_pos -= 20
                
                # Load and draw the image
                img = ImageReader(full_image_path)
                
                # Calculate image dimensions (max width 400px, maintain aspect ratio)
                img_width, img_height = img.getSize()
                max_width = 400
                if img_width > max_width:
                    ratio = max_width / img_width
                    img_width = max_width
                    img_height = img_height * ratio
                
                # Draw image
                canvas.drawImage(img, 30, y_pos - img_height, width=img_width, height=img_height)
                y_pos -= img_height + 20
            else:
                canvas.setFont("Helvetica", 10)
                canvas.setFillColor(colors.red)
                canvas.drawString(30, y_pos, "Image not found")
                y_pos -= 20
        except Exception as e:
            canvas.setFont("Helvetica", 10)
            canvas.setFillColor(colors.red)
            canvas.drawString(30, y_pos, f"Error loading image: {str(e)}")
            y_pos -= 20
        
        # Doctor signature area
        y_pos -= 30
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(colors.HexColor('#E17726'))
        canvas.drawString(30, y_pos, "DOCTOR'S SIGNATURE")
        
        y_pos -= 40
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.black)
        canvas.drawString(30, y_pos, f"Dr. {doctor.get('name', 'N/A')}")
        canvas.drawString(30, y_pos - 15, f"{doctor.get('qualification', 'MBBS')} | {doctor.get('specialization', 'General Medicine')}")
        
    except Exception as e:
        print(f"Error drawing mobile prescription content: {e}")
        raise e

