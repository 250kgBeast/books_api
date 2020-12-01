import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from shop.models import Book, UserBookRelation
from shop.serizalizers import BookSerializer, UserBookRelationSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Book1', author_name='Author1',
                                          price='100.00', owner=self.user)
        self.book_2 = Book.objects.create(name='Book2', author_name='Author2',
                                          price='100.00', owner=self.user)
        self.book_3 = Book.objects.create(name='Book3 Author2', author_name='Author3',
                                          price='300.00', owner=self.user)
        self.url = reverse('book-list')

    def test_get(self):
        books = Book.objects.all().annotate(
            likes_count=Count(Case(When(userbookrelation__like=True, then=1)))
        )
        response = self.client.get(self.url)
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(response.status_code, 200)

    def test_get_search(self):
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            likes_count=Count(Case(When(userbookrelation__like=True, then=1)))
        )
        serializer_data = BookSerializer(books, many=True).data
        response = self.client.get(
            self.url,
            data={
                'search': 'Author2'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_get_filter(self):
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_2.id]).annotate(
            likes_count=Count(Case(When(userbookrelation__like=True, then=1)))
        )
        serializer_data = BookSerializer(books, many=True).data
        response = self.client.get(
            self.url,
            data={
                'price': '100.00'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_get_order_by_price(self):
        books = Book.objects.all().annotate(
            likes_count=Count(Case(When(userbookrelation__like=True, then=1)))
        )
        serializer_data = BookSerializer(books, many=True).data
        response = self.client.get(
            self.url,
            data={
                'ordering': '-price'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

    def test_order_by_author_name(self):
        books = Book.objects.all().annotate(
            likes_count=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('-author_name')
        serializer_data = BookSerializer(books, many=True).data
        response = self.client.get(
            self.url,
            data={
                'ordering': '-author_name'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer_data)

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
        self.assertEqual(Book.objects.last().owner, self.user)

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
        url = reverse('book-detail', args=(self.book_1.id,))
        self.assertTrue(Book.objects.filter(name='Book1').exists())
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Book.objects.filter(name='Book1').exists())

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        self.assertEqual(self.book_1.price, '100.00')
        data = {
            "name": self.book_1.name,
            "author_name": self.book_1.author_name,
            "price": 200
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, json_data,
                                   content_type='application/json')

        self.assertEqual(response.status_code, 403)
        self.book_1.refresh_from_db()
        self.assertEqual(100, self.book_1.price)
        self.assertEqual(response.data, {
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')
        })

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        self.assertTrue(Book.objects.filter(name='Book1').exists())
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Book.objects.filter(name='Book1').exists())
        self.assertEqual(response.data, {
            'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                  code='permission_denied')
        })

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        self.assertEqual(self.book_1.price, '100.00')
        data = {
            "name": self.book_1.name,
            "author_name": self.book_1.author_name,
            "price": 200
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, json_data,
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.book_1.refresh_from_db()
        self.assertEqual(200, self.book_1.price)


class BooksRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create(username='test_username1')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Book1', author_name='Author1',
                                          price='100.00', owner=self.user1)
        self.book_2 = Book.objects.create(name='Book2', author_name='Author2',
                                          price='100.00', owner=self.user1)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'like': True,
        }
        self.client.force_login(self.user2)
        json_data = json.dumps(data)
        response = self.client.patch(url, json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        relation = UserBookRelation.objects.get(user=self.user2,
                                                book=self.book_1)
        self.book_1.refresh_from_db()
        self.assertTrue(relation.like)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'rate': 3,
        }
        self.client.force_login(self.user2)
        json_data = json.dumps(data)
        response = self.client.patch(url, json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)
        relation = UserBookRelation.objects.get(user=self.user2,
                                                book=self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            'rate': 6,
        }
        self.client.force_login(self.user2)
        json_data = json.dumps(data)
        response = self.client.patch(url, json_data,
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
