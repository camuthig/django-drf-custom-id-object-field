from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from bookstore import models, serializers
import base64


class ModelViewSet(viewsets.ModelViewSet):
    def get_object(self):
        """
        Returns the object the view is displaying.

        This is a port of the GenericAPIView implementation to support decoding the ID
        """

        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        decoded_lookup_value = base64.urlsafe_b64decode(self.kwargs[lookup_url_kwarg]).decode("utf-8")

        filter_kwargs = {self.lookup_field: decoded_lookup_value}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class AuthorViewSet(ModelViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class BookViewSet(ModelViewSet):
    queryset = models.Book.objects.all()
    serializer_class = serializers.BookSerializer
