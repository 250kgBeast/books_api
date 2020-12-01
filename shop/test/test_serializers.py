from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.test import TestCase

from shop.models import Book, UserBookRelation
from shop.serizalizers import BookSerializer


class BooksSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        user3 = User.objects.create(username='user3')

        book_1 = Book.objects.create(name='Book1', author_name='Author1', price='100.00')
        book_2 = Book.objects.create(name='Book2', author_name='Author2', price='200.00')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True)
        UserBookRelation.objects.create(user=user3, book=book_1, like=True)

        UserBookRelation.objects.create(user=user1, book=book_2, like=True)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            likes_count=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')

        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id':  book_1.id,
                'name': 'Book1',
                'author_name': 'Author1',
                'price': '100.00',
                'likes_count': 3
            },
            {
                'id': book_2.id,
                'name': 'Book2',
                'author_name': 'Author2',
                'price': '200.00',
                'likes_count': 2
            },
        ]
        self.assertEqual(expected_data, data)
