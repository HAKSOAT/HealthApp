from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_404_NOT_FOUND
from drf_yasg.utils import swagger_auto_schema

from healthcentre.serializer import (
    PingViewsetSerializer
)
from students.serializer import StudentSerializer
from utils.helpers import format_response
from utils.pagination import StandardPagination
from students.models import Ping, Student
from utils.filters import filter_student


class StudentView(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """ View for student's information """
    serializer_class = StudentSerializer
    pagination_class = StandardPagination()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.none()

    def paginator(self):
        return self.pagination_class

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

    def list(self, request):
        query = request.query_params.get('query')
        search_fields = ["first_name", "last_name",
                         "matric_number", "clinic_number"]
        if query:
            students = filter_student(*search_fields, query=query)
        else:
            students = Student.objects.all()
        paginated_students = self.pagination_class.paginate_queryset(
            queryset=students, request=request
        )
        serializer = self.serializer_class(paginated_students, many=True)
        response = self.pagination_class.get_paginated_response(
            serializer.data,
            'Successfully retrieved students'
        )
        return response


class PingViewset(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """ Viewset for Pings """
    serializer_class = PingViewsetSerializer
    pagination_class = StandardPagination()

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Student.objects.none()

    def paginator(self):
        return self.pagination_class

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
        student_id = request.query_params.get('student', None)

        if student_id:
            pings = Ping.objects.filter(student__id=student_id)
        else:
            pings = Ping.objects.all()
        paginated_pings = self.pagination_class.paginate_queryset(
            queryset=pings, request=request
        )
        serializer = self.serializer_class(paginated_pings, many=True)
        response = self.pagination_class.get_paginated_response(
            serializer.data,
            'Successfully retrieved pings'
        )
        return response


class StatisticsView(mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """ Viewset for statistics """

    @swagger_auto_schema(operation_description='Views statistics')
    def list(self, request):
        statistics = {
            'pings': Ping.objects.count(),
            'replied_pings': 0,
            'video_calls': 0,
            'students': Student.objects.count()
        }
        return format_response(data=statistics,
                               message='Statistics retrieved.')
