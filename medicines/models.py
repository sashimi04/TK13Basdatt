from django.db import models
import uuid

# Create your models here.


class Obat(models.Model):
    kode = models.CharField(max_length=10, primary_key=True)
    nama = models.CharField(max_length=100)
    harga = models.IntegerField()
    stok = models.IntegerField()
    dosis = models.TextField()

    def __str__(self):
        return self.nama