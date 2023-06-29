from django.contrib.auth.models import User
from django.db.models import Case, When, Count
from django_filters.compat import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):

    def setUp(self) -> None:
        self.user_1 = User.objects.create(username='test_user1')
        self.user_2 = User.objects.create(username='test_user2')
        self.user_3 = User.objects.create(username='test_user3')
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1',
                                          owner=self.user_1)
        self.book_2 = Book.objects.create(name='War and Peace', price=1200,
                                          author_name='Author 2',
                                          owner=self.user_1)

    def test_ok(self):
        UserBookRelation.objects.create(user=self.user_1, book=self.book_1, like=True)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1,
                                        like=True)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1,
                                        like=True)

        UserBookRelation.objects.create(user=self.user_1, book=self.book_2,
                                        like=True)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_2,
                                        like=True)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1,
                                        like=False)
        books = Book.objects.all().annotate(annotated_likes=Count(
            Case(When(userbookrelation__like=True, then=1)))).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Alice',
                'price': '1000.00',
                'author_name': 'Author 1',
                'annotated_likes': 3
            },
            {
                'id': self.book_2.id,
                'name': 'War and Peace',
                'price': '1200.00',
                'author_name': 'Author 2',
                'annotated_likes': 2
            }
        ]
        print('Data', data)
        self.assertEquals(expected_data, data)
