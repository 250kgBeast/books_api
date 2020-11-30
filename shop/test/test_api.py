from django.urls import reverse
from rest_framework.test import APITestCase

from shop.models import Book
from shop.serizalizers import BookSerializer


class BooksApiTestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='Book1', price='100.00')
        book_2 = Book.objects.create(name='Book2', price='200.00')
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([book_1, book_2], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(response.status_code, 200)
