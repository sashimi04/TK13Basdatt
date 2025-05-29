from django.db import models
import uuid

# Create your models here.


class Perawatan(models.Model):
    kode = models.CharField(max_length=10, primary_key=True)
    nama = models.CharField(max_length=100)
    biaya = models.IntegerField()

    def __str__(self):
        return self.nama