from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from healthcentre import routing as hcrouting
from utils.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddleware(
        URLRouter(
            hcrouting.websocket_urls
        )
    )
})
