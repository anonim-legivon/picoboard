import random

from django.utils import timezone


def resolve_save_path(instance, filename):
    """
    Вычисляем путь для сохранения нового файла
    :param instance: Инстанс сохраняемого объекта
    :param str filename: Первоначальное имя файла
    :return: Путь для сохранения файла
    :rtype: str
    """
    thread: str = instance.post.thread.thread_num
    board: str = instance.post.thread.board.board

    now = timezone.now()
    today = now.strftime('%Y/%m/%d')

    return f'{today}/{board}/src/{thread}/{filename}'


def resolve_thumb_path(instance, filename):
    thread: str = instance.post.thread.thread_num
    board: str = instance.post.thread.board.board

    now = timezone.now()
    today = now.strftime('%Y/%m/%d')

    return f'{today}/{board}/thumb/{thread}/{filename}'


def roulette(match):
    """
    Бросаем кости с указанным количеством граней n-раз
    Использование 1RL2, где 1 - число граней, 2 - количество раз
    :param match: Объект match регулярного выражения
    :return: форматированный в html результат броска костей
    :rtype: str
    """
    first_num = int(match.group(1))
    last_num = int(match.group(2))

    if 0 < first_num <= 100 and 0 < last_num <= 10:
        maximum = first_num * last_num
        result = 0
        result_line = ''

        for i in range(0, last_num):
            rand_int = random.randint(0, first_num)
            result += rand_int
            result_line = (
                rand_int if not result_line else f'{result_line} + {rand_int}'
            )

        full_line = (
            f'{first_num}x{last_num}: {result_line} = {result}({maximum})'
        )
        return f'<br><span class="roulette">{full_line}</span><br>'

    return f'{first_num}RL{last_num}'
