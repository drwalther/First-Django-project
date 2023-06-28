from unittest import TestCase

from django.contrib.auth.models import User

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):

    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='test_user1')
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1',
                                          owner=self.user_1,
                                          readers=)
        self.book_2 = Book.objects.create(name='War and Peace', price=1200,
                                          author_name='Author 2',
                                          owner=self.user_1)

    def test_ok(self):
        data = BooksSerializer([self.book_1, self.book_2], many=True).data
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Alice',
                'price': '1000.00',
                'author_name': 'Author 1',
                'owner': self.book_1.owner.id
            },
            {
                'id': self.book_2.id,
                'name': 'War and Peace',
                'price': '1200.00',
                'author_name': 'Author 2',
                'owner': self.book_2.owner.id
            }
        ]
        self.assertEquals(expected_data, data)
