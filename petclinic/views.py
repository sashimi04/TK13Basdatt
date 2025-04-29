# path=petclinic/views.py
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')  # Pastikan template ini ada

def hewan_list(request):
    return render(request, 'hewan_list.html')  # Pastikan template ini ada

def jenis_hewan_list(request):
    return render(request, 'jenis_hewan_list.html')  # Pastikan template ini ada