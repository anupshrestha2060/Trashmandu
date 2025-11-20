# userapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='user-logout'),
     path('register/', views.user_register, name='user-register'),
    path('verify/<uuid:token>/', views.verify_user, name='user-verify'),
    path('dashboard/', views.user_dashboard, name='user-dashboard'),
    path('register/', views.user_register, name='user-register'),
    path('verify/<uuid:token>/', views.verify_user, name='verify-user'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset-password'),
]