document.addEventListener('DOMContentLoaded', () => {
    const broadcastButton = document.getElementById('broadcastButton');
    const video = document.getElementById('preview');
    const streamsDiv = document.getElementById('streams');
    let isLive = false; // Track live status
    let streamId = null; // Track current Stream ID
    let websocket = null; // WebSocket object
    let frameInterval = null; // Interval for sending frames

    const startBroadcast = async (streamId) => {
        try {
            console.log('Requesting camera access...');
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            console.log('Camera access granted.');
    
            video.srcObject = stream;
            video.style.display = 'block';
            video.play();
    
            // Notify the server to start the broadcast
            const response = await fetch('/broadcast/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stream_id: streamId }),
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                alert(errorData.message || 'Failed to start broadcast.');
                return;
            }
    
            const responseData = await response.json();
            console.log('Backend response:', responseData);
    
            // Establish WebSocket connection immediately after backend setup
            websocket = new WebSocket(`ws://${window.location.host}/ws/live/${streamId}/`);
            
            websocket.onopen = () => {
                console.log('WebSocket connection established.');
                frameInterval = setInterval(() => sendFrame(stream, websocket), 33); // 30 FPS
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
    
            isLive = true;
            broadcastButton.textContent = 'Stop Live';
        } catch (error) {
            console.error('Error starting broadcast:', error);
            alert('Failed to start broadcast. Please try again.');
        }
    };

    const stopBroadcast = () => {
        console.log('Stopping broadcast...');
        if (websocket) {
            websocket.close();
            websocket = null;
        }
        if (frameInterval) {
            clearInterval(frameInterval);
            frameInterval = null;
        }
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
        video.style.display = 'none';
        isLive = false;
        broadcastButton.textContent = 'Go Live';
        alert('Broadcast stopped successfully.');
    };

    const sendFrame = (stream, websocket) => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(blob => {
            if (websocket.readyState === WebSocket.OPEN) {
                console.log('Sending frame with size:', blob.size);
                websocket.send(blob);
            }
        }, 'image/jpeg');
    };

    // Start or Stop Broadcast
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

    // Load Active Streams
    if (streamsDiv) {
        console.log('Fetching active streams...');
        fetch('/streams/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.text(); // Expecting HTML content
            })
            .then(data => {
                console.log('Active streams fetched successfully');
                streamsDiv.innerHTML = data; // Insert HTML directly
            })
            .catch(error => {
                console.error('Error fetching streams:', error);
                streamsDiv.innerHTML = '<p class="error">Failed to load streams. Please try again later.</p>';
            });
    }
});
