from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_404_NOT_FOUND
from drf_yasg.utils import swagger_auto_schema

from firstaid.serializer import FirstAidTipSerializer
from firstaid.models import Tip
from firstaid.utils.helpers import run_search
from utils.helpers import format_response


class FirstAidTipView(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """ View for first aid information """
    serializer_class = FirstAidTipSerializer
    permission_classes = ()

    def retrieve(self, request, pk):
        tip = Tip.objects.filter(id=pk).first()
        if not tip:
            return format_response(success=False,
                                   message='First aid tip not found',
                                   status=HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(tip)
        tip.views += 1
        tip.save()
        return format_response(data=serializer.data,
                               message='Successfully retrieved First aid tip')

    def list(self, request):
        if request.query_params:
            query = request.query_params.get('query', '')
            tips = run_search(query)
        else:
            tips = Tip.objects.all()
        serializer = self.serializer_class(tips, many=True)
        return format_response(data=serializer.data,
                               message='Successfully retrieved First aid tips')
