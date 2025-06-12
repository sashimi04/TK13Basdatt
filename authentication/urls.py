from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_alt'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_type, name='register_type'),
    path('register/individual/', views.register_individual, name='register_individual'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/veterinarian/', views.register_veterinarian, name='register_vet'),  # Changed this
    path('register/nurse/', views.register_nurse, name='register_nurse'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-password/', views.update_password, name='update_password'),
    path('hewan/', views.hewan_list, name='hewan_list'),
    path('jenis_hewan/', views.jenis_hewan_list, name='jenis_hewan_list'),
    path('api/hewan/', views.api_hewan, name='api_hewan'),
    path('api/jenis-hewan/', views.api_jenis_hewan, name='api_jenis_hewan_list'),
    path('api/jenis-hewan/<str:id>/', views.api_jenis_hewan, name='api_jenis_hewan_detail'),
    path('api/klien/', views.api_klien, name='api_klien_list'),
    path('daftar-vaksinasi/', views.daftar_vaksinasi, name='daftar_vaksinasi'),
    path('daftar-kunjungan/', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('kelola-hewan/', views.kelola_hewan, name='kelola_hewan'),
]