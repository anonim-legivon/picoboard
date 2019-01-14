from rest_framework import serializers

from .post import PostSerializer
from ..models import Thread

THREAD_READ_ONLY_FIELDS = (
    'is_pinned', 'is_closed', 'thread_id',
)

THREAD_EXCLUDE_FIELDS = ('id',)


class ThreadPreviewSerializer(serializers.ModelSerializer):
    op_post = PostSerializer(many=False)
    last_posts = PostSerializer(many=True)

    thread_num = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    board = serializers.ReadOnlyField(source='board.board')
    files_count = serializers.ReadOnlyField()

    class Meta:
        model = Thread
        exclude = THREAD_EXCLUDE_FIELDS
        read_only_fields = THREAD_READ_ONLY_FIELDS


class ThreadSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)

    thread_num = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    board = serializers.ReadOnlyField(source='board.board')
    files_count = serializers.ReadOnlyField()
    unique_posters = serializers.ReadOnlyField()

    class Meta:
        model = Thread
        exclude = THREAD_EXCLUDE_FIELDS
        read_only_fields = THREAD_READ_ONLY_FIELDS
