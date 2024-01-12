from django.shortcuts import get_object_or_404, render
from django.views.generic import *
from books.models import *

# Create your views here.

class HomeView(TemplateView):
    template_name = 'index.html'

def homepage(request, category_slug=None):
    books = Book.objects.all()
    categories = Category.objects.all()
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        books = Book.objects.filter(category = category)
    return render(request, './index.html', {'books':books, 'categories':categories})