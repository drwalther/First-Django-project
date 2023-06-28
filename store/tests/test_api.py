import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='War and Peace', price=1500,
                                          author_name='Author 3')
        self.book_3 = Book.objects.create(name='The life of Author 1',
                                          price=1200, author_name='Author 2')

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

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BooksSerializer([self.book_1, self.book_3,
                                           self.book_2], many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serializer_data, response.data)

    def test_create(self):
        starting_count = Book.objects.all().count()
        url = reverse('book-list')
        data = {
            'name': 'Black fire',
            'price': 760,
            'author_name': 'Jack Jacobson'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        ending_count = Book.objects.all().count()
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(starting_count, ending_count - 1)
        self.assertEquals(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 500,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEquals(500, self.book_1.price)

    def test_update_not_owner(self):
        self.user_2 = User.objects.create(username='test_user2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 500,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEquals(1000, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user_2 = User.objects.create(username='test_user2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 500,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEquals(500, self.book_1.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        starting_count = Book.objects.all().count()
        data = {
            'name': self.book_1.name,
            'price': self.book_1.price,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.delete(url, data=json_data,
                                      content_type='application/json')
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        ending_count = Book.objects.all().count()
        self.assertEquals(starting_count, ending_count + 1)
