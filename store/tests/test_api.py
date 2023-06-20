from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookApiTestCase(APITestCase):

    def setUp(self) -> None:
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1')
        self.book_2 = Book.objects.create(name='War and Peace', price=1200,
                                          author_name='Author 3')
        self.book_3 = Book.objects.create(name='The life of Author 1',
                                          price=1500, author_name='Author 2')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2,
                                           self.book_3], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book_1, self.book_3],
                                          many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serializer_data, response.data)
