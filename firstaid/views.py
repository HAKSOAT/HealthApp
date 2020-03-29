from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from drf_yasg.utils import swagger_auto_schema
from django.db.models import F

from firstaid.serializer import FirstAidTipSerializer
from firstaid.models import Tip
from firstaid.utils.helpers import run_search
from utils.helpers import format_response


class FirstAidTipView(viewsets.ViewSet):
    """ View for first aid information """
    serializer_class = FirstAidTipSerializer
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(operation_description='Views a first aid tip')
    def retrieve(self, request, pk):
        tip = Tip.objects.filter(id=pk).first()
        if not tip:
            return format_response(success=False,
                                   message='First aid tip not found',
                                   status=HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(tip)
        return format_response(data=serializer.data,
                               message='Successfully retrieved First aid tip')

    @swagger_auto_schema(operation_description='Increases view count '
                                               'for a First aid tip')
    def partial_update(self, request, pk):
        Tip.objects.filter(id=pk).update(views=F('views') + 1)
        tip = Tip.objects.filter(id=pk).first()
        if not tip:
            return format_response(success=False,
                                   message='First aid tip not found',
                                   status=HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(tip)
        return format_response(data=serializer.data, status=HTTP_200_OK)

    @swagger_auto_schema(operation_description='Views all first aid tips.\n\n'
                                               '\nCan also search for tips by'
                                               'providing a query parameter.\n'
                                               '\nLike: <b>/firstaid/tip?query=<search-query></b>')
    def list(self, request):
        if request.query_params:
            query = request.query_params.get('query', '')
            tips = run_search(query)
        else:
            tips = Tip.objects.all()
        serializer = self.serializer_class(tips, many=True)
        return format_response(data=serializer.data,
                               message='Successfully retrieved First aid tips')
