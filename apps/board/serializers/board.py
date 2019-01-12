from rest_framework import serializers

from ..models import Board


class BoardSerializer(serializers.ModelSerializer):
    last_num = serializers.ReadOnlyField()

    class Meta:
        model = Board

        exclude = ('id', 'category', 'trip_required', 'is_hidden')
        lookup_field = 'board'
        extra_kwargs = {
            'url': {'lookup_field': 'board'}
        }
