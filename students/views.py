import os

import jwt
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.core.mail import send_mail
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from config import settings
from students.serializer import (
    RegisterStudentSerializer,
    ConfirmStudentSerializer,
    LoginStudentSerializer,
    StudentSerializer,
    ResetPasswordSerializer,
    PingViewsetSerializer
)
from utils.helpers import format_response, save_in_redis, get_from_redis, delete_from_redis
from students.utils.generate import generate_otp
from students.models import Student, Token


class RegisterStudentViewset(viewsets.ViewSet):
    """ Viewset for student registration """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(query_serializer=RegisterStudentSerializer)
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
        save_in_redis(f'CONFIRM: {data["email"]}', otp, 60*5)
        return format_response(message='Successfully created an account. '
                                       'Check email to get OTP and proceed to confirm account.')


class ConfirmStudentViewset(viewsets.ViewSet):
    """ Viewset for student confirmation  """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(query_serializer=ConfirmStudentSerializer,
                         operation_description='Confirms a student\'s account. To request OTP, '
                                               'the otp field is not needed. However, it is '
                                               'needed to provide OTP for account confirmation.'
                         )
    def partial_update(self, request, pk):
        data = request.data
        student = Student.objects.filter(matric_number=pk).first()
        if not student:
            return format_response(error='Student does not have an account',
                                   status=HTTP_400_BAD_REQUEST)

        if student.is_confirmed:
            return format_response(error='Student\'s account is already confirmed',
                                   status=HTTP_400_BAD_REQUEST)

        context = {'email': student.email}
        serializer = ConfirmStudentSerializer(student, data=data, context=context)
        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        if not data.get('otp', None):
            otp = get_from_redis(f'CONFIRM: {student.email}')
            if otp:
                return format_response(error='OTP already generated. Check email and specify otp key with its value',
                                       status=HTTP_400_BAD_REQUEST)
            otp = generate_otp()
            save_in_redis(f'CONFIRM: {student.email}', otp, 60 * 5)
            send_mail(
                'Confirm HealthApp Account',
                'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
                os.getenv('HOST_EMAIL'),
                [student.email],
                fail_silently=False
            )
            return format_response(message='Successfully generated Account Confirmation OTP')

        serializer.save()
        delete_from_redis(f'CONFIRM: {student.email}')
        return format_response(message='Successfully confirmed student')


class LoginStudentView(APIView):
    """ Viewset for student logging in """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(query_serializer=LoginStudentSerializer,
                         operation_description='Logs in a student. '
                                               'Matric number or email are valid'
                         )
    def post(self, request):
        data = request.data
        serializer = LoginStudentSerializer(data=data)
        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        token = jwt.encode({
            'uid': serializer.validated_data['student'].id,
            'iat': settings.JWT_SETTINGS['ISS_AT'](),
            'exp': settings.JWT_SETTINGS['EXP_AT']()
        }, settings.SECRET_KEY)

        auth_data = {
            'student': serializer.validated_data['student'],
            'token': token.decode("utf-8"),
            'is_blacklisted': False
        }
        serializer.validated_data['student'].last_login = timezone.now()
        serializer.validated_data['student'].save()
        Token(**auth_data).save()
        return format_response(token=token,
                               message='Successfully logged in')


class LogoutStudentView(APIView):
    """ View for student log out """
    permission_classes = ()

    def post(self, request):
        user = request.user
        token = request.headers["authorization"].split()[1]
        auth_data = {
            'student': user,
            'token': token,
            'is_blacklisted': False
        }
        listed_token = Token.objects.filter(**auth_data).first()
        if not listed_token:
            return format_response(error='Student is already logged out',
                                   status=HTTP_400_BAD_REQUEST)

        listed_token.is_blacklisted = True
        listed_token.save()
        return format_response(message='Successfully logged out')


class StudentView(APIView):
    """ View for student's information """

    def get(self, request):
        student = request.user
        serialized_data = StudentSerializer(student)
        return format_response(data=serialized_data.data,
                               message='Retrieved student details')

    @swagger_auto_schema(query_serializer=StudentSerializer,
                         operation_description='Update student\'s values. To update password, '
                                               'ensure the new_password field is filled.')
    def patch(self, request):
        data = request.data
        student = request.user
        serializer = StudentSerializer(student, data=data,
                                       partial=True, context={'id': student.id})

        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        serializer.save()
        if data.get('new_password', None):
            Token.objects.filter(student=student).update(is_blacklisted=True)
        return format_response(message='Successfully updated student')


class ResetPasswordViewset(viewsets.ViewSet):
    """ View for resetting password """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(query_serializer=ResetPasswordSerializer,
                         operation_description='Reset student\'s password. To request OTP, '
                                               'the otp field is not needed. However, it is '
                                               'needed to provide OTP for password reset.')
    def partial_update(self, request, pk):
        data = request.data
        student = Student.objects.filter(matric_number=pk).first()
        if not student:
            return format_response(error='Student does not have an account',
                                   status=HTTP_400_BAD_REQUEST)

        if not student.is_confirmed:
            return format_response(error='Account is not yet confirmed',
                                   status=HTTP_400_BAD_REQUEST)

        context = {'email': student.email}
        serializer = ResetPasswordSerializer(student, data=data, context=context)
        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        if not data.get('otp', None):
            otp = get_from_redis(f'RESET: {student.email}')
            if otp:
                return format_response(error='OTP already generated. Check email and specify otp key with its value',
                                       status=HTTP_400_BAD_REQUEST)
            otp = generate_otp()
            save_in_redis(f'RESET: {student.email}', otp, 60 * 5)
            send_mail(
                'Reset HealthApp Password',
                'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
                os.getenv('HOST_EMAIL'),
                [student.email],
                fail_silently=False
            )
            return format_response(message='Successfully generated Password Reset OTP')

        serializer.save()
        Token.objects.filter(student=student).update(is_blacklisted=True)
        delete_from_redis(f'RESET: {student.email}')
        return format_response(message='Successfully reset password')


class PingViewset(viewsets.ViewSet):
    """ Viewset for Pings """

    @swagger_auto_schema(query_serializer=PingViewsetSerializer,
                         operation_description='Send a ping.')
    def create(self, request):
        data = request.data
        student = request.user
        serializer = PingViewsetSerializer(data=data, context={'id': student.id})
        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)
        serializer.save()
        return format_response(message='Successfully sent a ping')
