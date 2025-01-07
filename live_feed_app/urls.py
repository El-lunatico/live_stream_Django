from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('broadcast/', views.start_broadcast, name='start_broadcast'),
    path('streams/', views.get_streams, name='get_streams'),
    path('stop_broadcast/', views.stop_broadcast, name='stop_broadcast'),
    path('watch_stream/<str:stream_id>/', views.watch_stream, name='watch_stream'),
    path('stream/<str:stream_id>/', views.watch_stream, name='stream_video'),
]
