import re

from django.db.models import DateTimeField, ExpressionWrapper, F, Q
from django.utils import timezone

from core.helpers import gen_tripcode, get_remote_ip
from .exceptions import (
    BoardNotFound, ThreadClosedError, ThreadNotFound, UserBannedError,
    WordInSpamListError
)
from .models import Ban, Board, SpamWord, Thread


def post_processing(request, serializer, **kwargs):
    board_name = kwargs.get('board_board')
    thread_id = kwargs.get('posts__num')

    name = serializer.validated_data.get('name')
    subject = serializer.validated_data.get('subject')
    comment = serializer.validated_data.get('comment')

    post_kwargs = dict()

    try:
        board = Board.objects.get(board=board_name)
    except Board.DoesNotExist:
        raise BoardNotFound

    ip = get_remote_ip(request)

    check_ban(ip, board)

    if check_spam(comment, subject, board):
        raise WordInSpamListError

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

    if name:
        tripcode = gen_tripcode(name, board.trip_permit)

        post_kwargs['name'] = tripcode['name'] or board.default_name
        post_kwargs['tripcode'] = tripcode['trip']

    post_kwargs['ip'] = ip

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


def check_spam(comment, subject, board):
    """
    Проверяем сообщение на содержания в нем слов из спам листа
    :param subject: Тема поста
    :param comment: Сообщение
    :param board: Доска
    :return: Содержится ли слово в спам листе
    :rtype: bool
    """

    spam_filters = SpamWord.objects.filter(
        Q(for_all_boards=True) | Q(boards=board)
    ).values_list('expression', flat=True)

    if not spam_filters.exists():
        return True

    flags = re.IGNORECASE
    expressions = '|'.join(
        '(?:{0})'.format(x) for x in spam_filters
    )

    if subject:
        check_subject = re.fullmatch(expressions, subject, flags=flags)

        if check_subject:
            return True

    return re.fullmatch(expressions, comment, flags=flags)


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
