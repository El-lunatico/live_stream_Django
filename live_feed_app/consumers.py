import logging
import sqlite3
import asyncio
import cv2
import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import numpy as np

logger = logging.getLogger(__name__)


class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        logger.info(f"WebSocket connection attempt for stream ID: {self.stream_id}")

        # Validate stream ID
        if not self.validate_stream(self.stream_id):
            logger.warning(f"Invalid or inactive stream ID: {self.stream_id}")
            await self.close()
            return

        self.room_group_name = f"live_stream_{self.stream_id}"

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"WebSocket connected to {self.room_group_name}")

        except Exception as e:
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected from {self.room_group_name}")
        except Exception as e:
            logger.error(f"Error during WebSocket disconnection: {e}")

    async def receive(self, text_data=None, bytes_data=None):
        logger.info(f"Received message: {text_data if text_data else '[binary data]'}")
        try:
            if text_data:
                data = json.loads(text_data)
                frame_data = data.get('frame')  # Assuming frame is sent as base64

                if frame_data:
                    # Log frame metadata
                    logger.debug(f"Frame data length: {len(frame_data)}")
                    frame_bytes = base64.b64decode(frame_data.split(',')[1])
                    np_array = np.frombuffer(frame_bytes, dtype=np.uint8)
                    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

                    if frame is not None:
                        logger.debug(f"Frame received with shape: {frame.shape}")
                    else:
                        logger.warning("Received frame is None or failed to decode.")

                    # Optional: Show frame locally for debugging
                    cv2.imshow('Received Frame', frame)
                    cv2.waitKey(1)

                    # Send the frame to other clients in the same stream group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'send_frame',
                            'frame': frame_data,  # Send the frame data back as base64
                        }
                    )
            else:
                logger.warning("No text data received.")
        except Exception as e:
            logger.error(f"Error processing frame: {e}")

    async def send_frame(self, event):
        frame_data = event['frame']
        logger.debug(f"Sending frame to WebSocket: {len(frame_data)} bytes")
        await self.send(text_data=json.dumps({
            'frame': frame_data  # Send the base64 encoded frame
        }))

    def validate_stream(self, stream_id):
        """Check if the stream ID exists and is active in the database."""
        try:
            conn = sqlite3.connect('streams.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM active_streams WHERE stream_id = ? AND status = "active"', (stream_id,))
            stream = cursor.fetchone()
            conn.close()
            logger.debug(f"Validation result for stream_id {stream_id}: {'Exists' if stream else 'Does not exist'}")
            return bool(stream)
        except sqlite3.Error as e:
            logger.error(f"Database error during validation: {e}")
            return False
