from django.urls import path

from healthcentre import consumers

websocket_urls = [
    path(r'ws/pings', consumers.ChatConsumer)
]