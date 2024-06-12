from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        return HttpResponse(
            render_to_string('registration/signup_success.html', {'user': self.object})
        )

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.profile
    
    def form_valid(self, form):
        response = super().form_valid(form)
        return HttpResponse(
            render_to_string('profile_success.html', {'profile': self.object})
        )

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

class AccountView(TemplateView):
    template_name = 'account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_form'] = CustomUserCreationForm()
        context['login_form'] = AuthenticationForm()  # Formulaire de connexion
        return context

class LandingPageView(LoginRequiredMixin, TemplateView):
    template_name = 'landing.html'