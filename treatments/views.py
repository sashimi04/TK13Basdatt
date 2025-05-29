from django.shortcuts import render
from django.db import connection

def list_treatment(request):
    search_query = request.GET.get('search', '')

    with connection.cursor() as cursor:
        if search_query:
            cursor.execute(
                "SELECT kode_perawatan, nama_perawatan, biaya_perawatan FROM perawatan WHERE nama_perawatan LIKE %s ORDER BY nama_perawatan ASC",
                [f'%{search_query}%']
            )
        else:
            cursor.execute("SELECT kode_perawatan, nama_perawatan, biaya_perawatan FROM perawatan ORDER BY nama_perawatan ASC")

        # Pindahkan fetchall() ke dalam blok with
        rows = cursor.fetchall()

    treatments = [
        {'kode': row[0], 'nama': row[1], 'biaya': row[2]}
        for row in rows
    ]

    return render(request, 'ListTreatment.html', {
        'treatments': treatments,
        'search_query': search_query
    })