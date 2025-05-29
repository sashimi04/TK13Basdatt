from django.shortcuts import render
from django.db import connection

def list_medicines(request):
    search_query = request.GET.get('search', '')

    with connection.cursor() as cursor:
        if search_query:
            cursor.execute(
                "SELECT kode, nama, harga, stok, dosis FROM obat WHERE nama LIKE %s ORDER BY nama ASC",
                [f'%{search_query}%']
            )
        else:
            cursor.execute("SELECT kode, nama, harga, stok, dosis FROM obat ORDER BY nama ASC")

        rows = cursor.fetchall()

    medicines = [
        {'kode': row[0], 'nama': row[1], 'harga': row[2], 'stok': row[3], 'dosis': row[4]}
        for row in rows
    ]

    return render(request, 'ListMedicine.html', {
        'medicines': medicines,
        'search_query': search_query
    })

def add_medicine(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok')
        dosis = request.POST.get('dosis')

        try:
            # Generate kode obat baru secara otomatis
            with connection.cursor() as cursor:
                # Cari kode obat terakhir
                cursor.execute("SELECT MAX(kode) FROM obat")
                max_kode = cursor.fetchone()[0]

                if max_kode:
                    # Ekstrak angka dari kode terakhir
                    last_num = int(re.search(r'\d+', max_kode).group())
                    new_num = last_num + 1
                else:
                    new_num = 1

                # Format kode baru (MED001, MED002, dst)
                new_kode = f'OB{new_num:03d}'

                # Insert obat baru
                cursor.execute(
                    "INSERT INTO obat (kode, nama, harga, stok, dosis) VALUES (%s, %s, %s, %s, %s)",
                    [new_kode, nama, harga, stok, dosis]
                )

            messages.success(request, f'Obat berhasil ditambahkan! Kode: {new_kode}')
            return redirect('list_medicines')
        except IntegrityError:
            messages.error(request, 'Terjadi kesalahan: Kode obat sudah terdaftar!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('list_medicines')

def update_stock(request):
    if request.method == 'POST':
        kode = request.POST.get('kode')
        new_stock = request.POST.get('new_stock')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE obat SET stok = %s WHERE kode = %s",
                    [new_stock, kode]
                )
                if cursor.rowcount == 0:
                    messages.error(request, 'Obat tidak ditemukan!')
                else:
                    messages.success(request, f'Stok obat berhasil diupdate!')
            return redirect('list_medicines')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('list_medicines')