from django.db import models
from django.contrib.auth.models import User
from .constants import *

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='books/media/books_images')
    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class BorrowBook(models.Model):
    user = models.ForeignKey(User, related_name="book_borrowed",  on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book',related_name="book", on_delete=models.CASCADE)
    transation = models.ForeignKey('accounts.Transaction',related_name="transation", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=None)
    returned_quantity = models.PositiveIntegerField(default=0)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True, default=None)
    borrow_price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.id}-{self.book}-{self.user}"