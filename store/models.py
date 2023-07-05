from django.contrib.auth.models import User
from django.db import models




class Book(models.Model):
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=250, default='')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation',
                                     related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None,
                                 null=True)

    def __str__(self):
        return f'id {self.id}: {self.name}'


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'terrible'),
        (2, 'bad'),
        (3, 'normal'),
        (4, 'good'),
        (1, 'excellent')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user.username}, {self.book.name}, Rate: {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        super().save(*args, **kwargs)
        set_rating(self.book)
