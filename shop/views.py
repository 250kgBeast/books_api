from rest_framework.viewsets import ModelViewSet

from shop.models import Book
from shop.serizalizers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
