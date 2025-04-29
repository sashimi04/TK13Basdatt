from django.core.management.base import BaseCommand
from petclinic.models import JenisHewan, Pemilik, HewanPeliharaan
from datetime import date

class Command(BaseCommand):
    help = 'Adds dummy data to the database'

    def handle(self, *args, **kwargs):
        # Create dummy jenis hewan
        jenis_kucing = JenisHewan.objects.create(nama='Kucing')
        jenis_anjing = JenisHewan.objects.create(nama='Anjing')
        jenis_burung = JenisHewan.objects.create(nama='Burung')

        # Create dummy pemilik
        pemilik1 = Pemilik.objects.create(
            nama='John Doe',
            email='john@example.com'
        )
        pemilik2 = Pemilik.objects.create(
            nama='Jane Smith',
            email='jane@example.com'
        )

        # Create dummy hewan peliharaan
        HewanPeliharaan.objects.create(
            pemilik=pemilik1,
            jenis=jenis_kucing,
            nama='Whiskers',
            tanggal_lahir=date(2020, 1, 1),
            foto='https://placekitten.com/200/200'
        )
        HewanPeliharaan.objects.create(
            pemilik=pemilik2,
            jenis=jenis_anjing,
            nama='Buddy',
            tanggal_lahir=date(2019, 6, 15),
            foto='https://placedog.net/200/200'
        )

        self.stdout.write(self.style.SUCCESS('Successfully added dummy data')) 