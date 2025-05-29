from django.urls import path
from . import views

urlpatterns = [
    path('vaccines/', views.list_vaccine, name='list_vaccine'),
    path('vaccines/create/', views.create_vaccine, name='create_vaccine'),
    path('vaccines/<str:vaccine_id>/update/', views.update_vaccine, name='update_vaccine'),
    path('vaccines/<str:vaccine_id>/update-stock/', views.update_vaccine_stock, name='update_vaccine_stock'),
    path('vaccines/<str:vaccine_id>/delete/', views.delete_vaccine, name='delete_vaccine'),
    
    path('vaccinations/', views.list_vaccination, name='list_vaccination'),
    path('vaccinations/create/', views.create_vaccination, name='create_vaccination'),
    path('vaccinations/<int:vaccination_id>/update/', views.update_vaccination, name='update_vaccination'),
    path('vaccinations/<int:vaccination_id>/delete/', views.delete_vaccination, name='delete_vaccination'),
    
    path('clients/', views.list_client, name='list_client'),
    path('clients/<int:client_id>/', views.detail_client, name='detail_client'),
]