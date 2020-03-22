import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async

from students.models import Token


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        received_token = self.scope.get(
            'url_route', {}).get(
            'kwargs', {}).get(
            'token', None)

        token = await self.get_token(received_token)

        print(token)

        if token:
            await self.send(
                text_data=json.dumps(
                    {"message": 'Can\'t access'}
                ))

        self.group_name = 'healthcentre'

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def get_token(self, received_token):
        token = Token.objects.filter(**{
            'token': received_token,
            'is_blacklisted': False}).first()
        return token

    async def disconnect(self, code):
        received_token = self.scope.get(
            'url_route', {}).get(
            'kwargs', {}).get(
            'token', None)

        token = Token.objects.filter(
            token=received_token, is_blacklisted=False)

        if not token:
            await self.send(
                text_data=json.dumps(
                    {"message": 'Can\'t access'}
                ))

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_ping_notification(self, data):
        await self.send(text_data=json.dumps(data))
