import jwt

from channels.db import database_sync_to_async
from django.conf import settings

from students.models import Student
from healthcentre.models import Worker


def add_header(get_response):
    def middleware(request):
        # Django uses this header to generate https urls
        request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
        response = get_response(request)
        return response
    return middleware


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        if b'sec-websocket-protocol' in headers:
            try:
                token = headers[b'sec-websocket-protocol']
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=['HS256'])

                user = self.get_user(payload['uid'])
                scope['user'] = user
            except:
                scope['error'] = 'Invalid token'
        return self.inner(scope)

    @database_sync_to_async
    def get_user(self, uid):
        user = Student.objects.get_all().filter(
            id=uid).first() or Worker.objects.filter(
            id=uid).first()
        return user


