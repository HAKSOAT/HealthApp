from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.response import Response
from students.models import BlackListedToken


class IsTokenBlackListed(permissions.BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id
        is_allowed_user = True
        token = "".join(request.headers["authorization"].split())[6:]
        try:
            is_blacklisted_token = BlackListedToken.objects.get(
                user=user_id, token=token)

            if is_blacklisted_token:
                is_allowed_user = False
                raise exceptions.PermissionDenied(
                    {'error': 'You do not have permission to perform this action.',
                     'message': 'Session has expired. Please login again.'})
        except BlackListedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user
