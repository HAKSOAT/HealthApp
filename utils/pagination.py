from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from utils.helpers import format_response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 30
    invalid_page_message = 'Page does not exist'

    def get_paginated_response(self, data, message=None):
        next_link = 1
        meta_data = {
            'links': {
                'next': self.get_next_link(), #.replace('http://', 'https://'),
                'previous': self.get_previous_link()#.replace('http://', 'https://')
            },
            'count': self.page.paginator.count,
        }

        if message:
            return format_response(meta_data=meta_data,
                                   data=data,
                                   message=message)
        else:
            return format_response(meta_data=meta_data,
                                   data=data)
