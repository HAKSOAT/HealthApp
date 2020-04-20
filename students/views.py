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
from utils.pagination import StandardPagination
from students.utils.generate import generate_otp
from students.models import Student, Token, Ping
from healthcentre.signals import ping_signal


class RegisterStudentViewset(viewsets.ViewSet):
    """ Viewset for student registration """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegisterStudentSerializer

    @swagger_auto_schema(request_body=RegisterStudentSerializer,
                         operation_description='Registers a student.\n\n'
                                               'Returns the <b>id</b> of the '
                                               'created user, to be used for'
                                               'confirmation purposes.')
    def create(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

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
    serializer_class = ConfirmStudentSerializer

    @swagger_auto_schema(request_body=ConfirmStudentSerializer,
                         operation_description=
                         'Confirms a student\'s account.\n\n'
                         'A request body with an <b>otp</b> key in it'
                         ' is needed to confirm an account.\n'
                         'Otherwise, it is not needed if the intention is '
                         'only to receive an OTP.'
                         )
    def partial_update(self, request, pk):
        data = request.data
        student = Student.objects.get_all().filter(id=pk).first()
        if not student:
            return format_response(error='Account does not exist',
                                   status=HTTP_400_BAD_REQUEST)

        if student.is_confirmed:
            return format_response(error='Account is already confirmed',
                                   status=HTTP_400_BAD_REQUEST)

        context = {'email': student.email}
        serializer = self.serializer_class(
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
    serializer_class = LoginSerializer

    @swagger_auto_schema(request_body=LoginSerializer,
                         operation_description='Logs in a user.\n\n'
                                               'For the healthcare admin, '
                                               'the <b>email</b> key should '
                                               'be the username.'
                         )
    def post(self, request):
        data = request.data
        context = {'user_type': request._request.path_info.split('/')[3]}
        serializer = self.serializer_class(data=data, context=context)
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

    @swagger_auto_schema(operation_description='Logs out the current user')
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

    @swagger_auto_schema(operation_description=
                         'Views the current student\'s profile')
    def get(self, request):
        student = request.user
        serializer = self.serializer_class(student)
        data = serializer.data
        return format_response(data=data,
                               message='Retrieved student details')

    @swagger_auto_schema(request_body=StudentSerializer,
                         operation_description=
                         'Updates the current student\'s profile.\n\n'
                         'To update password, provide the <b>password</b> and'
                         '<b>new_password</b> keys.')
    def patch(self, request):
        data = request.data
        student = request.user
        serializer = self.serializer_class(
            student, data=data,
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
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(request_body=ResetPasswordSerializer,
                         operation_description=
                         'Resets a student\'s password.\n\n'
                         'A request body is with <b>email</b> key only'
                         ' is needed to request an OTP.\n\n'
                         'Otherwise, the'
                         '<ul>'
                         '<li>email</li>'
                         '<li>otp</li>'
                         '<li>password</li>'
                         '<li>password_again</li>'
                         '</ul>\n\n'
                         'keys are required to reset the password.')
    def patch(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return format_response(
                error=serializer.errors.get('errors', serializer.errors),
                status=HTTP_400_BAD_REQUEST)
        student = Student.objects.get_all().filter(
            email=data.get('email')).first()
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
    serializer_class = PingViewsetSerializer
    pagination_class = StandardPagination()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.none()

    def paginator(self):
        return self.pagination_class

    @swagger_auto_schema(request_body=PingViewsetSerializer,
                         operation_description='Sends a ping.')
    def create(self, request):
        data = request.data
        student = request.user
        serializer = self.serializer_class(data=data,
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

    @swagger_auto_schema(operation_description='Views a ping')
    def retrieve(self, request, pk):
        student = request.user

        ping = Ping.objects.filter(id=pk, student__id=student.id).first()

        if not ping:
            return format_response(
                error='Ping not found',
                status=HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(ping)
        return format_response(data=serializer.data,
                               message='Successfully retrieved ping')

    @swagger_auto_schema(query_serializer=PingViewsetSerializer,
                         operation_description='Views all pings')
    def list(self, request):
        student = request.user
        pings = Ping.objects.filter(student__id=student.id)
        paginated_pings = self.pagination_class.paginate_queryset(
            queryset=pings, request=request
        )
        serializer = self.serializer_class(paginated_pings, many=True)
        response = self.pagination_class.get_paginated_response(
            serializer.data,
            'Successfully retrieved pings')
        return response
