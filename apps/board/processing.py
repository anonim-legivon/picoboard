import mimetypes
import re
from os.path import splitext

import bleach
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from core import helpers
from .exceptions import (
    BoardNotFound, CommentRequiredError, FileCountLimitError, FileRequiredError,
    FileSizeLimitError, ProxyDisallowed, ThreadClosedError, ThreadNotFound,
    UnknownFileTypeError, UserBannedError, WordInSpamListError
)
from .helpers import roulette
from .models import Ban, Board, SpamWord, Thread


def process_post(request, serializer, **kwargs):
    data: dict = serializer.validated_data

    board_name: str = kwargs.get('board_board')
    thread_id: int = kwargs.get('posts__num')

    subject: str = data.get('subject', '')[:40]
    comment: str = data.get('comment')
    name: str = data.get('name')
    sage: bool = data.get('sage')
    files: list = data.get('post_files')
    op: bool = data.get('op', False)

    try:
        board = Board.objects.get(board=board_name)
    except Board.DoesNotExist:
        raise BoardNotFound

    ip = helpers.get_remote_ip(request)

    if not settings.PROXY_ALLOWED:
        if helpers.is_proxy_connect(ip):
            raise ProxyDisallowed

    check_ban(ip, board)

    subject = subject if board.enable_subject else ''
    sage = sage if board.enable_sage else False

    check_spam(board, subject, comment)

    if files:
        if len(files) > board.max_files:
            raise FileCountLimitError
        check_files(files, board.filesize_limit)
    elif not ((thread_id and comment) and (files or comment)):
        raise CommentRequiredError
    elif not thread_id and board.file_required:
        raise FileRequiredError

    if thread_id:
        try:
            thread = Thread.objects.get(board=board, posts__num=thread_id)
        except Thread.DoesNotExist:
            raise ThreadNotFound

        if thread.is_closed:
            raise ThreadClosedError

        is_op_post = False
        parent = thread.thread_num
        op = True if op and thread.op_post.ip == ip else False

    else:
        thread = Thread.objects.create(board=board)
        is_op_post = True
        parent = 0

        trim_database(board)

    poster_name = name or board.default_name
    name_trip = helpers.gen_tripcode(poster_name, board.enable_trips)
    require_trip = helpers.require_trip(ip) if board.trip_required else ''
    processed_name = (
        name_trip['name'] if board.enable_names else board.default_name
    )
    tripcode = require_trip or name_trip['trip']

    serializer.context['thread'] = thread
    serializer.context['is_op_post'] = is_op_post
    serializer.context['parent'] = parent
    serializer.context['comment'] = process_text(comment, board.enable_roulette)
    serializer.context['op'] = op

    post_kwargs = {
        'name': processed_name,
        'tripcode': tripcode,
        'ip': ip,
        'subject': subject,
        'sage': sage,
    }

    serializer.save(**post_kwargs)


def check_ban(ip, board):
    """
    Проверка постера на бан по доске
    :param ip: IP постера
    :param board: Текущая доска
    :raises: UserBannedError, если постер заблокирован
    """
    now = timezone.now()

    q = (
        Q(board=board) | Q(for_all_boards=True),
        Q(inet__net_contains_or_equals=ip),
        Q(until__gte=now),
    )

    try:
        ban = Ban.objects.filter(*q).latest('until')
    except Ban.DoesNotExist:
        return
    else:
        until = timezone.make_naive(ban.until)
        raise UserBannedError(reason=ban.reason, until=until)


def check_spam(board, *args):
    """
    Проверяем сообщение на содержания в нем слов из спам листа
    :param args: Тексты для проверки
    :type args: str
    :param board: Доска
    """
    spam_filters = SpamWord.objects.filter(
        Q(for_all_boards=True) | Q(boards=board)
    ).values_list('expression', flat=True)

    if not spam_filters.exists():
        return

    text = ' '.join(args)
    flags = (re.IGNORECASE | re.MULTILINE)
    expressions = '|'.join(
        '(?:{0})'.format(x) for x in spam_filters
    )

    if re.search(expressions, text, flags=flags):
        raise WordInSpamListError


def check_files(files, filesize_limit):
    allowed_mimetypes = (
        *settings.ALLOWED_IMAGE_TYPES,
        *settings.ALLOWED_VIDEO_TYPES,
    )

    total_filesize = sum(f.size for f in files)

    for file in files:
        file_ext = splitext(file.name)[1].lower()
        file_type = file.content_type
        guessed_ext = mimetypes.guess_all_extensions(file_type)

        if file_ext not in guessed_ext or file_type not in allowed_mimetypes:
            raise UnknownFileTypeError

    if total_filesize > filesize_limit:
        raise FileSizeLimitError


def process_text(text, enable_roulette):
    """
    Меняем псевдоразметку на html
    :param str text: Сообщение поста
    :param bool enable_roulette: Обрабатывать рулетку
    :return: Сообщение с разметкой и экранированным html
    :rtype: str
    """
    allowed_tags = settings.ALLOWED_TAGS
    allowed_styles = settings.ALLOWED_STYLES
    text = bleach.clean(text, tags=allowed_tags, styles=allowed_styles)

    link_markup = r'<a href="\1" target="_blank">\1</a>\2'
    bold_markup = r'<b class="bold">\1</b>'
    italic_markup = r'<strong class="italic">\1</strong>'
    crossed_markup = r'<em class="crossed">\1</em>'
    spoiler_markup = r'<i class="spoiler">\1</i>'
    post_link_markup = r'<a class="post_link" data-link="\1">>>\1</a>'
    quote_markup = r'\1<span class="quote">\2</span>\3'

    # Костыль чтобы вернуть > для корректного поиска цитаты
    text = re.sub(r'&gt;', '>', text, flags=re.M)

    text = re.sub(r'(https?:.+?)( |\n|$)', link_markup, text, flags=re.M)
    text = re.sub(r'\*\*(.+?)\*\*', bold_markup, text)
    text = re.sub(r'\*(.+?)\*', italic_markup, text)
    text = re.sub(r'__(.+?)__', crossed_markup, text)
    text = re.sub(r'%%(.+?)%%', spoiler_markup, text)
    text = re.sub(r'>>([0-9]+)', post_link_markup, text)
    text = re.sub(r'(^|\n)(>.+?)(\n|$)', quote_markup, text, flags=re.M)
    if enable_roulette:
        text = re.sub(r'([0-9]+)RL([0-9]+)', roulette, text)

    text = re.sub('\n', '<br>', text, flags=re.M)

    return text


# TODO: Сделать кастомный менеджер для softdelete
def trim_database(board):
    """
    Чистим базу данных каждый раз при создании тредов
    Удаляем треды, которые выходят за максимальное количество тредов доски
    :param board: Доска которую будем чистить
    :return: Количество удаленных тредов
    :rtype: int
    """
    deleted_count = 0
    max_threads = board.thread_limit
    total_threads = board.threads.count()

    if total_threads >= max_threads:
        delete_count = total_threads - max_threads
        threads_for_delete = Thread.objects.filter(
            board=board
        ).order_by('lasthit')[:delete_count]

        _, deleted_count = Thread.objects.filter(
            pk__in=threads_for_delete
        ).delete()

    return deleted_count
