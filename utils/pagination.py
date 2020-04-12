from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 30
    invalid_page_message = 'Page does not exist'

    def get_paginated_response(self, data, message=None):
        paginated_response = {
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        }

        if message:
            paginated_response['message'] = message

        return Response(paginated_response)
