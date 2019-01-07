from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound


class BoardNotFound(NotFound):
    default_detail = _('Указанная доска не найдена')
    default_code = 'board_not_found'


class ThreadNotFound(NotFound):
    default_detail = _('Указанный тред не найден')
    default_code = 'thread_not_found'


class WordInSpamListError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Пост содержит слово из спам листа')
    default_code = 'word_in_spam_list_error'


class ThreadClosedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Тред закрыт')
    default_code = 'thread_closed_error'
