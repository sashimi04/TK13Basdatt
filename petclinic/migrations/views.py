from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Vaccine, Vaccination, Visit, Client

def list_vaccine(request):
    vaccines = Vaccine.objects.all()
    return render(request, 'list_list_vaccine.html', {'vaccines': vaccines})

def create_vaccine(request):
    if request.method == 'POST':
        try:
            vaccine = Vaccine(
                vaccine_id=request.POST['vaccine_id'],
                name=request.POST['nama'],
                price=request.POST['harga'],
                stock=request.POST['stok']
            )
            vaccine.save()
            return redirect('list_vaccine')
        except IntegrityError as e:
            messages.error(request, str(e))
    return render(request, 'create_list_vaccine.html')

def update_vaccine(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, vaccine_id=vaccine_id)
    if request.method == 'POST':
        vaccine.name = request.POST['nama']
        vaccine.price = request.POST['harga']
        vaccine.save()
        return redirect('list_vaccine')
    return render(request, 'update_list_vaccine.html', {'vaccine': vaccine})

def update_vaccine_stock(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, vaccine_id=vaccine_id)
    if request.method == 'POST':
        vaccine.stock = request.POST['stok']
        vaccine.save()
        return redirect('list_vaccine')
    return render(request, 'update_stock_list_vaccine.html', {'vaccine': vaccine})

def delete_vaccine(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, vaccine_id=vaccine_id)
    if request.method == 'POST':
        try:
            vaccine.delete()
            return redirect('list_vaccine')
        except IntegrityError as e:
            messages.error(request, "Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi")
            return render(request, 'delete_list_vaccine.html', {'vaccine': vaccine, 'cannot_delete': True})
    
    used_in_vaccination = Vaccination.objects.filter(vaccine=vaccine).exists()
    return render(request, 'delete_list_vaccine.html', {
        'vaccine': vaccine, 
        'cannot_delete': used_in_vaccination
    })

def list_vaccination(request):
    vaccinations = Vaccination.objects.select_related('visit', 'vaccine').all()
    return render(request, 'list_list_vaccination.html', {'vaccinations': vaccinations})

def create_vaccination(request):
    if request.method == 'POST':
        try:
            visit = get_object_or_404(Visit, visit_id=request.POST['kunjungan'])
            vaccine = get_object_or_404(Vaccine, vaccine_id=request.POST['vaksin'].split(' - ')[0])
            
            vaccination = Vaccination(visit=visit, vaccine=vaccine)
            vaccination.save()
            return redirect('list_vaccination')
        except IntegrityError as e:
            if "tidak mencukupi" in str(e):
                messages.error(request, str(e))
            else:
                messages.error(request, "Vaksinasi sudah ada untuk kunjungan ini")
    
    visits = Visit.objects.all()
    vaccines = Vaccine.objects.all()
    return render(request, 'create_list_vaccination.html', {'visits': visits, 'vaccines': vaccines})

def update_vaccination(request, vaccination_id):
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)
    if request.method == 'POST':
        try:
            old_vaccine = vaccination.vaccine
            new_vaccine = get_object_or_404(Vaccine, vaccine_id=request.POST['vaksin'].split(' - ')[0])
            
            vaccination.vaccine = new_vaccine
            vaccination.save()
            return redirect('list_vaccination')
        except IntegrityError as e:
            messages.error(request, str(e))
    
    vaccines = Vaccine.objects.all()
    return render(request, 'update_list_vaccination.html', {'vaccination': vaccination, 'vaccines': vaccines})

def delete_vaccination(request, vaccination_id):
    vaccination = get_object_or_404(Vaccination, id=vaccination_id)
    if request.method == 'POST':
        vaccination.delete()
        return redirect('list_vaccination')
    return render(request, 'delete_list_vaccination.html', {'vaccination': vaccination})

def list_client(request):
    clients = Client.objects.all()
    return render(request, 'list_client.html', {'clients': clients})

def detail_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    pets = client.pet_set.all()
    return render(request, 'detail_client.html', {'client': client, 'pets': pets})