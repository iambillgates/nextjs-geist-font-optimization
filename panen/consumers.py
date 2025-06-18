import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Location, SensorData
from django.utils import timezone

class MonitoringConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is established
        """
        # Add the client to the monitoring group
        await self.channel_layer.group_add(
            "monitoring",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed
        """
        # Remove the client from the monitoring group
        await self.channel_layer.group_discard(
            "monitoring",
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when data is received from the WebSocket
        """
        try:
            data = json.loads(text_data)
            
            # Save sensor data to database
            if 'sensor_data' in data:
                await self.save_sensor_data(data['sensor_data'])
            
            # Broadcast the data to all connected clients
            await self.channel_layer.group_send(
                "monitoring",
                {
                    "type": "broadcast_sensor_data",
                    "data": data
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format"
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "error": str(e)
            }))

    async def broadcast_sensor_data(self, event):
        """
        Broadcasts sensor data to all connected clients
        """
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def save_sensor_data(self, sensor_data):
        """
        Saves sensor data to the database
        """
        try:
            location = Location.objects.get(id=sensor_data['location_id'])
            SensorData.objects.create(
                location=location,
                timestamp=timezone.now(),
                temperature=sensor_data['temperature'],
                humidity=sensor_data['humidity'],
                soil_moisture=sensor_data['soil_moisture'],
                light_intensity=sensor_data['light_intensity']
            )
        except Location.DoesNotExist:
            raise Exception("Invalid location ID")
        except KeyError as e:
            raise Exception(f"Missing required field: {str(e)}")

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when a WebSocket connection is established for alerts
        """
        await self.channel_layer.group_add(
            "alerts",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection for alerts is closed
        """
        await self.channel_layer.group_discard(
            "alerts",
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when alert data is received
        """
        try:
            data = json.loads(text_data)
            
            # Broadcast the alert to all connected clients
            await self.channel_layer.group_send(
                "alerts",
                {
                    "type": "broadcast_alert",
                    "data": data
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Invalid JSON format"
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                "error": str(e)
            }))

    async def broadcast_alert(self, event):
        """
        Broadcasts alerts to all connected clients
        """
        await self.send(text_data=json.dumps(event["data"]))

    @database_sync_to_async
    def check_alert_conditions(self, sensor_data):
        """
        Checks if sensor data should trigger any alerts
        """
        alerts = []
        
        # Temperature alert
        if sensor_data['temperature'] > 35:
            alerts.append({
                'type': 'temperature',
                'message': f"High temperature detected: {sensor_data['temperature']}°C",
                'severity': 'high'
            })
        
        # Humidity alert
        if sensor_data['humidity'] > 85:
            alerts.append({
                'type': 'humidity',
                'message': f"High humidity detected: {sensor_data['humidity']}%",
                'severity': 'medium'
            })
        
        # Soil moisture alert
        if sensor_data['soil_moisture'] < 30:
            alerts.append({
                'type': 'soil_moisture',
                'message': f"Low soil moisture detected: {sensor_data['soil_moisture']}%",
                'severity': 'high'
            })
        
        return alerts
