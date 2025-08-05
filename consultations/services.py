import requests
import json
from datetime import datetime
from django.conf import settings


class WhatsAppNotificationService:
    """Service for sending WhatsApp notifications via MSG91 API"""
    
    def __init__(self):
        self.auth_key = "416664AgVFnjJ8nhio65d6fc7bP1"
        self.integrated_number = "917008182954"
        self.template_name = "diracai3"
        self.namespace = "1159b496_e313_4115_ace7_0210e4de2eea"
        self.api_url = "https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/bulk/"
    
    def send_doctor_appointment_notification(self, consultation):
        """
        Send WhatsApp notification to doctor about scheduled appointment
        
        Args:
            consultation: Consultation object with all details
        """
        try:
            # Get doctor's phone number
            doctor_phone = consultation.doctor.phone
            if not doctor_phone:
                print(f"❌ No phone number found for doctor: {consultation.doctor.name}")
                return False
            
            # Format phone number with 91 prefix
            if not doctor_phone.startswith('91'):
                doctor_phone = f"91{doctor_phone}"
            
            # Format date and time
            scheduled_date = consultation.scheduled_date.strftime("%d %B, %Y")
            scheduled_time = consultation.scheduled_time.strftime("%I:%M %p")
            
            # Get meeting link
            try:
                meeting_link = consultation.doctor_meeting_link
            except:
                meeting_link = "Meeting link will be shared soon"
            
            # Prepare the API payload
            payload = {
                "integrated_number": self.integrated_number,
                "content_type": "template",
                "payload": {
                    "messaging_product": "whatsapp",
                    "type": "template",
                    "template": {
                        "name": self.template_name,
                        "language": {
                            "code": "en",
                            "policy": "deterministic"
                        },
                        "namespace": self.namespace,
                        "to_and_components": [
                            {
                                "to": [doctor_phone],
                                "components": [
                                    {
                                        "type": "body",
                                        "parameters": [
                                            {
                                                "type": "text",
                                                "text": consultation.doctor.name
                                            },
                                            {
                                                "type": "text",
                                                "text": scheduled_date
                                            },
                                            {
                                                "type": "text",
                                                "text": scheduled_time
                                            },
                                            {
                                                "type": "text",
                                                "text": consultation.patient.name
                                            },
                                            {
                                                "type": "text",
                                                "text": consultation.consultation_type
                                            },
                                            {
                                                "type": "text",
                                                "text": meeting_link
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
            
            # Send the request
            headers = {
                'Content-Type': 'application/json',
                'authkey': self.auth_key
            }
            
            print(f"📱 Sending WhatsApp notification to doctor: {consultation.doctor.name} ({doctor_phone})")
            print(f"📱 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📱 WhatsApp API Response Status: {response.status_code}")
            print(f"📱 WhatsApp API Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('status') == 'success':
                    print(f"✅ WhatsApp notification sent successfully to doctor: {consultation.doctor.name}")
                    return True
                else:
                    print(f"❌ WhatsApp API returned error: {response_data}")
                    return False
            else:
                print(f"❌ WhatsApp API request failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending WhatsApp notification: {str(e)}")
            return False
    
    def send_patient_appointment_confirmation(self, consultation):
        """
        Send WhatsApp notification to patient about appointment confirmation
        
        Args:
            consultation: Consultation object with all details
        """
        try:
            # Get patient's phone number
            patient_phone = consultation.patient.phone
            if not patient_phone:
                print(f"❌ No phone number found for patient: {consultation.patient.name}")
                return False
            
            # Format phone number with 91 prefix
            if not patient_phone.startswith('91'):
                patient_phone = f"91{patient_phone}"
            
            # Format date and time
            scheduled_date = consultation.scheduled_date.strftime("%d %B, %Y")
            scheduled_time = consultation.scheduled_time.strftime("%I:%M %p")
            
            # Get meeting link
            try:
                meeting_link = consultation.doctor_meeting_link
            except:
                meeting_link = "Meeting link will be shared soon"
            
            # Prepare the API payload (using same template for now)
            payload = {
                "integrated_number": self.integrated_number,
                "content_type": "template",
                "payload": {
                    "messaging_product": "whatsapp",
                    "type": "template",
                    "template": {
                        "name": self.template_name,
                        "language": {
                            "code": "en",
                            "policy": "deterministic"
                        },
                        "namespace": self.namespace,
                        "to_and_components": [
                            {
                                "to": [patient_phone],
                                "components": [
                                    {
                                        "type": "body",
                                        "parameters": [
                                            {
                                                "type": "text",
                                                "text": consultation.patient.name
                                            },
                                            {
                                                "type": "text",
                                                "text": scheduled_date
                                            },
                                            {
                                                "type": "text",
                                                "text": scheduled_time
                                            },
                                            {
                                                "type": "text",
                                                "text": consultation.doctor.name
                                            },
                                            {
                                                "type": "text",
                                                "text": consultation.consultation_type
                                            },
                                            {
                                                "type": "text",
                                                "text": meeting_link
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
            
            # Send the request
            headers = {
                'Content-Type': 'application/json',
                'authkey': self.auth_key
            }
            
            print(f"📱 Sending WhatsApp notification to patient: {consultation.patient.name} ({patient_phone})")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📱 WhatsApp API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('status') == 'success':
                    print(f"✅ WhatsApp notification sent successfully to patient: {consultation.patient.name}")
                    return True
                else:
                    print(f"❌ WhatsApp API returned error: {response_data}")
                    return False
            else:
                print(f"❌ WhatsApp API request failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending WhatsApp notification: {str(e)}")
            return False 