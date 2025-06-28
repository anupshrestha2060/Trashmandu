from django.contrib import admin
from django.urls import path, include
from collection import views as collection_views

urlpatterns = [
    path('', collection_views.home, name='home'),
    path('user/', include('userapp.urls')),        # cleaner URL: /user/login/
   path('collector/', include('collectorapp.urls')),
  # /collector/login/
    path('adminapp/', include('adminapp.urls')),   # keep 'adminapp' since 'admin/' is for Django admin
    path('admin/', admin.site.urls),
]
