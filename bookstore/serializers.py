from rest_framework import serializers
from bookstore import models


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Author
        fields = ['name']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = ['title']
