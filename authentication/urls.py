# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Registration
    path('register/', views.register_type, name='register_type'),
    path('register/individual/', views.register_individual, name='register_individual'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/veterinarian/', views.register_veterinarian, name='register_vet'),
    path('register/nurse/', views.register_nurse, name='register_nurse'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
    path('hewan/', views.hewan_list, name='hewan_list'),
    path('jenis-hewan/', views.jenis_hewan_list, name='jenis_hewan_list'),
    path('jenis-hewan/create/', views.create_jenis_hewan, name='create_jenis_hewan'),
    path('jenis-hewan/update/<uuid:id_jenis>/', views.update_jenis_hewan, name='update_jenis_hewan'),
    path('jenis-hewan/delete/<uuid:id_jenis>/', views.delete_jenis_hewan, name='delete_jenis_hewan'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('update-password/', views.update_password, name='update_password'),

]