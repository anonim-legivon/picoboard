from rest_framework import serializers

from .post import PostSerializer
from ..models import Thread

THREAD_READ_ONLY_FIELDS = (
    'is_pinned', 'is_closed', 'thread_id',
)

THREAD_EXCLUDE_FIELDS = ('id', 'is_removed',)


class ThreadPreviewSerializer(serializers.ModelSerializer):
    op_post = PostSerializer(many=False)
    last_posts = PostSerializer(many=True)

    thread_id = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    board = serializers.ReadOnlyField(source='board.board')

    class Meta:
        model = Thread
        exclude = THREAD_EXCLUDE_FIELDS
        read_only_fields = THREAD_READ_ONLY_FIELDS


class ThreadSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)

    posts_count = serializers.ReadOnlyField()
    board = serializers.ReadOnlyField(source='board.board')

    class Meta:
        model = Thread
        exclude = THREAD_EXCLUDE_FIELDS
        read_only_fields = THREAD_READ_ONLY_FIELDS
