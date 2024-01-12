
from django.urls import path
from .views import *
 
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile_update/', UserLibraryAccountUpdateView.as_view(), name='profile_update' ),
    path('profile/', UserProfileView.as_view(), name='profile' ),
    path('change-password/', change_password, name='change_password'),
    path("deposit/", DepositMoneyView.as_view(), name="deposit_money"),
   
]