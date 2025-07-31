import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from doctors.models import DoctorStatus
from authentication.models import User

logger = logging.getLogger(__name__)

class DoctorStatusConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time doctor status updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Check if user has appropriate permissions
        if not await self.has_permission():
            await self.close()
            return
        
        # Join the doctor status group
        await self.channel_layer.group_add(
            "doctor_status_updates",
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial status data
        await self.send_initial_status()
        
        logger.info(f"WebSocket connected for user: {self.user.id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave the group
        await self.channel_layer.group_discard(
            "doctor_status_updates",
            self.channel_name
        )
        
        logger.info(f"WebSocket disconnected for user: {self.user.id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'status_update':
                await self.handle_status_update(data)
            elif message_type == 'ping':
                await self.send(json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            else:
                await self.send(json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def handle_status_update(self, data):
        """Handle doctor status update requests"""
        if not await self.is_doctor():
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Only doctors can update status'
            }))
            return
        
        try:
            status_data = data.get('data', {})
            updated_status = await self.update_doctor_status(status_data)
            
            # Broadcast the update to all connected clients
            await self.channel_layer.group_send(
                "doctor_status_updates",
                {
                    'type': 'status_update',
                    'data': updated_status
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating doctor status: {e}")
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Failed to update status'
            }))
    
    async def status_update(self, event):
        """Send status update to WebSocket"""
        await self.send(json.dumps({
            'type': 'status_update',
            'data': event['data']
        }))
    
    async def send_initial_status(self):
        """Send initial doctor status data"""
        try:
            statuses = await self.get_all_doctor_statuses()
            await self.send(json.dumps({
                'type': 'initial_status',
                'data': statuses
            }))
        except Exception as e:
            logger.error(f"Error sending initial status: {e}")
    
    @database_sync_to_async
    def has_permission(self):
        """Check if user has permission to access doctor status"""
        return self.user.is_authenticated and (
            self.user.role in ['admin', 'superadmin'] or 
            hasattr(self.user, 'doctor_profile')
        )
    
    @database_sync_to_async
    def is_doctor(self):
        """Check if user is a doctor"""
        return hasattr(self.user, 'doctor_profile')
    
    @database_sync_to_async
    def update_doctor_status(self, status_data):
        """Update doctor status in database"""
        try:
            doctor_status = DoctorStatus.objects.get(doctor=self.user.doctor_profile)
            
            # Update fields
            if 'current_status' in status_data:
                doctor_status.current_status = status_data['current_status']
            if 'status_note' in status_data:
                doctor_status.status_note = status_data['status_note']
            if 'is_available' in status_data:
                doctor_status.is_available = status_data['is_available']
            
            # Update activity timestamp
            doctor_status.last_activity = timezone.now()
            doctor_status.save()
            
            # Return updated status data
            return {
                'doctor_id': doctor_status.doctor.id,
                'doctor_name': doctor_status.doctor.user.name,
                'doctor_email': doctor_status.doctor.user.email,
                'doctor_specialization': doctor_status.doctor.specialization,
                'doctor_profile_picture': doctor_status.doctor.user.profile_picture.url if doctor_status.doctor.user.profile_picture else None,
                'is_online': doctor_status.is_online,
                'is_logged_in': doctor_status.is_logged_in,
                'is_available': doctor_status.is_available,
                'current_status': doctor_status.current_status,
                'status_display': doctor_status.status_display,
                'is_active': doctor_status.is_active,
                'last_activity': doctor_status.last_activity.isoformat(),
                'last_activity_formatted': doctor_status.last_activity.strftime('%H:%M'),
                'last_login': doctor_status.last_login.isoformat() if doctor_status.last_login else None,
                'last_login_formatted': doctor_status.last_login.strftime('%H:%M') if doctor_status.last_login else None,
                'current_consultation': doctor_status.current_consultation.id if doctor_status.current_consultation else None,
                'current_consultation_info': {
                    'id': doctor_status.current_consultation.id,
                    'patient_name': doctor_status.current_consultation.patient.user.name,
                    'scheduled_time': doctor_status.current_consultation.scheduled_time,
                } if doctor_status.current_consultation else None,
                'status_updated_at': doctor_status.status_updated_at.isoformat(),
                'status_note': doctor_status.status_note,
                'auto_away_threshold': doctor_status.auto_away_threshold,
            }
            
        except DoctorStatus.DoesNotExist:
            raise Exception("Doctor status not found")
    
    @database_sync_to_async
    def get_all_doctor_statuses(self):
        """Get all doctor statuses for initial load"""
        statuses = DoctorStatus.objects.select_related(
            'doctor', 'doctor__user', 'current_consultation', 'current_consultation__patient'
        ).all()
        
        return [{
            'doctor_id': status.doctor.id,
            'doctor_name': status.doctor.user.name,
            'doctor_email': status.doctor.user.email,
            'doctor_specialization': status.doctor.specialization,
            'doctor_profile_picture': status.doctor.user.profile_picture.url if status.doctor.user.profile_picture else None,
            'is_online': status.is_online,
            'is_logged_in': status.is_logged_in,
            'is_available': status.is_available,
            'current_status': status.current_status,
            'status_display': status.status_display,
            'is_active': status.is_active,
            'last_activity': status.last_activity.isoformat(),
            'last_activity_formatted': status.last_activity.strftime('%H:%M'),
            'last_login': status.last_login.isoformat() if status.last_login else None,
            'last_login_formatted': status.last_login.strftime('%H:%M') if status.last_login else None,
            'current_consultation': status.current_consultation.id if status.current_consultation else None,
            'current_consultation_info': {
                'id': status.current_consultation.id,
                'patient_name': status.current_consultation.patient.user.name,
                'scheduled_time': status.current_consultation.scheduled_time,
            } if status.current_consultation else None,
            'status_updated_at': status.status_updated_at.isoformat(),
            'status_note': status.status_note,
            'auto_away_threshold': status.auto_away_threshold,
        } for status in statuses]


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join user-specific notification group
        await self.channel_layer.group_add(
            f"notifications_{self.user.id}",
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Notification WebSocket connected for user: {self.user.id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            f"notifications_{self.user.id}",
            self.channel_name
        )
        logger.info(f"Notification WebSocket disconnected for user: {self.user.id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            else:
                await self.send(json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(json.dumps({
            'type': 'notification',
            'data': event['data']
        }))


class ConsultationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time consultation updates
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Join consultation updates group
        await self.channel_layer.group_add(
            "consultation_updates",
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Consultation WebSocket connected for user: {self.user.id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            "consultation_updates",
            self.channel_name
        )
        logger.info(f"Consultation WebSocket disconnected for user: {self.user.id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            else:
                await self.send(json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def consultation_update(self, event):
        """Send consultation update to WebSocket"""
        await self.send(json.dumps({
            'type': 'consultation_update',
            'data': event['data']
        })) 