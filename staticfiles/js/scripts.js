document.addEventListener('DOMContentLoaded', () => {
    const broadcastButton = document.getElementById('broadcastButton');
    const video = document.getElementById('preview');
    const streamsDiv = document.getElementById('streams');

    let isLive = false; // Track live status
    let streamId = null; // Current Stream ID
    let websocket = null; // WebSocket object
    let frameInterval = null; // Interval for sending frames

    // Initialize WebSocket connection
    const initializeWebSocket = (streamId) => {
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const websocketUrl = `${protocol}${window.location.host}/ws/live/${streamId}/`;
        websocket = new WebSocket(websocketUrl);

        websocket.onopen = () => {
            console.log('WebSocket connection established.');
            startFrameTransmission();
        };

        websocket.onclose = () => {
            console.log('WebSocket connection closed.');
            stopBroadcast();
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            alert('WebSocket connection failed. Please check the server.');
            stopBroadcast();
        };
    };

    // Start video frame transmission
    const startFrameTransmission = () => {
        frameInterval = setInterval(() => {
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                sendFrame();
            }
        }, 33); // Send frames at ~30 FPS
    };

    // Stop video frame transmission
    const stopFrameTransmission = () => {
        if (frameInterval) {
            clearInterval(frameInterval);
            frameInterval = null;
        }
    };

    // Capture and send video frame
    const sendFrame = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const base64Data = canvas.toDataURL('image/webp'); // Encode frame as WebP
        websocket.send(JSON.stringify({ frame: base64Data })); // Send frame
    };

    // Start broadcast
    const startBroadcast = async (streamId) => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            video.style.display = 'block';
            video.play();

            const response = await fetch('/broadcast/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stream_id: streamId }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to start broadcast.');
            }

            initializeWebSocket(streamId);
            isLive = true;
            broadcastButton.textContent = 'Stop Live';
        } catch (error) {
            console.error('Error starting broadcast:', error);
            alert(error.message);
        }
    };

    // Stop broadcast
    const stopBroadcast = () => {
        console.log('Stopping broadcast...');
        if (websocket) {
            websocket.close();
            websocket = null;
        }
        stopFrameTransmission();

        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }

        video.style.display = 'none';
        isLive = false;
        broadcastButton.textContent = 'Go Live';
        alert('Broadcast stopped successfully.');
    };

    // Fetch and display active streams
    const loadActiveStreams = async () => {
        try {
            const response = await fetch('/streams/');
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            const data = await response.text();
            streamsDiv.innerHTML = data;

            const streamLinks = streamsDiv.querySelectorAll('.stream-link');
            streamLinks.forEach(link => {
                link.addEventListener('click', (event) => {
                    const streamId = event.target.dataset.streamId;
                    window.location.href = `/watch_stream/${streamId}/`;
                });
            });
        } catch (error) {
            console.error('Error fetching streams:', error);
            streamsDiv.innerHTML = '<p class="error">Failed to load streams. Please try again later.</p>';
        }
    };

    // Toggle broadcast on button click
    if (broadcastButton) {
        broadcastButton.addEventListener('click', () => {
            if (!isLive) {
                streamId = prompt('Enter a unique Stream ID:');
                if (!/^[a-zA-Z0-9_-]+$/.test(streamId)) {
                    alert('Stream ID can only contain alphanumeric characters, dashes, and underscores.');
                    return;
                }
                startBroadcast(streamId);
            } else {
                stopBroadcast();
            }
        });
    }

    // Load streams on page load
    if (streamsDiv) {
        loadActiveStreams();
    }
});
