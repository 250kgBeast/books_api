import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from shop.models import Book
from shop.serizalizers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.book_1 = Book.objects.create(name='Book1', author_name='Author1', price='100.00')
        self.book_2 = Book.objects.create(name='Book2', author_name='Author2', price='100.00')
        self.book_3 = Book.objects.create(name='Book3 Author2', author_name='Author3', price='300.00')
        self.url = reverse('book-list')
        self.user = User.objects.create(username='test_username')

    def test_get(self):
        response = self.client.get(self.url)
        serializer_data = BookSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        serializer_data = BookSerializer([self.book_2, self.book_3], many=True).data
        response = self.client.get(
            self.url,
            data={
                'search': 'Author2'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_get_filter(self):
        serializer_data = BookSerializer([self.book_1, self.book_2], many=True).data
        response = self.client.get(
            self.url,
            data={
                'price': '100.00'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_get_order_by_price(self):
        serializer_data = BookSerializer([self.book_3, self.book_1, self.book_2], many=True).data
        response = self.client.get(
            self.url,
            data={
                'ordering': '-price'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_order_by_author_name(self):
        serializer_data = BookSerializer([self.book_3, self.book_2, self.book_1], many=True).data
        response = self.client.get(
            self.url,
            data={
                'ordering': '-author_name'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_permission_denied_for_unauthenticated_users(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create(self):
        self.assertEqual(Book.objects.count(), 3)
        data = {
            "id": 1,
            "name": "Programing in Python 3",
            "author_name": "Mark Summerfield",
            "price": "600.00"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(self.url, json_data,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Book.objects.count(), 4)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.assertEqual(self.book_1.price, '100.00')
        data = {
            "name": self.book_1.name,
            "author_name": self.book_1.author_name,
            "price": 200
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, json_data,
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.book_1.refresh_from_db()
        self.assertEqual(200, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id, ))
        self.assertTrue(Book.objects.filter(name='Book1').exists())
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Book.objects.filter(name='Book1').exists())
