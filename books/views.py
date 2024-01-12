from django.shortcuts import get_object_or_404, redirect, render
from .models import *
from django.views.generic import *
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import Transaction
from accounts.constants import *
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.apps import apps
from .constants import *
from .forms import *

# Create your views here.
def send_borrowbook_email(user,book, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'book' : book,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

def book_list(request, category_slug=None):
    books = Book.objects.all()
    categories = Category.objects.all()
    if category_slug is not None:
        category = Category.objects.get(slug = category_slug)
        books = Book.objects.filter(category = category)
    return render(request, './books/book_list.html', {'books':books, 'categories':categories})


class BookDetailsPageView(DetailView):
    model = Book
    template_name = './books/book_details.html'
    pk_url_kwarg = 'book_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        reviews = book.reviews.all()
        user_has_borrowed_book = BorrowBook.objects.filter(user=self.request.user, book=book).first()
        # print(user_has_borrowed_book.status)
        can_add_review = False
        if user_has_borrowed_book:
            can_add_review = user_has_borrowed_book.status == 'Returned'

        review_form = ReviewForm()
        context['reviews'] = reviews
        context['can_add_review'] = can_add_review
        # print(context['can_add_review'])
        context['review_form'] = review_form
        return context


@method_decorator(login_required, name='dispatch')
class BorrowBookView(View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        user_account = request.user.account

        if user_account.balance < book.price:
            messages.error(request, "Insufficient balance to borrow the book.")
            return redirect('bookDetailspage', book_id=book_id)

        borrow_price = book.price
        return_date = None

        transaction = Transaction.objects.create(
            account=user_account,
            amount=-borrow_price,
            transaction_type=BORROW,
            balance_after_transaction = user_account.balance - borrow_price
        )

        

        borrow_entry = BorrowBook.objects.create(
            user=request.user,
            book=book,
            transation=transaction,
            borrow_date=timezone.now(),
            return_date=return_date,
            borrow_price=borrow_price,
            status=BORROWED
        )


        user_account.balance -= borrow_price
        book.quantity -=1
        book.save()
        
        user_account.borrowed_books.add(borrow_entry)
        user_account.save()

        transaction.save()

        messages.success(request, "Book borrowed successfully.")
        send_borrowbook_email(request.user, book, "Borrowed Book Successfully", "books/borrowbook_mail.html")
        return redirect('profile')


@method_decorator(login_required, name='dispatch')
class ReturnBookView(View):
    def post(self, request, borrow_id):
        borrow_entry = get_object_or_404(BorrowBook, id=borrow_id, user=request.user, status=BORROWED)
        book = get_object_or_404(Book, id=borrow_entry.book_id)
        user_account = request.user.account
        return_amount = borrow_entry.borrow_price

        borrow_entry.status = RETURNED
        borrow_entry.returned_quantity += 1
        borrow_entry.return_date = timezone.now()
        book.quantity += 1
        book.save()
        borrow_entry.save()


        user_account.balance += return_amount
        user_account.save()

        Transaction.objects.create(
            account=user_account,
            amount=return_amount,
            balance_after_transaction=user_account.balance,
            transaction_type=RETURN,
        )

        messages.success(request, "Book returned successfully.")
        return redirect('profile') 




@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'Review added successfully.')
            return redirect('bookDetailspage', book_id=book_id)
        else:
            messages.error(request, 'Error adding review. Please check your input.')
            return redirect('bookDetailspage', book_id=book_id)

    return redirect('bookDetailspage', book_id=book_id)