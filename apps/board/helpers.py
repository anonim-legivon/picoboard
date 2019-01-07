import re

from django.db.models import Q

from core.helpers import gen_tripcode, get_remote_ip
from .exceptions import (
    BoardNotFound, ThreadClosedError, ThreadNotFound, WordInSpamListError
)
from .models import Board, SpamWord, Thread


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
        parent = thread.thread_id

    else:
        thread = Thread.objects.create(board=board)
        is_op_post = True
        parent = 0

    serializer.context['thread'] = thread
    serializer.context['is_op_post'] = is_op_post
    serializer.context['parent'] = parent

    if name:
        tripcode = gen_tripcode(name, board.trip_permit)

        post_kwargs['name'] = tripcode['name'] or board.default_name
        post_kwargs['tripcode'] = tripcode['trip']

    post_kwargs['ip'] = get_remote_ip(request)

    return serializer, post_kwargs


def check_spam(comment, subject, board):
    """
    Проверяем сообщение на содержания в нем слов из спам листа
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
