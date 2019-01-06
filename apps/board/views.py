from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from core.helpers import gen_tripcode, get_remote_ip
from core.mixins import CreateListRetrieveMixin
from .exceptions import BoardNotFound
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
            qs = qs.order_by('-lasthit')

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

    # TODO: create и post совпадают, возможно стоит вынести в отдельную функцию,
    #       но в дальнейшем может измениться
    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=['post'])
    def post(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer, **kwargs):
        board_name = self.kwargs.get('board_board')
        thread_id = self.kwargs.get('posts__num')

        name = serializer.validated_data.get('name')

        try:
            board = Board.objects.get(board=board_name)
        except Board.DoesNotExist:
            raise BoardNotFound
        else:
            serializer.context['board'] = board
            serializer.context['thread'] = thread_id

        if name:
            tripcode = gen_tripcode(name, board.trip_permit)

            kwargs['name'] = tripcode['name'] or board.default_name
            kwargs['tripcode'] = tripcode['trip']

        kwargs['ip'] = get_remote_ip(self.request)

        serializer.save(**kwargs)


class BoardViewSet(ReadOnlyModelViewSet, GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = 'board'


class CategoryViewSet(ReadOnlyModelViewSet, GenericViewSet):
    queryset = Category.objects.prefetch_related('boards').order_by('-order')
    serializer_class = CategorySerializer
