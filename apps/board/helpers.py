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
