from rest_framework.pagination import LimitOffsetPagination


class ThreadLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 20
