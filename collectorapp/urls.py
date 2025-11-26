from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.collector_dashboard, name='collector-dashboard'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept-request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject-request'),
    path('profile/', views.collector_profile, name='collector-profile'),
    path('register/', views.collector_register, name='collector-register'),
    path('login/', views.collector_login, name='collector-login'),
    path('logout/', views.collector_logout, name='collector-logout'),
    path('verify/<uuid:token>/', views.verify_collector, name='verify-collector'),
    path('forgot-password/', views.collector_forgot_password, name='collector-forgot-password'),
    path('reset-password/<str:token>/', views.collector_reset_password, name='collector-reset-password'),
]
