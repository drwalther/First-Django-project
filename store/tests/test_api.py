import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookApiTestCase(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create(username='test_user')
        self.user_2 = User.objects.create(username='test_user2')
        self.user_3 = User.objects.create(username='test_user3', is_staff=True)

        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1',
                                          owner=self.user_1)
        self.book_2 = Book.objects.create(name='War and Peace', price=1500,
                                          author_name='Author 3')
        self.book_3 = Book.objects.create(name='The life of Author 1',
                                          price=1200, author_name='Author 2')
        UserBookRelation.objects.create(user=self.user_1, book=self.book_1,
                                        like=True, rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(annotated_likes=Count(
            Case(When(userbookrelation__like=True, then=1))))
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[2]['annotated_likes'], 1)
        self.assertEqual(serializer_data[2]['rating'], '5.00')

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(
            id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(
                Case(When(userbookrelation__like=True, then=1)))).select_related(
            'owner').prefetch_related('readers')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        books = Book.objects.filter(
            id__in=[self.book_1.id, self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(
                Case(When(userbookrelation__like=True, then=1)))).order_by(
            'price')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BooksSerializer(books, many=True).data
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
        self.client.force_login(self.user_1)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        ending_count = Book.objects.all().count()
        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(starting_count, ending_count - 1)
        self.assertEquals(self.user_1, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 500,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEquals(500, self.book_1.price)

    def test_update_not_owner(self):
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
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 500,
            'author_name': self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_3)
        response = self.client.patch(url, data=json_data,
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
        self.client.force_login(self.user_1)
        response = self.client.delete(url, data=json_data,
                                      content_type='application/json')
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        ending_count = Book.objects.all().count()
        self.assertEquals(starting_count, ending_count + 1)


class BookRelationTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.user_2 = User.objects.create(username='test_user_2')
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='War and Peace', price=1500,
                                          author_name='Author 3')
        self.book_3 = Book.objects.create(name='The life of Author 1',
                                          price=1200, author_name='Author 2')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {'like': True}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {'in_bookmarks': True}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {'rate': 3}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        print('book id', self.book_1.id)
        print('book id', self.book_1.id, self.user.username)
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {'rate': 6}
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(None, relation.rate)
