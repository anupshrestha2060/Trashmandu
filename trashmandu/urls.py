from django.contrib import admin
from django.urls import path, include
from collection import views as collection_views

urlpatterns = [
    path('', collection_views.home, name='home'),
    path('user/', include('userapp.urls')),
    path('collector/', include('collectorapp.urls')),
    path('adminapp/', include('adminapp.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
]
