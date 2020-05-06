import base64

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from typing import Optional

from bookstore import models


class HashedPrimaryKeyField(serializers.CharField):
    def to_internal_value(self, data):
        return base64.urlsafe_b64decode(data).decode('utf-8')

    def to_representation(self, value):
        return base64.urlsafe_b64encode(bytes(f'{value}', 'utf-8')).decode('utf-8')


class HashedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        data = base64.urlsafe_b64decode(data).decode('utf-8')
        return super().to_internal_value(data)

    def to_representation(self, value):
        if value is None:
            return value

        return base64.urlsafe_b64encode(bytes(f'{value.pk}', 'utf-8')).decode('utf-8')


class NestedHashedPrimaryKeyRelatedField(HashedPrimaryKeyRelatedField):
    default_error_messages = {
        'id_missing': _('The id key must be provided'),
    }

    fields = {
        'id': HashedPrimaryKeyField(),
    }

    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
        super().__init__(**kwargs)

    def _format(self) -> Optional[str]:
        format = self.context.get('format', None)

        if format is None and settings.URL_FORMAT_OVERRIDE is not None:
            request = self.context['request']
            format = request.query_params.get(settings.URL_FORMAT_OVERRIDE)

        return format

    def _is_json(self):
        request = self.context['request']
        content_type = request.headers.get('content-type', None)

        return 'application/json' in content_type

    def _accepts_json(self):
        return 'json' == self._format()

    def run_validation(self, data=None):
        if self._is_json() and data is not None:
            if not isinstance(data, dict):
                self.fail('id_missing')
            if 'id' not in data:
                self.fail('id_missing')

        return super().run_validation(data=data)

    def use_pk_only_optimization(self):
        if self._accepts_json:
            return False

        return True

    def to_internal_value(self, data):
        if self._is_json() and data is not None:
            data = data['id']

        return super().to_internal_value(data)

    def to_representation(self, value):
        if self._accepts_json():
            return self.serializer(instance=value).data

        return super().to_representation(value)


class ModelSerializer(serializers.ModelSerializer):
    id = HashedPrimaryKeyField(read_only=True)


class AuthorSerializer(ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['id', 'name']


class BookSerializer(ModelSerializer):
    class Meta:
        model = models.Book
        fields = ['id', 'title', 'author']

    author = NestedHashedPrimaryKeyRelatedField(queryset=models.Author.objects, serializer=AuthorSerializer)
