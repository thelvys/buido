from django.urls import path, include
from .views import SignUpView, ProfileUpdateView, CustomLoginView, CustomLogoutView, AccountView, LandingPageView


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')), # Utilisation des URLs d'authentification intégrées
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', AccountView.as_view(), name='account'), 
    path('landing/', LandingPageView.as_view(), name='landing'),
    
]
