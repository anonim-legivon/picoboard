from rest_framework.views import exception_handler

from board.exceptions import UserBannedError


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc, 'default_code'):
            response.data['code'] = exc.default_code

        if isinstance(exc, UserBannedError):
            response.data['reason'] = exc.reason
            response.data['until'] = exc.until

    return response
