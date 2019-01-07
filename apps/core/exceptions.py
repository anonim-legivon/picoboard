from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc, 'default_code'):
            response.data['code'] = exc.default_code

    return response
