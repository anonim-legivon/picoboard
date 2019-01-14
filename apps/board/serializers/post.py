from django.conf import settings
from recaptcha.fields import ReCaptchaField
from rest_framework import serializers

from .. import constants
from ..models import File, Post


class FileSerializer(serializers.ModelSerializer):
    size = serializers.ReadOnlyField(source='file.size')
    path = serializers.ReadOnlyField(source='file.url')
    name = serializers.ReadOnlyField()
    thumbnail = serializers.ReadOnlyField(source='thumbnail.url')

    class Meta:
        exclude = ('id', 'post', 'file',)
        model = File

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['type'] == constants.IMAGE_FILE:
            representation.pop('duration', None)
        return representation


class PostSerializer(serializers.ModelSerializer):
    recaptcha = ReCaptchaField(write_only=True)
    comment = serializers.CharField(
        required=True, min_length=4, max_length=15000
    )
    post_files = serializers.ListField(
        child=serializers.FileField(use_url=False),
        required=False, write_only=True
    )
    files = FileSerializer(many=True, read_only=True)

    # op = serializers.ReadOnlyField()

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

    def create(self, validated_data):
        thread = self.context.get('thread')
        is_op_post = self.context.get('is_op_post')
        parent = self.context.get('parent')

        validated_data.pop('recaptcha', None)
        validated_data['comment'] = self.context.get('comment')

        files = validated_data.pop('post_files', None)

        post = Post.objects.create(
            thread=thread, is_op_post=is_op_post, parent=parent,
            **validated_data
        )

        if files:
            related_files = []
            for file in files:
                file_type = 0 if file.content_type in settings.ALLOWED_IMAGE_TYPES else 1
                file = File(file=file, post=post, type=file_type)
                file.save()
                related_files.append(file)

            post.files.add(*related_files)

        return post
