import socket
from crypt import crypt

from django.conf import settings


def get_remote_ip(request) -> str:
    """
    Получаем из META ip адрес отправителя запроса
    :param request: Django request
    :return: ip адрес
    :rtype: str
    """
    x_forwarded_for: str = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip: str = x_forwarded_for.split(',')[0]
    else:
        ip: str = request.META.get('REMOTE_ADDR')

    return ip


def is_proxy_connect(host: str) -> bool:
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


def tripcode(uid: str) -> str:
    """
    Генератор трипкод по уникальному идентификатору
    :param str uid: Уникальный идентификатор
    :return: Трипкод
    :rtype: str
    """
    salt_table: str = (
        '................................'
        '.............../0123456789ABCDEF'
        'GABCDEFGHIJKLMNOPQRSTUVWXYZabcde'
        'fabcdefghijklmnopqrstuvwxyz.....'
        '................................'
        '................................'
        '................................'
        '................................'
    )

    salt: str = (uid + 'H..')[1:3].translate(salt_table)

    trip: str = crypt(uid, salt)[3:]

    return trip


def gen_tripcode(string: str, permit: bool) -> dict:
    """
    Генератор трипкодов
    :param str string: Имя#пароль
    :param bool permit: Разрешен ли трипкод на доске
    :return: Словарь с именем и трипкодом
    :rtype: dict
    """
    start: int = string.find('#')
    if start == -1 or not permit:
        return {
            'name': string,
            'trip': ''
        }

    trip_name: str = string[start:]
    main_name: str = string[:start]

    trip_name: str = tripcode(trip_name)

    return {
        'name': main_name,
        'trip': trip_name
    }


def require_trip(uid: str) -> str:
    return tripcode(uid)
