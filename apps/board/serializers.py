from rest_framework import serializers
from rest_framework.exceptions import NotFound

from .models import Board, Category, Post, Thread


class PostSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(read_only=True)
    message = serializers.CharField(required=True, max_length=2000)
    ip = serializers.IPAddressField(write_only=True, required=False)

    class Meta:
        model = Post
        exclude = ('id', 'thread',)

    # TODO: #2 Создание тредов и постов
    def create(self, validated_data):
        board = self.context.get('board')
        thread = self.context.get('thread')
        if board:
            try:
                b = Board.objects.get(name=board)
            except Board.DoesNotExist:
                raise NotFound
            else:
                if thread:
                    t = Thread.objects.get(board=b, posts__post_id=thread)
                    is_op_post = False
                else:
                    t = Thread.objects.create(board=b)
                    is_op_post = True

                p = Post.objects.create(thread=t, is_op_post=is_op_post,
                                        **validated_data)
                return p


THREAD_READ_ONLY_FIELDS = ('is_pinned', 'is_closed', 'is_deleted', 'thread_id',)
THREAD_EXCLUDE_FIELDS = ('id', 'board',)


class ThreadPreviewSerializer(serializers.ModelSerializer):
    op_post = PostSerializer(many=False)
    last_posts = PostSerializer(many=True)

    thread_id = serializers.ReadOnlyField()

    class Meta:
        model = Thread
        exclude = THREAD_EXCLUDE_FIELDS
        read_only_fields = THREAD_READ_ONLY_FIELDS


class ThreadSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)

    class Meta:
        model = Thread
        exclude = THREAD_EXCLUDE_FIELDS
        read_only_fields = THREAD_READ_ONLY_FIELDS


class BoardSerializer(serializers.ModelSerializer):
    last_pid = serializers.ReadOnlyField()

    class Meta:
        model = Board

        exclude = ('id', 'category',)
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }


class CategorySerializer(serializers.ModelSerializer):
    boards = BoardSerializer(many=True)

    class Meta:
        model = Category
        fields = serializers.ALL_FIELDS
        read_only_fields = ('boards',)
