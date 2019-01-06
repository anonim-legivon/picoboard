from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound


class BoardNotFound(NotFound):
    default_detail = _('Указанная доска не найдена')
    default_code = 'board_not_found'


class ThreadNotFound(NotFound):
    default_detail = _('Указанный тред не найден')
    default_code = 'thread_not_found'
