from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_type, name='register_type'),
    path('register/individual/', views.register_individual, name='register_individual'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/veterinarian/', views.register_veterinarian, name='register_veterinarian'),
    path('register/nurse/', views.register_nurse, name='register_nurse'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-password/', views.update_password, name='update_password'),
    
    # Klien URLs
    path('kelola-hewan/', views.kelola_hewan, name='kelola_hewan'),
    path('daftar-kunjungan/', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('daftar-vaksinasi/', views.daftar_vaksinasi, name='daftar_vaksinasi'),
    
    # Front Desk URLs
    path('kelola-jenis-hewan/', views.kelola_jenis_hewan, name='kelola_jenis_hewan'),
    path('kelola-kunjungan/', views.kelola_kunjungan, name='kelola_kunjungan'),
    path('daftar-klien/', views.daftar_klien, name='daftar_klien'),
    
    # Dokter Hewan URLs
    path('daftar-jenis-hewan/', views.daftar_jenis_hewan, name='daftar_jenis_hewan'),
    path('perawatan-hewan/', views.perawatan_hewan, name='perawatan_hewan'),
    path('manajemen-obat/', views.manajemen_obat, name='manajemen_obat'),
    path('manajemen-perawatan/', views.manajemen_perawatan, name='manajemen_perawatan'),
    path('pemberian-obat/', views.pemberian_obat, name='pemberian_obat'),
    path('manajemen-vaksinasi/', views.manajemen_vaksinasi, name='manajemen_vaksinasi'),
    
    # Perawat URLs
    path('manajemen-vaksin/', views.manajemen_vaksin, name='manajemen_vaksin'),
    
    # Existing API URLs
    path('hewan/', views.hewan_list, name='hewan_list'),
    path('jenis_hewan/', views.jenis_hewan_list, name='jenis_hewan_list'),
    path('api/hewan/', views.api_hewan, name='api_hewan'),
    path('api/jenis-hewan/', views.api_jenis_hewan, name='api_jenis_hewan_list'),
    path('api/jenis-hewan/<str:id>/', views.api_jenis_hewan, name='api_jenis_hewan_detail'),
    path('api/klien/', views.api_klien, name='api_klien_list'),

    path('daftar-kunjungan/', views.daftar_kunjungan, name='daftar_kunjungan'),
    path('kelola-hewan/', views.kelola_hewan, name='kelola_hewan'),
    path('daftar-vaksinasi/', views.daftar_vaksinasi, name='daftar_vaksinasi'),
    
]