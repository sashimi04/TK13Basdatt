from django.db import models

# Create your models here.

class JenisHewan(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Pemilik(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.nama

class HewanPeliharaan(models.Model):
    pemilik = models.ForeignKey(Pemilik, on_delete=models.CASCADE)
    jenis = models.ForeignKey(JenisHewan, on_delete=models.CASCADE)
    nama = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()
    foto = models.URLField()

    def __str__(self):
        return self.nama
