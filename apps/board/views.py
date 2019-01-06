from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from core.helpers import gen_tripcode, get_remote_ip
from core.mixins import CreateListRetrieveMixin
from .models import Board, Category, Thread
from .pagination import ThreadLimitOffsetPagination
from .serializers import (
    BoardSerializer, CategorySerializer, PostSerializer,
    ThreadPreviewSerializer, ThreadSerializer
)


class ThreadViewSet(CreateListRetrieveMixin, GenericViewSet):
    pagination_class = ThreadLimitOffsetPagination

    lookup_field = 'posts__post_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return ThreadPreviewSerializer
        else:
            return ThreadSerializer

    def get_queryset(self):
        qs = Thread.objects.filter(
            board__name=self.kwargs['board_name']
        )

        if self.action == 'list':
            qs.filter(posts__is_op_post=True)
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

    def create(self, request, *args, **kwargs):
        board = kwargs.get('board_name')
        serializer = PostSerializer(data=request.data, context={'board': board})
        serializer.is_valid(raise_exception=True)
        ip = get_remote_ip(request)
        self.perform_create(serializer, ip=ip)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    @action(detail=True, methods=['post'])
    def post(self, request, **kwargs):
        board = kwargs.get('board_name')
        thread_id = kwargs.get('posts__post_id')
        serializer = PostSerializer(
            data=request.data,
            context={'board': board, 'thread': thread_id}
        )
        serializer.is_valid(raise_exception=True)
        ip = get_remote_ip(request)
        self.perform_create(serializer, ip=ip)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer, **kwargs):
        name = serializer.validated_data.get('name')
        board_name = serializer.context.get('board')

        try:
            board = Board.objects.get(name=board_name)
        except Board.DoesNotExist:
            raise NotFound
        else:
            serializer.context['board'] = board

        if name:
            tripcode = gen_tripcode(name, board.trip_permit)
            kwargs['name'] = tripcode['name'] or _('Аноним')
            kwargs['tripcode'] = tripcode['trip']

        serializer.save(**kwargs)


class BoardViewSet(ReadOnlyModelViewSet, GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    lookup_field = 'name'


class CategoryViewSet(ReadOnlyModelViewSet, GenericViewSet):
    queryset = Category.objects.prefetch_related('boards').order_by('-order')
    serializer_class = CategorySerializer
