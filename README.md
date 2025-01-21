
# Django Video Streaming Application

## Overview

This application provides a platform for live video streaming, enabling users to broadcast their streams and view streams from other users. 
It uses Django for the backend and WebSocket communication for real-time updates.

---

## Features

- **Start Broadcasting**: Initiate a new video stream with a unique stream ID.
- **Stop Broadcasting**: End an active video stream.
- **View Streams**: Access and view active broadcasts in real-time.
- **Active Stream List**: Display a dynamic list of ongoing streams.
- **Responsive UI**: View streams seamlessly on mobile and desktop devices.
- **Secure Communication**: WebSocket connections are secured for data integrity.

---

## Requirements

- Python 3.8+
- Django 4.x
- SQLite (default) or another database supported by Django
- WebSocket-compatible server (e.g., Daphne or ASGI for Django Channels)

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # For Linux/MacOS
   venv\Scripts\activate     # For Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Usage

### Start a Broadcast
- Send a POST request to `/start_broadcast/` with a JSON payload:
  ```json
  {
    "stream_id": "unique_stream_id"
  }
  ```

### Stop a Broadcast
- Send a POST request to `/stop_broadcast/` with a JSON payload:
  ```json
  {
    "stream_id": "unique_stream_id"
  }
  ```

### View Active Streams
- Navigate to `/streams/` to see the list of active broadcasts.

---

## Folder Structure

- **`project_root/`**:
  - Contains Django settings and core configuration files.
- **`app/`**:
  - Main app handling video streaming logic.
- **`templates/`**:
  - HTML templates for stream viewing.
- **`static/`**:
  - Static assets such as CSS and JavaScript files.

---

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

---

## Troubleshooting

- If you encounter database errors, ensure migrations are applied with `python manage.py migrate`.
- For WebSocket connection issues, verify that a WebSocket-compatible server (like Daphne) is running.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Django Documentation: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- WebSocket Guides: [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
