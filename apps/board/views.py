from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.viewsets import GenericViewSet

from .models import Board, Category, Thread
from .serializers import (BoardSerializer, CategorySerializer,
                          ThreadPreviewSerializer, ThreadSerializer)


class CreateListRetrieveMixin(CreateModelMixin, ListModelMixin,
                              RetrieveModelMixin):
    pass


class ThreadViewSet(CreateListRetrieveMixin, GenericViewSet):
    queryset = Thread.objects.prefetch_related('posts')

    def get_serializer_class(self):
        if self.action == 'list':
            return ThreadPreviewSerializer
        else:
            return ThreadSerializer


class BoardViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer


class CategoryViewSet(ListModelMixin, GenericViewSet):
    queryset = Category.objects.prefetch_related('boards')
    serializer_class = CategorySerializer
