document.getElementById('startBroadcast')?.addEventListener('click', async () => {
    const streamId = prompt('Enter a stream ID:');
    if (streamId) {
        const video = document.getElementById('preview');
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;

        await fetch('/start_broadcast/', {
            method: 'POST',
            body: JSON.stringify({ stream_id: streamId }),
            headers: { 'Content-Type': 'application/json' },
        }).then(response => response.json())
          .then(data => alert(data.message));
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const streamsDiv = document.getElementById('streams');
    if (streamsDiv) {
        fetch('/get_streams/')
            .then(response => response.json())
            .then(data => {
                data.streams.forEach(stream => {
                    const video = document.createElement('video');
                    video.src = `/ws/live/${stream}/`;
                    video.controls = true;
                    video.autoplay = true;
                    streamsDiv.appendChild(video);
                });
            });
    }
});
