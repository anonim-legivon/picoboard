from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from core.mixins import CreateListRetrieveMixin
from .helpers import post_processing
from .models import Board, Category, Thread
from .pagination import ThreadLimitOffsetPagination
from .serializers import (
    BoardSerializer,
    CategorySerializer,
    PostSerializer,
    ThreadPreviewSerializer,
    ThreadSerializer,
)


class ThreadViewSet(CreateListRetrieveMixin, GenericViewSet):
    pagination_class = ThreadLimitOffsetPagination

    lookup_field = 'posts__num'

    def get_serializer_class(self):
        return (
            ThreadPreviewSerializer
            if self.action == 'list' else
            ThreadSerializer
        )

    def get_queryset(self):
        qs = Thread.objects.filter(
            board__board=self.kwargs['board_board']
        )

        if self.action == 'list':
            qs = qs.select_related('board')
            qs = qs.order_by('-is_pinned', '-lasthit')

        qs = qs.prefetch_related('posts')
        return qs

    def get_throttles(self):
        if self.action in ['create', 'post']:
            self.throttle_scope = 'thread.' + self.action
        return super().get_throttles()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_field

        filter_kwargs = {
            self.lookup_field: self.kwargs[lookup_url_kwarg],
            'posts__is_op_post': True
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    @cache_response(1)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(1)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    # TODO: create и post совпадают, возможно стоит вынести в отдельную функцию,
    #       но в дальнейшем может измениться
    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    # TODO: Так как функции совпадают пока заменил на вызов create
    @action(detail=True, methods=['post'])
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer, **kwargs):
        serializer, post_kwargs = post_processing(
            self.request, serializer, **self.kwargs
        )

        serializer.save(**post_kwargs)


class BoardViewSet(CacheResponseMixin, ReadOnlyModelViewSet, GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = 'board'


class CategoryViewSet(CacheResponseMixin, ReadOnlyModelViewSet, GenericViewSet):
    queryset = Category.objects.prefetch_related('boards').order_by('-order')
    serializer_class = CategorySerializer
