from django.db import models

class Vaccine(models.Model):
    vaccine_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    
    def __str__(self):
        return f"{self.vaccine_id} - {self.name}"

class Client(models.Model):
    identity_number = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    client_type = models.CharField(max_length=20, choices=[('Individu', 'Individu'), ('Perusahaan', 'Perusahaan')])

class Pet(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    birth_date = models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

class Visit(models.Model):
    visit_id = models.CharField(max_length=10, primary_key=True)
    visit_date = models.DateField()
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)

class Vaccination(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('visit', 'vaccine')