import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from students.models import Student, Ping
from students.utils.enums import PingStatuses
from healthcentre.models import Worker


class PingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'healthcentre'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_ping_notification(self, data):
        await self.send(text_data=json.dumps(data))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        ping_attrs = await self.get_ping_attributes(['id', 'student'])

        if ping_attrs is None:
            return None

        group_name = await self.set_group_name(ping_attrs[0])
        if group_name is None:
            return None

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        try:
            await self.accept(self.scope['subprotocols'][0])
        except:
            await self.close()

    async def disconnect(self, code):
        if 'group_name' in self.__dict__.keys():
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

        await self.close(code)

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            text_data_json = {'error': 'Only json format supported'}

        status = text_data_json.get('status', None)
        if status:
            is_status_set = await self.set_status(status)
            if is_status_set is False:
                return None

        await self.channel_layer.group_send(
            self.destination_group_name,
            {
                'type': 'send_message',
                **text_data_json
            }
        )

    async def set_status(self, status):
        try:
            await self.check_status_validity(status)
            filter_n_values = {'filters': {'id': self.ping_id},
                               'values': {
                                   'status': PingStatuses[status].value}
                               }
            await self.set_db_object_attributes(Ping, filter_n_values)
            message = {'message': f'Status `{status}` is set successfully'}

        except (KeyError, AssertionError):
            message = {'error': f'status `{status}` can\'t be set'}

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_message',
                **message
            }
        )

        if message.get('error', None):
            return False
        else:
            return True

    async def check_status_validity(self, status):
        # A ping's status should not be changeable once out of pending state
        ping_attrs = await self.get_db_object_attributes(
            Ping, ['status'], id=self.ping_id)
        assert ping_attrs[0]['status'] == PingStatuses.pending.value

        if self.user._meta.object_name == Student._meta.object_name:
            assert status == PingStatuses.ignored.value
        elif self.user._meta.object_name == Worker._meta.object_name:
            assert status == PingStatuses.accepted.value

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def get_ping_attributes(self, attrs):
        self.ping_id = self.scope.get(
            'url_route', {}).get(
            'kwargs', {}).get(
            'ping_id', None)
        ping_attrs = await self.get_db_object_attributes(
            Ping, attrs, id=self.ping_id)
        if not ping_attrs:
            message = 'Ping does not exist'
            ping_attrs = await self.error_disconnect(message)

        return ping_attrs

    @staticmethod
    @database_sync_to_async
    def get_db_object_attributes(model, attrs, **filters):
        return list(model.objects.filter(**filters).values(*attrs))

    @staticmethod
    @database_sync_to_async
    def set_db_object_attributes(model, filters_n_values):
        filters = filters_n_values.get('filters', {})
        values = filters_n_values.get('values', {})
        model.objects.filter(**filters).update(**values)

    async def set_group_name(self, ping_attrs):
        try:
            self.user = await self.scope['user']
            if self.user._meta.object_name == Student._meta.object_name:
                self.group_name = f'{ping_attrs["id"]}'
                self.destination_group_name = f'healthcentre-{ping_attrs["id"]}'
                assert self.user.id == ping_attrs["student"]

            elif self.user._meta.object_name == Worker._meta.object_name:
                self.group_name = f'healthcentre-{ping_attrs["id"]}'
                self.destination_group_name = f'{ping_attrs["id"]}'

            return self.group_name

        except (TypeError, KeyError, AssertionError) as error:
            if isinstance(error, AssertionError):
                message = "Unauthorized to access"
            else:
                message = self.scope.get('error', None)
            return await self.error_disconnect(message)

    async def error_disconnect(self, message):
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"message": message}
            ))
        await self.disconnect(None)
        return None
