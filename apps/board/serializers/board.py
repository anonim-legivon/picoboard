from rest_framework import serializers

from ..models import Board


class BoardSerializer(serializers.ModelSerializer):
    last_pid = serializers.ReadOnlyField()

    class Meta:
        model = Board

        exclude = ('id', 'category',)
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }
