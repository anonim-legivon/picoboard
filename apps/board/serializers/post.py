from rest_framework import serializers

from ..models import Post


class PostSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=True, max_length=15000)

    class Meta:
        model = Post
        exclude = ('id', 'thread',)
        read_only_fields = (
            'tripcode', 'is_deleted', 'num',
            'parent', 'is_op_post', 'thread',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'ip': {'write_only': True},
        }

    # TODO: #2 Создание тредов и постов
    def create(self, validated_data):
        thread = self.context.get('thread')
        is_op_post = self.context.get('is_op_post')
        parent = self.context.get('parent')
        validated_data['comment'] = self.context.get('comment')

        post = Post.objects.create(
            thread=thread, is_op_post=is_op_post, parent=parent,
            **validated_data
        )

        return post
