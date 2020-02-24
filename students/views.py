import os

from rest_framework import viewsets
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.mail import send_mail

from students.serializer import RegisterStudentSerializer
from utils.helpers import format_response
from students.utils.generate import generate_otp


class RegisterStudentViewset(viewsets.ViewSet):
    """Viewset for student registration"""
    def create(self, request):
        data = request.data
        serializer = RegisterStudentSerializer(data=data)

        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        serializer.save()
        otp = generate_otp()
        send_mail(
            'Confirm HealthApp Account',
            'The OTP code is {}'.format(otp),
            os.getenv('HOST_EMAIL'),
            [serializer.data['email']],
            fail_silently=False
        )
        return format_response(message='Successfully created an account')
