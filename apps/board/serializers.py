from rest_framework import serializers
from rest_framework.exceptions import NotFound

from .models import Board, Category, Post, Thread


class PostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='post_id', read_only=True)
    message = serializers.CharField(required=True, max_length=2000)

    class Meta:
        model = Post
        exclude = ('post_id', 'thread',)

    def create(self, validated_data):
        board = self.context.get('board')
        if board:
            try:
                b = Board.objects.get(name=board)
            except Board.DoesNotExist:
                raise NotFound
            else:
                t = Thread.objects.create(board=b)
                p = Post.objects.create(thread=t, is_op_post=True,
                                        **validated_data)
                return p


class ThreadPreviewSerializer(serializers.ModelSerializer):
    op_post = PostSerializer(many=False)
    last_posts = PostSerializer(many=True)

    class Meta:
        model = Thread
        exclude = ('board',)
        read_only_fields = ('is_pinned', 'is_closed', 'is_deleted',)


class ThreadSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)

    class Meta:
        model = Thread
        exclude = ('board',)
        read_only_fields = ('is_pinned', 'is_closed', 'is_deleted',)


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = serializers.ALL_FIELDS


class CategorySerializer(serializers.ModelSerializer):
    boards = BoardSerializer(many=True)

    class Meta:
        model = Category
        fields = serializers.ALL_FIELDS
        read_only_fields = ('boards',)
