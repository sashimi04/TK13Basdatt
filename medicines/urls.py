from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_medicines, name='list_medicines'),
    path('add/', views.add_medicine, name='add_medicine'),
    path('update-stock/', views.update_stock, name='update_stock'),
]