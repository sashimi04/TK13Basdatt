from django.shortcuts import render

# Create your views here.
def treatment_list(request):
    return render(request, 'ListTreatment.html', {})