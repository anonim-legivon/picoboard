from crypt import crypt


def get_remote_ip(request):
    """
    Получаем из META ip адрес отправителя запроса
    :param request: Django request
    :return: ip адрес
    :rtype: str
    """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def gen_tripcode(trip, permit):
    """
    Генератор трипкодов
    :param str trip: Имя#пароль
    :param bool permit: Разрешен ли трипкод на доске
    :return: Словарь с именем и трипкодом
    :rtype: dict
    """

    start = trip.find('#')
    if start == -1 or not permit:
        return {
            'name': '',
            'trip': ''
        }

    trip_name = trip[start:]
    main_name = trip[:start]

    SALT = (
        '................................'
        '.............../0123456789ABCDEF'
        'GABCDEFGHIJKLMNOPQRSTUVWXYZabcde'
        'fabcdefghijklmnopqrstuvwxyz.....'
        '................................'
        '................................'
        '................................'
        '................................'
    )

    salt = (trip_name + 'H..')[1:3].translate(SALT)

    trip_name = crypt(trip_name, salt)[3:]

    return {
        'name': main_name,
        'trip': trip_name
    }
