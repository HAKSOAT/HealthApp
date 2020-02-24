from rest_framework.response import Response


def format_response(**kwargs):
    ''' Helper function to format response '''
    if kwargs.get('error'):
        return Response({'success': kwargs.get('success', False), 'error': kwargs.get('error'), **kwargs},
                        status=kwargs.get('status', 400))

    return Response({'success': kwargs.get('success', True), **kwargs},
                    status=kwargs.get('status', 200))
