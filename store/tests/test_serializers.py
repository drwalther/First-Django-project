from django.contrib.auth.models import User
from django.db.models import Case, When, Count, Avg
from django_filters.compat import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create(username='test_user1',
                                          first_name='Paul', last_name='Smith')
        self.user_2 = User.objects.create(username='test_user2',
                                          first_name="Jerome", last_name='King')
        self.user_3 = User.objects.create(username='test_user3',
                                          first_name="Pietro",
                                          last_name="Jovannie")
        self.book_1 = Book.objects.create(name='Alice', price=1000,
                                          author_name='Author 1',
                                          owner=self.user_1)
        self.book_2 = Book.objects.create(name='War and Peace', price=1200,
                                          author_name='Author 2')

    def test_ok(self):
        UserBookRelation.objects.create(user=self.user_1, book=self.book_1,
                                        like=True, rate=5)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1,
                                        like=True, rate=5)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1,
                                        like=True, rate=4)

        UserBookRelation.objects.create(user=self.user_1, book=self.book_2,
                                        like=True, rate=4)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_2,
                                        like=True, rate=3)
        user_book_3 = UserBookRelation.objects.create(user=self.user_3,
                                                      book=self.book_2,
                                                      like=False)
        user_book_3.rate = 4
        user_book_3.save()
        books = Book.objects.all().annotate(annotated_likes=Count(
            Case(When(userbookrelation__like=True, then=1)))).select_related(
            'owner').prefetch_related('readers').order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': self.book_1.id,
                'name': 'Alice',
                'price': '1000.00',
                'author_name': 'Author 1',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'test_user1',
                'readers': [
                    {
                        'first_name': self.user_1.first_name,
                        'last_name': self.user_1.last_name
                    },
                    {
                        'first_name': self.user_2.first_name,
                        'last_name': self.user_2.last_name
                    },
                    {
                        'first_name': self.user_3.first_name,
                        'last_name': self.user_3.last_name
                    }
                ]
            },
            {
                'id': self.book_2.id,
                'name': 'War and Peace',
                'price': '1200.00',
                'author_name': 'Author 2',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': '',
                'readers': [
                    {
                        'first_name': self.user_1.first_name,
                        'last_name': self.user_1.last_name
                    },
                    {
                        'first_name': self.user_2.first_name,
                        'last_name': self.user_2.last_name
                    },
                    {
                        'first_name': self.user_3.first_name,
                        'last_name': self.user_3.last_name
                    }
                ]
            }
        ]

        self.assertEquals(expected_data, data)
