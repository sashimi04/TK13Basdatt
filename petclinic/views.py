# path=petclinic/views.py
from django.shortcuts import render
from .models import JenisHewan, Pemilik, HewanPeliharaan
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404

def dashboard(request):
    return render(request, 'dashboard.html')  # Pastikan template ini ada

def hewan_list(request):
    hewan_list = HewanPeliharaan.objects.all()
    pemilik_list = Pemilik.objects.all()
    jenis_hewan_list = JenisHewan.objects.all()
    
    # Debugging
    print("Debug - Hewan Peliharaan:")
    for hewan in hewan_list:
        print(f"ID: {hewan.id}, Nama: {hewan.nama}, Pemilik: {hewan.pemilik.nama}")
    
    context = {
        'hewan_list': hewan_list,
        'pemilik_list': pemilik_list,
        'jenis_hewan_list': jenis_hewan_list,
    }
    return render(request, 'hewan_list.html', context)

def jenis_hewan_list(request):
    jenis_list = JenisHewan.objects.all()
    
    # Debugging
    print("Debug - Jenis Hewan:")
    for jenis in jenis_list:
        print(f"ID: {jenis.id}, Nama: {jenis.nama}")
    
    return render(request, 'jenis_hewan_list.html', {'jenis_hewan_list': jenis_list})

# API endpoints for CRUD operations
@csrf_exempt
def api_hewan(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        hewan = HewanPeliharaan.objects.create(
            pemilik_id=data['pemilik'],
            jenis_id=data['jenis'],
            nama=data['nama'],
            tanggal_lahir=data['tanggal_lahir'],
            foto=data['foto']
        )
        return JsonResponse({'id': hewan.id, 'message': 'Created successfully'})
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        hewan = get_object_or_404(HewanPeliharaan, id=data['id'])
        hewan.pemilik_id = data['pemilik']
        hewan.jenis_id = data['jenis']
        hewan.nama = data['nama']
        hewan.tanggal_lahir = data['tanggal_lahir']
        hewan.foto = data['foto']
        hewan.save()
        return JsonResponse({'message': 'Updated successfully'})
    
    elif request.method == 'DELETE':
        hewan_id = request.GET.get('id')
        hewan = get_object_or_404(HewanPeliharaan, id=hewan_id)
        hewan.delete()
        return JsonResponse({'message': 'Deleted successfully'})

@csrf_exempt
def api_jenis_hewan(request, id=None):
    if request.method == 'DELETE':
        jenis = get_object_or_404(JenisHewan, id=id)
        jenis.delete()
        return JsonResponse({'message': 'Deleted successfully'})