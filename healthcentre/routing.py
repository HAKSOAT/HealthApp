from django.urls import re_path

from healthcentre import consumers

websocket_urls = [
    re_path(r'ws/pings', consumers.PingConsumer),
    re_path(r'ws/chat/(?P<ping_id>\w+)', consumers.ChatConsumer)
]