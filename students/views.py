import os

import jwt
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, \
    HTTP_404_NOT_FOUND
from django.core.mail import send_mail
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema

from config import settings
from students.serializer import (
    RegisterStudentSerializer,
    ConfirmStudentSerializer,
    LoginSerializer,
    StudentSerializer,
    ResetPasswordSerializer,
    PingViewsetSerializer
)
from utils.helpers import format_response, save_in_redis, get_from_redis, \
    delete_from_redis
from students.utils.generate import generate_otp
from students.models import Student, Token, Ping
from healthcentre.signals import ping_signal


class RegisterStudentViewset(viewsets.ViewSet):
    """ Viewset for student registration """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(request_body=RegisterStudentSerializer,
                         query_serializer=RegisterStudentSerializer)
    def create(self, request):
        data = request.data
        serializer = RegisterStudentSerializer(data=data)

        if not serializer.is_valid():
            return format_response(
                error=serializer.errors.get('errors', serializer.errors),
                status=HTTP_400_BAD_REQUEST)

        otp = generate_otp()
        save_in_redis(f'CONFIRM: {data["email"]}', otp, 60 * 4.9)
        send_mail(
            'Confirm HealthApp Account',
            'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
            os.getenv('HOST_EMAIL'),
            [data['email']],
            fail_silently=False
        )
        student = serializer.save()
        response_data = {'id': student.id}
        return format_response(
            data=response_data,
            message='Successfully created an account. '
                    'Check email to get OTP and proceed to confirm account.',
            status=HTTP_201_CREATED
        )


class ConfirmStudentViewset(viewsets.ViewSet):
    """ Viewset for student confirmation  """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(request_body=ConfirmStudentSerializer,
                         query_serializer=ConfirmStudentSerializer,
                         operation_description=
                         'Confirms a student\'s account. To request OTP, '
                         'the otp field is not needed. However, it is '
                         'needed to provide OTP for account confirmation.'
                         )
    def partial_update(self, request, pk):
        data = request.data
        student = Student.objects.filter(id=pk).first()
        if not student:
            return format_response(error='Account does not exist',
                                   status=HTTP_400_BAD_REQUEST)

        if student.is_confirmed:
            return format_response(error='Account is already confirmed',
                                   status=HTTP_400_BAD_REQUEST)

        context = {'email': student.email}
        serializer = ConfirmStudentSerializer(
            student, data=data, context=context)
        if not serializer.is_valid():
            return format_response(
                error=serializer.errors.get('errors', serializer.errors),
                status=HTTP_400_BAD_REQUEST)

        if not data.get('otp', None):
            otp = get_from_redis(f'CONFIRM: {student.email}', None)
            if otp:
                return format_response(
                    error='OTP already generated. Check your email.',
                    status=HTTP_400_BAD_REQUEST)
            otp = generate_otp()
            save_in_redis(f'CONFIRM: {student.email}', otp, 60 * 4.9)
            send_mail(
                'Confirm HealthApp Account',
                'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
                os.getenv('HOST_EMAIL'),
                [student.email],
                fail_silently=False
            )
            return format_response(
                message='Successfully generated Account Confirmation OTP')

        serializer.save()
        delete_from_redis(f'CONFIRM: {student.email}')
        return format_response(message='Successfully confirmed student')


class LoginView(APIView):
    """ Viewset for logging in """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(request_body=LoginSerializer,
                         query_serializer=LoginSerializer,
                         operation_description='Logs in a user'
                         )
    def post(self, request):
        data = request.data
        context = {'user_type': request._request.path_info.split('/')[3]}
        serializer = LoginSerializer(data=data, context=context)
        if not serializer.is_valid():
            return format_response(
                error=serializer.errors.get('errors', serializer.errors),
                status=HTTP_400_BAD_REQUEST)

        token = jwt.encode({
            'uid': serializer.validated_data['user'].id,
            'iat': settings.JWT_SETTINGS['ISS_AT'](),
            'exp': settings.JWT_SETTINGS['EXP_AT']()
        }, settings.SECRET_KEY)

        auth_data = {
            'user_id': serializer.validated_data['user'].id,
            'user_table': serializer.validated_data['user']._meta.object_name,
            'token': token.decode("utf-8"),
            'is_blacklisted': False
        }
        serializer.validated_data['user'].last_login = timezone.now()
        serializer.validated_data['user'].save()
        Token(**auth_data).save()
        return format_response(token=token,
                               message='Successfully logged in')


