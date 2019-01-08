import re

from django.db.models import DateTimeField, ExpressionWrapper, F, Q
from django.utils import timezone

from core import helpers
from .exceptions import (
    BoardNotFound, ThreadClosedError, ThreadNotFound, UserBannedError,
    WordInSpamListError
)
from .models import Ban, Board, SpamWord, Thread


def post_processing(request, serializer, **kwargs):
    board_name = kwargs.get('board_board')
    thread_id = kwargs.get('posts__num')

    subject = serializer.validated_data.get('subject')[:40]
    comment = serializer.validated_data.get('comment')
    sage = serializer.validated_data.get('sage')

    try:
        board = Board.objects.get(board=board_name)
    except Board.DoesNotExist:
        raise BoardNotFound

    ip = helpers.get_remote_ip(request)

    check_ban(ip, board)

    if check_spam(text=[comment, subject], board=board):
        raise WordInSpamListError

    subject = subject if board.enable_subject else ''
    sage = sage if board.enable_sage else False

    if thread_id:
        try:
            thread = Thread.objects.get(board=board, posts__num=thread_id)
        except Thread.DoesNotExist:
            raise ThreadNotFound

        if thread.is_closed:
            raise ThreadClosedError

        is_op_post = False
        parent = thread.thread_num

    else:
        thread = Thread.objects.create(board=board)
        is_op_post = True
        parent = 0

    serializer.context['thread'] = thread
    serializer.context['is_op_post'] = is_op_post
    serializer.context['parent'] = parent
    serializer.context['comment'] = process_text(comment)

    name = serializer.validated_data.get('name') or board.default_name

    name_trip = helpers.gen_tripcode(name, board.enable_trips)
    require_trip = helpers.require_trip(ip) if board.trip_required else ''

    name = (
        name_trip['name'] if board.enable_names else board.default_name
    )
    tripcode = require_trip or name_trip['trip']

    post_kwargs = {
        'name': name,
        'tripcode': tripcode,
        'ip': ip,
        'subject': subject,
        'sage': sage
    }

    return serializer, post_kwargs


def check_ban(ip, board):
    now = timezone.now()

    until = ExpressionWrapper(
        F('created') + F('duration'), output_field=DateTimeField()
    )
    q = (
        Q(board=board) | Q(for_all_boards=True),
        Q(inet__net_contains_or_equals=ip),
        Q(until__gte=now),
    )

    try:
        ban = Ban.objects.annotate(until=until).filter(*q).latest('until')
    except Ban.DoesNotExist:
        return
    else:
        until = timezone.make_naive(ban.until)
        raise UserBannedError(reason=ban.reason, until=until)


def check_spam(text, board):
    """
    Проверяем сообщение на содержания в нем слов из спам листа
    :param text: Текст для проверки
    :param board: Доска
    :return: Содержится ли слово в спам листе
    :rtype: bool
    """

    spam_filters = SpamWord.objects.filter(
        Q(for_all_boards=True) | Q(boards=board)
    ).values_list('expression', flat=True)

    if not spam_filters.exists():
        return False

    flags = re.IGNORECASE
    expressions = '|'.join(
        '(?:{0})'.format(x) for x in spam_filters
    )

    if isinstance(text, list):
        return any([re.fullmatch(expressions, t, flags=flags) for t in text])

    return re.fullmatch(expressions, text, flags=flags)


def process_text(text):
    new_text = re.sub(r'<', '&lt;', text)
    new_text = re.sub(
        r'(http:.+?)( |\n|$)', r'<a href="\1" target="_blank">\1</a>\2',
        new_text, flags=re.M
    )
    new_text = re.sub(
        r'(https:.+?)( |\n|$)', r'<a href="\1" target="_blank">\1</a>\2',
        new_text, flags=re.M
    )
    new_text = re.sub(r'\*\*(.+?)\*\*', r'<b class="bold">\1</b>', new_text)
    new_text = re.sub(
        r'\*(.+?)\*', r'<strong class="italic">\1</strong>', new_text
    )
    new_text = re.sub(r'__(.+?)__', r'<em class="crossed">\1</em>', new_text)
    new_text = re.sub(r'%%(.+?)%%', r'<i class="spoiler">\1</i>', new_text)

    # TODO: Ответы на посты
    new_text = re.sub(
        r'>>([0-9]+)', r'<a class="post_link" data-link="\1">>>\1</a>',
        new_text
    )

    new_text = re.sub(
        r'(^|\n)(>.+?)(\n|$)', r'\1<span class="quote">\2</span>\3', new_text,
        flags=re.M
    )

    return new_text
