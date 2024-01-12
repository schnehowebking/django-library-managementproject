from django.shortcuts import get_object_or_404, render
from django.views.generic import *
from .forms import *
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.shortcuts import redirect
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string
from books.models import *

def send_passchange_email(user, subject, template):
    message = render_to_string(template, {
        'user' : user,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

def send_deposit_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount': amount
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')
    
    def form_valid(self,form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form)


class UserProfileView(LoginRequiredMixin, ListView):
    template_name = 'accounts/dashboard.html'
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        borrow_books = BorrowBook.objects.filter(user=self.request.user)
        context['borrow_books'] = borrow_books
        return context
    

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Password changed successfully.')
            send_passchange_email(request.user, "Password Changed", "accounts/change_password_mail.html")
            return redirect('profile')
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, './accounts/change_password.html', {'form': form})



@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

class UserLibraryAccountUpdateView(View):
    template_name = 'accounts/update_profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile') 
        return render(request, self.template_name, {'form': form})



class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'accounts/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):       
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
      
        account.balance += amount
        account.save(
            update_fields=[
                'balance'
            ]
        )
        
        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        send_deposit_email(self.request.user, amount, "Wallet Balance Added", "accounts/deposit_mail.html")

        return super().form_valid(form)
    
    
    

