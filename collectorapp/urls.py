from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CollectorLoginView.as_view(), name='collector-login'),
    path('dashboard/', views.collector_dashboard, name='collector-dashboard'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept-request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject-request'),
    path('logout/', views.collector_logout, name='collector-logout'),
    path('register/', views.collector_register, name='collector-register'),
    path('profile/', views.collector_profile, name='collector-profile'),
    # Verification endpoints removed — not used in current flow
]
