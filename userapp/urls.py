from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='user-login'),
    path('register/', views.user_register, name='user-register'),
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('pickup-request/', views.pickup_request, name='pickup-request'),
    path('logout/', views.user_logout, name='user-logout'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
]
