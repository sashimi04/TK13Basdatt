# path=petclinic/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Halaman utama adalah dashboard
    path('hewan/', views.hewan_list, name='hewan_list'),
    path('jenis_hewan/', views.jenis_hewan_list, name='jenis_hewan_list'),
]