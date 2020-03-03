import jwt

from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header)
from students.models import Student


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
            student = Student.objects.filter(id=payload['uid']).first()
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Cannot validate your access credentials'})
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Token has expired'})

        if not student:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Cannot validate your access credentials'})

        if not student.is_confirmed:
            raise exceptions.AuthenticationFailed(
                {'error': 'Authentication Failed',
                 'message': 'Account is not yet confirmed'})

        return student, payload
