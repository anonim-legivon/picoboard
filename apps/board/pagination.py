from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ThreadPageNumberPagination(PageNumberPagination):
    """
    Пагинация для списка тредов. Выводим по 20 тредов на страницу и докидываем
    общее количество страниц в ответ сервера
    """

    page_size = 20

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
