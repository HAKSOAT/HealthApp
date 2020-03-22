import json
from asgiref.sync import async_to_sync

import channels.layers
from django.dispatch import receiver

from healthcentre.signals import ping_signal
from students.views import PingViewset


@receiver(ping_signal, sender=PingViewset)
def ping_receiver(sender, **kwargs):
    channel_layer = channels.layers.get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "healthcentre",
        {
            'type': 'send_ping_notification',
            'text': kwargs['ping_data']
        }
    )
