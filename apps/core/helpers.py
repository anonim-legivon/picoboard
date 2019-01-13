import socket
from crypt import crypt

from django.conf import settings


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


def is_proxy_connect(host):
    """
    Проверяем используется ли прокси
    Пытаемся подключиться к IP по сокетам используя порты из конфига
    :param str host: IP адрес
    :return: Идет ли запрос через прокси
    :rtype: bool
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        for port in settings.PROXY_PORTS:
            try:
                sock.connect((host, port))
            except ConnectionRefusedError:
                continue
            else:
                return True


def tripcode(uid):
    """
    Генератор трипкод по уникальному идентификатору
    :param str uid: Уникальный идентификатор
    :return: Трипкод
    :rtype: str
    """

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

    salt = (uid + 'H..')[1:3].translate(SALT)

    trip = crypt(uid, salt)[3:]

    return trip


def gen_tripcode(string, permit):
    """
    Генератор трипкодов
    :param str string: Имя#пароль
    :param bool permit: Разрешен ли трипкод на доске
    :return: Словарь с именем и трипкодом
    :rtype: dict
    """

    start = string.find('#')
    if start == -1 or not permit:
        return {
            'name': string,
            'trip': ''
        }

    trip_name = string[start:]
    main_name = string[:start]

    trip_name = tripcode(trip_name)

    return {
        'name': main_name,
        'trip': trip_name
    }


def require_trip(uid):
    return tripcode(uid)
