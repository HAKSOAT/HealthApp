def add_header(get_response):
    def middleware(request):
        # Django uses this header to generate https urls
        request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
        response = get_response(request)
        return response
    return middleware
