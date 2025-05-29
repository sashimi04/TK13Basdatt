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
    path('register/veterinarian/', views.register_veterinarian, name='register_veterinarian'),
    path('register/nurse/', views.register_nurse, name='register_nurse'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
]