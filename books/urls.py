from django.urls import path, include
from .views import *
urlpatterns = [
    
    path('list/', book_list, name='book_list'),
    path('list/<slug:category_slug>/', book_list, name='book_list_by_category'),
    path('list/details/<int:book_id>/', BookDetailsPageView.as_view(), name="bookDetailspage"),
    path('list/details/<int:book_id>/add_review/', add_review, name='add_review'),
    path('borrow/<int:book_id>/', BorrowBookView.as_view(), name='borrow_book'),
    path('return/<int:borrow_id>/', ReturnBookView.as_view(), name='return_book'),
    # path('update-status/<int:borrow_id>/', UpdateStatusView.as_view(), name='update_status'),

]