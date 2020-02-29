from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from students.models import BlackListedToken


class IsTokenBlackListed(permissions.BasePermission):
    def has_permission(self, request, view):
        student_id = request.user.id
        token = request.headers["authorization"].split()[1]

        is_blacklisted_token = BlackListedToken.objects.filter(
                student=student_id, token=token).first()

        if is_blacklisted_token:
            raise exceptions.PermissionDenied(
                {'success': False,
                 'error': 'Session has expired. Please login again.',
                 'status': HTTP_400_BAD_REQUEST})

        return True
