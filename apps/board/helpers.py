import random
from os.path import splitext

from django.utils import timezone


def resolve_save_path(instance, filename):
    thread = instance.post.thread.thread_num
    board = instance.post.thread.board.board

    now = timezone.now()
    timestamp = int(now.timestamp() * 10000)
    date = now.strftime('%Y/%m/%d')
    ext = splitext(filename)[1]

    return f'{date}/{board}/{thread}/{timestamp}{ext}'


def roulette(match):
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
