from rest_framework import serializers

from .board import BoardSerializer
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    boards = BoardSerializer(many=True)

    class Meta:
        model = Category
        fields = serializers.ALL_FIELDS
        read_only_fields = ('boards',)
