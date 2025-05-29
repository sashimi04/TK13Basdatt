from django.db import models
import uuid

# Create your models here.

class User(models.Model):
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=128)
    alamat = models.TextField()
    nomor_telepon = models.CharField(max_length=20)

    def __str__(self):
        return self.email

class Pegawai(models.Model):
    no_pegawai = models.CharField(primary_key=True, max_length=20)
    tanggal_mulai_kerja = models.DateField()
    tanggal_akhir_kerja = models.DateField(null=True, blank=True)
    email_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.no_pegawai

class Klien(models.Model):
    no_identitas = models.CharField(primary_key=True, max_length=20)
    tanggal_registrasi = models.DateField()
    email = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.no_identitas

class Individu(models.Model):
    no_identitas_klien = models.OneToOneField(Klien, primary_key=True, on_delete=models.CASCADE)
    nama_depan = models.CharField(max_length=50)
    nama_tengah = models.CharField(max_length=50, null=True, blank=True)
    nama_belakang = models.CharField(max_length=50)

    def get_full_name(self):
        names = [self.nama_depan]
        if self.nama_tengah:
            names.append(self.nama_tengah)
        names.append(self.nama_belakang)
        return ' '.join(names)

    def __str__(self):
        return self.get_full_name()

class Perusahaan(models.Model):
    no_identitas_klien = models.OneToOneField(Klien, primary_key=True, on_delete=models.CASCADE)
    nama_perusahaan = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_perusahaan

class FrontDesk(models.Model):
    no_front_desk = models.CharField(primary_key=True, max_length=20)
    no_pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE)

    def __str__(self):
        return self.no_front_desk

class TenagaMedis(models.Model):
    no_tenaga_medis = models.CharField(primary_key=True, max_length=20)
    no_pegawai = models.ForeignKey(Pegawai, on_delete=models.CASCADE)
    no_izin_praktik = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.no_tenaga_medis

class PerawatHewan(models.Model):
    no_perawat_hewan = models.CharField(primary_key=True, max_length=20)
    no_tenaga_medis = models.ForeignKey(TenagaMedis, on_delete=models.CASCADE)

    def __str__(self):
        return self.no_perawat_hewan

class DokterHewan(models.Model):
    no_dokter_hewan = models.CharField(primary_key=True, max_length=20)
    no_tenaga_medis = models.ForeignKey(TenagaMedis, on_delete=models.CASCADE)

    def __str__(self):
        return self.no_dokter_hewan

class SertifikatKompetensi(models.Model):
    no_sertifikat_kompetensi = models.CharField(primary_key=True, max_length=50)
    no_tenaga_medis = models.ForeignKey(TenagaMedis, on_delete=models.CASCADE)
    nama_sertifikat = models.CharField(max_length=100)

    def __str__(self):
        return self.nama_sertifikat

class JadwalPraktik(models.Model):
    no_dokter_hewan = models.ForeignKey(DokterHewan, on_delete=models.CASCADE)
    hari = models.CharField(max_length=10)
    jam = models.TimeField()

    class Meta:
        unique_together = ('no_dokter_hewan', 'hari', 'jam')

    def __str__(self):
        return f"{self.no_dokter_hewan} - {self.hari} {self.jam}"

class JenisHewan(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    nama_jenis = models.CharField(max_length=50)

    class Meta:
        db_table = 'jenis_hewan'
        managed = False  # agar Django tidak mengubah tabel

    def __str__(self):
        return self.nama_jenis

class Hewan(models.Model):
    nama = models.CharField(max_length=50, primary_key=True)
    no_identitas_klien = models.UUIDField()
    id_jenis = models.ForeignKey('JenisHewan', db_column='id_jenis', on_delete=models.CASCADE)
    tanggal_lahir = models.DateField()
    url_foto = models.CharField(max_length=255)

    class Meta:
        db_table = 'hewan'
        unique_together = (('nama', 'no_identitas_klien'),)
        managed = False

    def __str__(self):
        return self.nama

class Kunjungan(models.Model):
    id_kunjungan = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_hewan = models.ForeignKey(Hewan, on_delete=models.CASCADE)
    no_identitas_klien = models.ForeignKey(Klien, on_delete=models.CASCADE)
    no_front_desk = models.ForeignKey(FrontDesk, on_delete=models.CASCADE)
    no_perawat_hewan = models.ForeignKey(PerawatHewan, on_delete=models.CASCADE)
    no_dokter_hewan = models.ForeignKey(DokterHewan, on_delete=models.CASCADE)
    kode_vaksin = models.ForeignKey('Vaksin', on_delete=models.SET_NULL, null=True, blank=True)
    tipe_kunjungan = models.CharField(max_length=50)
    timestamp_awal = models.DateTimeField()
    timestamp_akhir = models.DateTimeField(null=True, blank=True)
    suhu = models.DecimalField(max_digits=4, decimal_places=2)
    berat_badan = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.id_kunjungan)

class KunjunganKeperawatan(models.Model):
    id_kunjungan = models.OneToOneField(Kunjungan, primary_key=True, on_delete=models.CASCADE)
    kode_perawatan = models.ForeignKey('Perawatan', on_delete=models.CASCADE)
    catatan = models.TextField()

    def __str__(self):
        return str(self.id_kunjungan)

class Perawatan(models.Model):
    kode_perawatan = models.CharField(primary_key=True, max_length=20)
    nama_perawatan = models.CharField(max_length=100)
    biaya_perawatan = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nama_perawatan

class PerawatanObat(models.Model):
    kode_perawatan = models.ForeignKey(Perawatan, on_delete=models.CASCADE)
    kode_obat = models.ForeignKey('Obat', on_delete=models.CASCADE)
    kuantitas_obat = models.IntegerField()

    class Meta:
        unique_together = ('kode_perawatan', 'kode_obat')

    def __str__(self):
        return f"{self.kode_perawatan} - {self.kode_obat}"

class Obat(models.Model):
    kode = models.CharField(primary_key=True, max_length=20)
    nama = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.IntegerField()
    dosis = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Vaksin(models.Model):
    kode = models.CharField(primary_key=True, max_length=20)
    nama = models.CharField(max_length=100)
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.IntegerField()

    def __str__(self):
        return self.nama
