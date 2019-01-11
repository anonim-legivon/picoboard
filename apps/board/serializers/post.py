from recaptcha.fields import ReCaptchaField
from rest_framework import serializers

from ..models import File, Post


class FileSerializer(serializers.ModelSerializer):
    size = serializers.ReadOnlyField(source='file.size')
    path = serializers.ReadOnlyField(source='file.url')
    name = serializers.SerializerMethodField()

    class Meta:
        exclude = ('id', 'post', 'file',)
        model = File

    def get_name(self, obj):
        name = obj.file.name.split('/')[-1:][0]
        return name


class PostSerializer(serializers.ModelSerializer):
    recaptcha = ReCaptchaField(write_only=True)
    comment = serializers.CharField(required=True, max_length=15000)
    post_files = serializers.ListField(
        child=serializers.FileField(use_url=False),
        required=False, write_only=True
    )
    files = FileSerializer(many=True, read_only=True, required=False)

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
        validated_data.pop('recaptcha', None)
        validated_data['comment'] = self.context.get('comment')

        files = validated_data.pop('post_files', None)

        post = Post.objects.create(
            thread=thread, is_op_post=is_op_post, parent=parent,
            **validated_data
        )

        if files:
            related = []
            for file in files:
                file = File(file=file, post=post, type=0)
                file.save()
                related.append(file)

            post.files.add(*related)

        return post
