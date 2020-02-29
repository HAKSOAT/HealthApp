import os

import jwt
from rest_framework import viewsets, mixins
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.mail import send_mail

from config import settings
from students.serializer import (
    RegisterStudentSerializer,
    ConfirmStudentSerializer,
    LoginStudentSerializer
)
from utils.helpers import format_response, save_in_redis, get_from_redis
from students.utils.generate import generate_otp
from students.models import Student


class RegisterStudentViewset(viewsets.ViewSet):
    """ Viewset for student registration """
    permission_classes = ()
    authentication_classes = ()

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
            'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
            os.getenv('HOST_EMAIL'),
            [data['email']],
            fail_silently=False
        )
        save_in_redis(f'OTP: {data["email"]}', otp, 60*5)
        return format_response(message='Successfully created an account. '
                                       'Check email to get OTP and proceed to confirm account.')


class ConfirmStudentViewset(viewsets.ViewSet):
    """ Viewset for student confirmation """
    permission_classes = ()
    authentication_classes = ()

    def partial_update(self, request, pk):
        data = request.data
        student = Student.objects.filter(matric_number=pk).first()
        if not student:
            return format_response(error='Student does not have an account',
                                   status=HTTP_400_BAD_REQUEST)

        serializer = ConfirmStudentSerializer(student, data=data)
        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        if student.email != data['email']:
            return format_response(error='Student\'s matric number and email do not match',
                                   status=HTTP_400_BAD_REQUEST)

        if data.get('new_otp', None):
            otp = get_from_redis(f'OTP: {data["email"]}')
            if otp:
                return format_response(error='OTP already generated. Check email.',
                                       status=HTTP_400_BAD_REQUEST)
            otp = generate_otp()
            save_in_redis(f'OTP: {data["email"]}', otp, 60 * 5)
            send_mail(
                'Confirm HealthApp Account',
                'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
                os.getenv('HOST_EMAIL'),
                [data['email']],
                fail_silently=False
            )
            return format_response(message='Successfully generated new OTP')

        serializer.save()
        return format_response(message='Successfully confirmed student')


class LoginStudentViewset(viewsets.ViewSet):
    """ Viewset for student logging in """
    permission_classes = ()
    authentication_classes = ()

    def create(self, request):
        data = request.data
        serializer = LoginStudentSerializer(data=data)
        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        print(serializer.__dict__)
        token = jwt.encode({
            'uid': serializer.validated_data['user_id'],
            'iat': settings.JWT_SETTINGS['ISS_AT'](),
            'exp': settings.JWT_SETTINGS['EXP_AT']()
        }, settings.SECRET_KEY)

        return format_response(token=token,
                               message='Successfully logged in')
