from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST

from students.serializer import RegisterStudentSerializer
from utils.helpers import format_response


class RegisterStudentViewset(viewsets.ViewSet):
    """Viewset for student registration"""
    def create(self, request):
        data = request.data
        serializer = RegisterStudentSerializer(data=data)

        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        serializer.save()
        return format_response(message='Successfully created an account')
