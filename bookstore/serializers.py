import base64

from rest_framework import serializers
from bookstore import models


class HashedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        # TODO This could be implemented in a safe manner
        data = base64.urlsafe_b64decode(data).decode('utf-8')
        return super().to_internal_value(data)

    def to_representation(self, value):
        # TODO Research how to use pk_field
        if value is None:
            return value

        id_value = f'{value.pk}'

        hashed = base64.urlsafe_b64encode(bytes(id_value, 'utf-8')).decode('utf-8')
        return hashed


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['name']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = ['title', 'author']

    serializer_related_field = HashedPrimaryKeyRelatedField
