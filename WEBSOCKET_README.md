# WebSocket Implementation for Sushrusa Backend

This document describes the WebSocket implementation for real-time communication in the Sushrusa backend.

## Overview

The WebSocket implementation provides real-time updates for:
- Doctor status monitoring
- Notifications
- Consultation updates
- Chat functionality

## Architecture

### Components

1. **ASGI Application**: Uses Django Channels for WebSocket support
2. **Channel Layers**: Redis-based backend for message routing
3. **Consumers**: WebSocket consumers for different types of real-time updates
4. **Middleware**: Custom authentication middleware for WebSocket connections

### WebSocket Endpoints

- `ws://localhost:8000/ws/doctor-status/` - Doctor status updates
- `ws://localhost:8000/ws/notifications/` - Real-time notifications
- `ws://localhost:8000/ws/consultations/` - Consultation updates

## Installation

### 1. Install Dependencies

```bash
pip install channels==4.0.0 channels-redis==4.1.0 daphne==4.0.0 redis==5.0.1
```

### 2. Start Redis

```bash
# Using Docker
docker-compose -f docker-compose.redis.yml up -d

# Or install Redis locally
sudo apt-get install redis-server
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Doctor Status Records

```bash
python manage.py create_doctor_statuses
```

### 5. Deploy WebSocket

```bash
./deploy_websocket.sh
```

## Usage

### Starting the Server

#### Development
```bash
python manage.py runserver
```

#### Production
```bash
daphne -b 0.0.0.0 -p 8000 myproject.asgi:application
```

### WebSocket Connection

#### JavaScript Client Example

```javascript
// Connect to doctor status WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/doctor-status/?token=YOUR_JWT_TOKEN');

socket.onopen = function(event) {
    console.log('WebSocket connected');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'initial_status':
            console.log('Initial doctor statuses:', data.data);
            break;
        case 'status_update':
            console.log('Doctor status updated:', data.data);
            break;
        case 'pong':
            console.log('Ping response received');
            break;
    }
};

socket.onclose = function(event) {
    console.log('WebSocket disconnected');
};

// Send ping to keep connection alive
setInterval(() => {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000);

// Update doctor status (for doctors only)
function updateStatus(status, note = '') {
    socket.send(JSON.stringify({
        type: 'status_update',
        data: {
            current_status: status,
            status_note: note,
            is_available: true
        }
    }));
}
```

#### Python Client Example

```python
import asyncio
import websockets
import json

async def connect_websocket():
    uri = "ws://localhost:8000/ws/doctor-status/?token=YOUR_JWT_TOKEN"
    
    async with websockets.connect(uri) as websocket:
        # Send ping
        await websocket.send(json.dumps({"type": "ping"}))
        
        # Listen for messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(connect_websocket())
```

## API Integration

### Broadcasting Updates

The backend automatically broadcasts updates when:

1. **Doctor Status Changes**: When a doctor updates their status via API or WebSocket
2. **Consultation Updates**: When consultation status changes
3. **Notifications**: When new notifications are created

### Manual Broadcasting

```python
from doctors.views import broadcast_doctor_status_update, broadcast_notification

# Broadcast doctor status update
broadcast_doctor_status_update(status_data)

# Broadcast notification to specific user
broadcast_notification(user_id, notification_data)
```

## Configuration

### Settings

The WebSocket configuration is in `settings.py`:

```python
# WebSocket Configuration
ASGI_APPLICATION = 'myproject.asgi.application'

# Channel Layers for WebSocket
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### Environment Variables

```bash
# Redis configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password  # Optional

# WebSocket settings
WEBSOCKET_ENABLED=true
WEBSOCKET_HEARTBEAT_INTERVAL=30
```

## Security

### Authentication

WebSocket connections are authenticated using JWT tokens passed as query parameters:

```
ws://localhost:8000/ws/doctor-status/?token=YOUR_JWT_TOKEN
```

### Authorization

- **Doctor Status**: Only authenticated users with admin/superadmin roles or doctor profiles can access
- **Notifications**: Users can only access their own notifications
- **Consultations**: All authenticated users can access consultation updates

## Monitoring

### Logging

WebSocket events are logged with the following levels:
- `INFO`: Connection/disconnection events
- `ERROR`: Authentication failures and processing errors
- `DEBUG`: Message processing details

### Health Checks

```bash
# Check Redis connection
redis-cli ping

# Check WebSocket endpoint
curl -I http://localhost:8000/ws/doctor-status/

# Monitor WebSocket connections
redis-cli monitor
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check if Redis is running
   docker ps | grep redis
   
   # Restart Redis
   docker-compose -f docker-compose.redis.yml restart
   ```

2. **WebSocket Connection Refused**
   ```bash
   # Check if server is running with ASGI
   ps aux | grep daphne
   
   # Restart server with ASGI
   daphne -b 0.0.0.0 -p 8000 myproject.asgi:application
   ```

3. **Authentication Failed**
   - Ensure JWT token is valid and not expired
   - Check if user has appropriate permissions
   - Verify token format in WebSocket URL

### Debug Mode

Enable debug logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'websockets': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Performance

### Optimization Tips

1. **Connection Pooling**: Use connection pooling for Redis
2. **Message Batching**: Batch multiple updates when possible
3. **Heartbeat Management**: Implement proper heartbeat mechanisms
4. **Load Balancing**: Use multiple Redis instances for high traffic

### Scaling

For production scaling:

1. **Multiple Redis Instances**: Use Redis Cluster
2. **Load Balancer**: Use nginx or haproxy for WebSocket load balancing
3. **Horizontal Scaling**: Deploy multiple Daphne instances
4. **Monitoring**: Use tools like Prometheus and Grafana

## Testing

### Unit Tests

```bash
python manage.py test websockets.tests
```

### Integration Tests

```bash
# Test WebSocket connection
python -m pytest tests/test_websockets.py

# Test with real client
python tests/websocket_client_test.py
```

## Deployment

### Production Checklist

- [ ] Redis is properly configured and secured
- [ ] JWT tokens are properly validated
- [ ] WebSocket endpoints are behind SSL/TLS
- [ ] Rate limiting is implemented
- [ ] Monitoring and logging are configured
- [ ] Backup strategy for Redis data
- [ ] Load balancing is configured
- [ ] Health checks are implemented

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or use the provided script
./deploy_websocket.sh
```

## Support

For issues and questions:

1. Check the logs: `tail -f logs/websocket.log`
2. Review this documentation
3. Check the Django Channels documentation
4. Contact the development team

## Changelog

### v1.0.0 (Current)
- Initial WebSocket implementation
- Doctor status real-time updates
- Notification broadcasting
- Consultation updates
- JWT authentication
- Redis channel layers
- Custom middleware
- Management commands
- Deployment scripts 