
from django.urls import path
from .views import *

urlpatterns = [
    path('',homepage, name='home'),
    path('<slug:category_slug>/', homepage, name='book_list_by_category_index'),
    # path('',HomeView.as_view(), name='home'),
]
