from django.test import TestCase
from django.urls import reverse

from shop.models import Book
from shop.serizalizers import BookSerializer


class BooksSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Book1', author_name='Author1', price='100.00')
        book_2 = Book.objects.create(name='Book2', author_name='Author2', price='200.00')
        data = BookSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id':  book_1.id,
                'name': 'Book1',
                'author_name': 'Author1',
                'price': '100.00'
            },
            {
                'id': book_2.id,
                'name': 'Book2',
                'author_name': 'Author2',
                'price': '200.00'
            },
        ]
        self.assertEqual(expected_data, data)
