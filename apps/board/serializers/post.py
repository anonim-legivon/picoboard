from rest_framework import serializers

from ..models import Post, Thread


class PostSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True, max_length=15000)

    class Meta:
        model = Post
        exclude = ('id', 'thread',)
        read_only_fields = ('tripcode', 'is_deleted', 'post_id',)
        extra_kwargs = {
            'password': {'write_only': True},
            'ip': {'write_only': True},
        }

    # TODO: #2 Создание тредов и постов
    def create(self, validated_data):
        board = self.context.get('board')
        thread = self.context.get('thread')

        if thread:
            thread = Thread.objects.get(board=board, posts__post_id=thread)
            is_op_post = False
        else:
            thread = Thread.objects.create(board=board)
            is_op_post = True

        post = Post.objects.create(thread=thread, is_op_post=is_op_post,
                                   **validated_data)
        return post
