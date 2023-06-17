from unittest import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Alice', price=1000)
        book_2 = Book.objects.create(name='War and Peace', price=1200)
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Alice',
                'price': '1000.00'
            },
            {
                'id': book_2.id,
                'name': 'War and Peace',
                'price': '1200.00'
            }
        ]
        self.assertEquals(expected_data, data)