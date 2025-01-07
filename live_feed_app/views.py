from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import cv2
import sqlite3

print("Views module loaded")


def create_db():
    """Create the database and table for storing active streams."""
    conn = sqlite3.connect('streams.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_streams (
            stream_id TEXT PRIMARY KEY,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_db()


def home(request):
    """Render the homepage."""
    return render(request, 'home.html')


@csrf_exempt
def start_broadcast(request):
    """Handle starting a new video broadcast."""
    if request.method == 'POST':
        print('start_broadcast endpoint hit')

        try:
            body = json.loads(request.body)
            stream_id = body.get('stream_id')
            
            # Validate Stream ID
            if not stream_id or not stream_id.isalnum():
                return JsonResponse({"message": "Invalid Stream ID. It must be alphanumeric."}, status=400)
            
            # Check for duplicate Stream ID in SQLite
            conn = sqlite3.connect('streams.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM active_streams WHERE stream_id = ?', (stream_id,))
            existing_stream = cursor.fetchone()
            conn.close()

            if existing_stream:
                return JsonResponse({"message": "Stream ID already exists."}, status=400)

            # Initialize VideoCapture for the new stream
            video_capture = cv2.VideoCapture(0)  # Use the default camera
            if not video_capture.isOpened():
                return JsonResponse({"message": "Failed to access webcam."}, status=500)
            
            # Insert the stream into the database
            conn = sqlite3.connect('streams.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO active_streams (stream_id, status) VALUES (?, ?)', (stream_id, 'active'))
            print(f"Stream added to DB: {stream_id}")
            conn.commit()
            conn.close()
            
            print("ACTIVE USERS ARE :", stream_id)
            return JsonResponse({"message": f"Broadcast '{stream_id}' started successfully."})
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data."}, status=400)
    elif request.method == 'GET':
        return render(request, 'broadcast.html')
    return JsonResponse({"message": "Invalid request method."}, status=405)

def get_streams(request):
    """Render the streams.html template with the list of active streams."""
    if request.method == 'GET':
        # Fetch active streams from the SQLite database
        conn = sqlite3.connect('streams.db')
        cursor = conn.cursor()
        cursor.execute('SELECT stream_id FROM active_streams WHERE status = "active"')
        active_streams = cursor.fetchall()
        conn.close()

        # Pass active streams to the template
        context = {"streams": [stream[0] for stream in active_streams]}  # Extract stream IDs
        return render(request, 'streams.html', context)
    return JsonResponse({"message": "Invalid request method."}, status=405)

@csrf_exempt
def stop_broadcast(request):
    """Handle stopping a video broadcast."""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            stream_id = body.get('stream_id')

            # Check if the stream exists in SQLite
            conn = sqlite3.connect('streams.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM active_streams WHERE stream_id = ?', (stream_id,))
            existing_stream = cursor.fetchone()

            if not existing_stream:
                return JsonResponse({"message": "Stream ID not found."}, status=404)

            # Update the stream status to inactive
            cursor.execute('UPDATE active_streams SET status = ? WHERE stream_id = ?', ('inactive', stream_id))
            conn.commit()
            conn.close()

            # Release the VideoCapture object (if needed)
            # video_capture = active_streams.pop(stream_id)
            # video_capture.release()
            
            return JsonResponse({"message": f"Broadcast '{stream_id}' stopped successfully."})
        
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON data."}, status=400)
    return JsonResponse({"message": "Invalid request method."}, status=405)

def watch_stream(request, stream_id):
    """Render video player or stream video frames."""
    # Check if the stream exists in SQLite
    conn = sqlite3.connect('streams.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM active_streams WHERE stream_id = ? AND status = "active"', (stream_id,))
    stream = cursor.fetchone()
    conn.close()

    if not stream:
        return JsonResponse({"message": "Stream not found."}, status=404)

    if request.method == 'GET':
        # Render the HTML page for watching the stream
        stream_url = f"ws://localhost:8000/ws/live/{stream_id}/"  # WebSocket URL
        return render(request, 'watch_stream.html', {"stream_id": stream_id, "stream_url": stream_url})


def gen_frames(video_capture):
    """Generate video frames for streaming."""
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error generating frames: {e}")
            break

import logging
logger = logging.getLogger(__name__)
