from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=256)


class Book(models.Model):
    title = models.CharField(max_length=256)
