import cv2
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
import sqlite3
import asyncio

logger = logging.getLogger(__name__)

class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        logger.info(f"Attempting WebSocket connection for stream ID: {self.stream_id}")
        
        # Validate stream ID in SQLite database
        conn = sqlite3.connect('streams.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM active_streams WHERE stream_id = ? AND status = "active"', (self.stream_id,))
        stream = cursor.fetchone()
        conn.close()
        
        if not stream:
            logger.warning(f"Stream ID {self.stream_id} not found in active_streams.")
            await self.close()
            return
        
        self.room_group_name = f"live_stream_{self.stream_id}"
        
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket connected to room: {self.room_group_name}")
        except Exception as e:
            logger.error(f"Error adding WebSocket to group: {e}")
            await self.close()
            return
        
        await self.accept()

        # Start sending video frames after connection is established
        asyncio.ensure_future(self.send_video_stream())

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(f"WebSocket disconnected from room: {self.room_group_name}")
            except Exception as e:
                logger.error(f"Error discarding WebSocket from group: {e}")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            logger.info(f"Text message received on WebSocket: {text_data}")
            # Handle text messages here
        elif bytes_data is not None:
            logger.info(f"Binary data received on WebSocket: {len(bytes_data)} bytes")
            # Handle binary data here (if needed)
        else:
            logger.warning("Received a message with no text_data or bytes_data")

    async def send_frame(self, frame_data):
        """
        Sends a single video frame to the WebSocket.
        """
        try:
            await self.send(bytes_data=frame_data)  # Send binary data
        except Exception as e:
            logger.error(f"Error sending frame: {e}")

    async def send_video_stream(self):
        """
        Captures video frames and sends them over WebSocket.
        """
        video_capture = cv2.VideoCapture(0)  # Open the default camera
        if not video_capture.isOpened():
            logger.error("Unable to access the camera.")
            await self.close()
            return
        
        logger.info("Camera opened successfully. Starting video stream.")
        
        try:
            while True:
                success, frame = video_capture.read()
                if not success:
                    logger.error("Failed to capture frame from camera.")
                    break

                # Encode the frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                logger.info(f"Captured and sending frame of size: {len(frame_data)} bytes")
                
                # Send the frame
                await self.send_frame(frame_data)
                
                # Limit the frame rate (30 FPS)
                await asyncio.sleep(1 / 30)
        except Exception as e:
            logger.error(f"Error during video stream: {e}")
        finally:
            video_capture.release()  # Release the camera resource
            logger.info("Camera released and video stream ended.")
            await self.close()
