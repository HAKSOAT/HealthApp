from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import exception_handler


def format_response(**kwargs):
    ''' Helper function to format response '''
    if kwargs.get('error'):
        return Response({'success': kwargs.get('success', False), 'error': kwargs.get('error'), **kwargs},
                        status=kwargs.get('status', 400))

    return Response({'success': kwargs.get('success', True), **kwargs},
                    status=kwargs.get('status', 200))


def save_in_redis(key, data, timeout):
    """
        This function save in redis
        1. This function take three arguments: key,
            data to be saved and timeout value
        2. Save the data with {key} arg as the key in redis
    """
    cache.set(key, data, timeout=timeout)


def get_from_redis(key, default):
    """
        This function save in redis
        1. This function takes one argument: key
        2. Retrieves the data cached using key or None
    """
    return cache.get(key, default)


def delete_from_redis(key):
    """
        This function deletes from redis
        1. This function takes one argument: key
        2. Deletes the data cached using key
    """
    cache.delete(key)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['success'] = False
        error_detail = response.data.get('detail', None)
        if error_detail:
            response.data['message'] = error_detail
            del response.data['detail']
        response.data['status'] = response.status_code

    return response