class LogoutView(APIView):
    """ View for user log out """
    permission_classes = ()

    def post(self, request):
        user = request.user
        token = request.headers["authorization"].split()[1]
        auth_data = {
            'user_id': user.id,
            'user_table': user._meta.object_name,
            'token': token,
            'is_blacklisted': False
        }
        listed_token = Token.objects.filter(**auth_data).first()
        if not listed_token:
            return format_response(error='User is already logged out',
                                   status=HTTP_400_BAD_REQUEST)

        listed_token.is_blacklisted = True
        listed_token.save()
        return format_response(message='Successfully logged out')


class StudentView(APIView):
    """ View for student's information """
    serializer_class = StudentSerializer

    def get(self, request):
        student = request.user
        serializer = self.serializer_class(student)
        data = serializer.data
        data.pop('password')
        return format_response(data=data,
                               message='Retrieved student details')

    @swagger_auto_schema(request_body=StudentSerializer,
                         query_serializer=StudentSerializer,
                         operation_description=
                         'Update student\'s values. To update password, '
                         'ensure the password and '
                         'new_password fields are filled.')
    def patch(self, request):
        data = request.data
        student = request.user
        serializer = self.serializer_class(student, data=data,
                                       partial=True, context={'id': student.id})

        if not serializer.is_valid():
            return format_response(error=serializer.errors.get('errors', serializer.errors),
                                   status=HTTP_400_BAD_REQUEST)

        serializer.save()
        if data.get('new_password', None):
            Token.objects.filter(user_id=student.id).update(is_blacklisted=True)
        return format_response(message='Successfully updated student')


class ResetPasswordView(APIView):
    """ View for resetting password """
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(request_body=ResetPasswordSerializer,
                         query_serializer=ResetPasswordSerializer,
                         operation_description=
                         'Reset student\'s password. To request OTP, ' 
                         'the otp field is not needed. However, it is ' 
                         'needed to provide OTP for password reset.')
    def patch(self, request):
        data = request.data
        serializer = ResetPasswordSerializer(data=data)
        if not serializer.is_valid():
            return format_response(
                error=serializer.errors.get('errors', serializer.errors),
                status=HTTP_400_BAD_REQUEST)
        print('HEre')
        student = Student.objects.filter(email=data.get('email')).first()
        if not student:
            return format_response(
                error='Account does not exist',
                status=HTTP_400_BAD_REQUEST)

        if not student.is_confirmed:
            return format_response(
                error='Account is not yet confirmed',
                status=HTTP_400_BAD_REQUEST)

        if not data.get('otp', None):
            otp = get_from_redis(f'RESET: {student.email}', None)
            if otp:
                return format_response(
                    error='OTP already generated. '
                          'Check email and specify otp key with its value',
                    status=HTTP_400_BAD_REQUEST)

            otp = generate_otp()
            send_mail(
                'Reset HealthApp Password',
                'The OTP code is {}.\n Valid for 5 minutes.'.format(otp),
                os.getenv('HOST_EMAIL'),
                [student.email],
                fail_silently=False
            )
            save_in_redis(f'RESET: {student.email}', otp, 60 * 4.9)
            return format_response(
                message='Successfully generated Password Reset OTP')

        serializer.update(student, serializer.data)
        Token.objects.filter(user_id=student.id).update(is_blacklisted=True)
        delete_from_redis(f'RESET: {student.email}')
        return format_response(message='Successfully reset password')


class PingViewset(viewsets.ViewSet):
    """ Viewset for Pings """

    @swagger_auto_schema(request_body=PingViewsetSerializer,
                         query_serializer=PingViewsetSerializer,
                         operation_description='Send a ping.')
    def create(self, request):
        data = request.data
        student = request.user
        serializer = PingViewsetSerializer(data=data,
                                           context={'id': student.id})
        if not serializer.is_valid():
            return format_response(
                error=serializer.errors.get('errors', serializer.errors),
                status=HTTP_400_BAD_REQUEST)
        serializer.save()
        ping_signal.send(sender=self.__class__, ping_data=serializer.data)
        return format_response(data=serializer.data,
                               message='Successfully sent a ping',
                               status=HTTP_201_CREATED)

    @swagger_auto_schema(query_serializer=PingViewsetSerializer,
                         operation_description='View a pin')
    def retrieve(self, request, pk):
        student = request.user

        ping = Ping.objects.filter(id=pk, student__id=student.id).first()

        if not ping:
            return format_response(
                error='Ping not found',
                status=HTTP_404_NOT_FOUND)

        serializer = PingViewsetSerializer(ping)
        return format_response(data=serializer.data,
                               message='Successfully retrieved ping')

    @swagger_auto_schema(query_serializer=PingViewsetSerializer,
                         operation_description='View all pings')
    def list(self, request):
        student = request.user

        pings = Ping.objects.filter(student__id=student.id)
        serializer = PingViewsetSerializer(pings, many=True)
        return format_response(data=serializer.data,
                               message='Successfully retrieved all Pings')
