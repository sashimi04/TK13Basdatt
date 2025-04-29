from django.shortcuts import render

# Create your views here.
def prescription_list(request):
    return render(request, 'ListPrescription.html', {})