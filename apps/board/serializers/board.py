from rest_framework import serializers

from ..models import Board


class BoardSerializer(serializers.ModelSerializer):
    last_num = serializers.ReadOnlyField()

    class Meta:
        model = Board

        exclude = ('id', 'category',)
        lookup_field = 'board'
        extra_kwargs = {
            'url': {'lookup_field': 'board'}
        }
