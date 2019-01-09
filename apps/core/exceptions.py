from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if hasattr(exc, 'default_code'):
            response.data['code'] = exc.default_code

        # FIXME: Какая-то ебанина с isinstance(exc, UserBannedError)
        #        надо проверить
            if exc.default_code == 'user_banned_error':
                response.data['reason'] = exc.reason
                response.data['until'] = exc.until

    return response
