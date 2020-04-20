import jwt

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header)

from students.models import Student
from healthcentre.models import Worker, IoT


class JSONWebTokenAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        token = get_authorization_header(request).decode().split()

        if self.keyword not in token:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Bearer String Not Set'})

        try:
            payload = jwt.decode(
                token[1], settings.SECRET_KEY, algorithms=['HS256'])
            user = Student.objects.get_all().filter(
                id=payload['uid']).first() or Worker.objects.filter(
                id=payload['uid']).first()
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Cannot validate your access credentials'})
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Session has expired. Kindly login again.'})

        if not user:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Cannot validate your access credentials'})

        if user._meta.object_name == Student._meta.object_name:
            if not user.is_confirmed:
                raise exceptions.AuthenticationFailed(
                    {'error': 'Authentication Failed',
                     'message': 'Account is not yet confirmed'})

        return user, payload


class APIKeyAuthentication(BaseAuthentication):
    keyword = 'Api-Key'

    def authenticate(self, request):

        token = get_authorization_header(request).decode().split()
        if self.keyword not in token:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Api-Key String Not Set'})

        iot = IoT.objects.filter(api_key=token[1]).first()
        if not iot:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Invalid Api-Key'})

        payload = None
        return iot, payload