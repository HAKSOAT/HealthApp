from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_404_NOT_FOUND
from drf_yasg.utils import swagger_auto_schema

from healthcentre.serializer import (
    PingViewsetSerializer
)
from students.serializer import StudentSerializer
from utils.helpers import format_response, save_in_redis, get_from_redis
from students.models import Ping, Student
from utils.authentication import APIKeyAuthentication


class StudentView(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """ View for student's information """
    serializer_class = StudentSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.none()

    @swagger_auto_schema(
        operation_description='Views a student\'s profile')
    def retrieve(self, request, pk):
        student = Student.objects.filter(id=pk).first()
        if not student:
            return format_response(success=False,
                                   message='Student account does not exist',
                                   status=HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(student)
        data = serializer.data
        return format_response(data=data,
                               message='Successfully retrieved'
                                       ' student\'s profile')


class PingViewset(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """ Viewset for Pings """
    serializer_class = PingViewsetSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Ping.objects.none()

    @swagger_auto_schema(operation_description='Views a ping.')
    def retrieve(self, request, pk):
        Ping.objects.filter(id=pk).update(is_read=True)
        ping = Ping.objects.filter(id=pk).first()
        if not ping:
            return format_response(success=False,
                                   message='Ping does not exist',
                                   status=HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(ping)
        return format_response(data=serializer.data,
                               message='Successfully retrieved Ping')

    @swagger_auto_schema(operation_description='Views all pings')
    def list(self, request):
        data = request.data
        student_id = data.get('student', None)

        if student_id:
            pings = Ping.objects.filter(student__id=student_id)
        else:
            pings = Ping.objects.all()
        serializer = self.serializer_class(pings, many=True)
        return format_response(data=serializer.data,
                               message='Successfully retrieved all Pings')


class IoTPingViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (APIKeyAuthentication, )
    permission_classes = ()

    @swagger_auto_schema(auto_schema=None)
    def list(self, request):
        last_check = get_from_redis('IOT', timezone.now())
        ping = Ping.objects.filter(created_at__gt=last_check).first()
        save_in_redis('IOT', timezone.now(), 60 * 10)
        if ping:
            return format_response(message='New ping found')
        else:
            return format_response(success=False,
                                   message='No new ping found',
                                   status=HTTP_404_NOT_FOUND)


def ws_index(request):
    return format_response(message='Here')
