# path=tk013/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Arahkan ke dashboard sebagai halaman utama
    path('', include('petclinic.urls')),  # Mengarahkan ke urls.py di aplikasi petclinic
]