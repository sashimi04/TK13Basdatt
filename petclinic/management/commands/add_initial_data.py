from django.core.management.base import BaseCommand
from petclinicc.models import JenisHewan, Pemilik, HewanPeliharaan
from datetime import date

class Command(BaseCommand):
    help = 'Adds initial data to the database'

    def handle(self, *args, **kwargs):
        # Create one jenis hewan
        jenis_kucing = JenisHewan.objects.create(
            nama='Kucing'
        )
        self.stdout.write(self.style.SUCCESS('Successfully added Jenis Hewan: Kucing'))

        # Create one pemilik
        pemilik = Pemilik.objects.create(
            nama='John Doe',
            email='john@example.com'
        )
        self.stdout.write(self.style.SUCCESS('Successfully added Pemilik: John Doe'))

        # Create one hewan peliharaan
        HewanPeliharaan.objects.create(
            pemilik=pemilik,
            jenis=jenis_kucing,
            nama='Whiskers',
            tanggal_lahir=date(2020, 1, 1),
            foto='https://placekitten.com/200/200'
        )
        self.stdout.write(self.style.SUCCESS('Successfully added Hewan: Whiskers')) 