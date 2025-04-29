# path=petclinic/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Halaman utama adalah dashboard
    path('hewan/', views.hewan_list, name='hewan_list'),
    path('jenis_hewan/', views.jenis_hewan_list, name='jenis_hewan_list'),
    path('api/hewan/', views.api_hewan, name='api_hewan'),
    path('api/jenis_hewan/<int:id>/', views.api_jenis_hewan, name='api_jenis_hewan'),
]