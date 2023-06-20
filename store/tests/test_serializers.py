from unittest import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):

    def setUp(self) -> None:
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1')
        self.book_2 = Book.objects.create(name='War and Peace', price=1200,
                                          author_name='Author 2')

    def test_ok(self):
        data = BooksSerializer([self.book_1, self.book_2], many=True).data
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Alice',
                'price': '1000.00',
                'author_name': 'Author 1'
            },
            {
                'id': self.book_2.id,
                'name': 'War and Peace',
                'price': '1200.00',
                'author_name': 'Author 2'
            }
        ]
        self.assertEquals(expected_data, data)
