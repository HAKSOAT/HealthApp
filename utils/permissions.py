from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from utils.constants import student_base_url, health_centre_base_url
from students.models import Token, Student
from healthcentre.models import Worker


class IsTokenBlackListed(permissions.BasePermission):
    def has_permission(self, request, view):
        student = request.user
        token = request.headers["authorization"].split()[1]

        is_blacklisted_token = Token.objects.filter(
                user_id=student.id, token=token, is_blacklisted=True).first()

        if is_blacklisted_token:
            raise exceptions.PermissionDenied(
                {'success': False,
                 'error': 'Session has expired. Please login again.',
                 'status': HTTP_400_BAD_REQUEST})

        return True


class HasSufficientPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        path_info = request._request.path_info

        if user._meta.object_name == Worker._meta.object_name:
            if not path_info.startswith('/' + health_centre_base_url):
                raise exceptions.PermissionDenied(
                    {'success': False,
                     'error': 'Only Health Centre workers can access',
                     'status': HTTP_403_FORBIDDEN})

        elif user._meta.object_name == Student._meta.object_name:
            if not path_info.startswith('/' + student_base_url):
                raise exceptions.PermissionDenied(
                    {'success': False,
                     'error': 'Only students can access',
                     'status': HTTP_403_FORBIDDEN})

        return True
