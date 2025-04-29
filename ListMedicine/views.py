from django.shortcuts import render

# Create your views here.
def medicine_list(request):
    return render(request, 'ListMedicine.html', {})