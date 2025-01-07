from django.urls import re_path
from live_feed_app import consumers

websocket_urlpatterns = [
    re_path(r'ws/live/(?P<stream_id>\w+)/$', consumers.LiveStreamConsumer.as_asgi()),
]
