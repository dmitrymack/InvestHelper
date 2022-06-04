from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from accounts.forms import RegisterForm, LoginForm


class SignUpView(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('main')
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('main')


class MyLoginView(LoginView):
    form_class = LoginForm

    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('main')


def logout_user(request):
    logout(request)
    return redirect('main')
