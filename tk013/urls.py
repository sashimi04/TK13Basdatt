# path=tk013/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('auth/', include('authentication.urls')),

    # # Arahkan ke dashboard sebagai halaman utama
    # path('', include('petclinic.urls')),  # Mengarahkan ke urls.py di aplikasi petclinic
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('medicines/', include('medicines.urls')),
    path('treatments/', include('treatments.urls')),
]