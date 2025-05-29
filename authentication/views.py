from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
import json
from datetime import datetime
from uuid import uuid4
from django.db import transaction
from django.utils import timezone
from django.db import connection
from datetime import date

def index(request):
    """Home page with login and register options"""
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Email dan password harus diisi'
            })
        
        try:
            with connection.cursor() as cursor:
                # Check in user table first
                cursor.execute("""
                    SELECT email, password, nomor_telepon, alamat 
                    FROM users 
                    WHERE email = %s AND password = %s
                """, [email, password])  # Direct password comparison
                user_data = cursor.fetchone()
                
                if not user_data:
                    return render(request, 'login.html', {
                        'error': 'Email atau password salah'
                    })

                # Store user session
                request.session['user_email'] = email
                
                # Determine user type and store in session
                user_type = get_user_specific_type(email)
                request.session['specific_user_type'] = user_type
                
                messages.success(request, f'Selamat datang kembali!')
                return redirect('dashboard')
                
        except Exception as e:
            print(f"Login error: {str(e)}")  # For debugging
            return render(request, 'login.html', {
                'error': 'Terjadi kesalahan saat login'
            })
        

def register_type(request):
    """Registration type selection page"""
    return render(request, 'register_type.html')

def register_individual(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first-name')
        middle_name = request.POST.get('middle-name')
        last_name = request.POST.get('last-name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        tanggal_registrasi = timezone.now().date()

        # Validasi sederhana
        if not all([email, first_name, last_name, password, phone, address]):
            messages.error(request, "Semua field wajib diisi kecuali nama tengah.")
            return render(request, 'register_individual.html')

        try:
            with connection.cursor() as cursor:
                # Insert ke tabel users dan klien/individu sesuai struktur DB kamu
                cursor.execute("""
                    INSERT INTO users (email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, address, phone])
                cursor.execute("""
                    INSERT INTO klien (email, no_identitas, tanggal_registrasi)
                    VALUES (%s, gen_random_uuid(), %s)
                """, [email, tanggal_registrasi])
                cursor.execute("""
                    INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang)
                    VALUES (
                        (SELECT no_identitas FROM klien WHERE email=%s),
                        %s, %s, %s
                    )
                """, [email, first_name, middle_name, last_name])
            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Registrasi gagal: {e}")
            return render(request, 'register_individual.html')

    return render(request, 'register_individual.html')

def register_company(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        company_name = request.POST.get('company_name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        tanggal_registrasi = date.today()

        try:
            with connection.cursor() as cursor:
                # Insert ke tabel users
                cursor.execute("""
                    INSERT INTO users (email, password, nomor_telepon, alamat)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, phone, address])

                # Insert ke tabel klien
                no_identitas = str(uuid4())
                cursor.execute("""
                    INSERT INTO klien (no_identitas, email, tanggal_registrasi)
                    VALUES (%s, %s, %s)
                """, [no_identitas, email, tanggal_registrasi])

                # Insert ke tabel perusahaan
                cursor.execute("""
                    INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan)
                    VALUES (%s, %s)
                """, [no_identitas, company_name])

            messages.success(request, "Registrasi perusahaan berhasil. Silakan login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
            return render(request, 'register_company.html')
    return render(request, 'register_company.html')

@transaction.atomic
def register_veterinarian(request):
    if request.method == 'GET':
        return render(request, 'register_vet.html')
    elif request.method == 'POST':
        license_no = request.POST.get('license', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        hire_date = request.POST.get('hire_date', '').strip()
        address = request.POST.get('address', '').strip()
        cert_number = request.POST.get('cert_number', '').strip()
        cert_name = request.POST.get('cert_name', '').strip()
        day = request.POST.get('day', '').strip()
        time = request.POST.get('time', '').strip()

        if not all([license_no, email, password, phone, hire_date, address, cert_number, cert_name, day, time]):
            return render(request, 'register_vet.html', {
                'error': 'Semua field wajib diisi'
            })

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT Email FROM USER WHERE Email = %s", [email])
                if cursor.fetchone():
                    return render(request, 'register_vet.html', {
                        'error': 'Email sudah terdaftar'
                    })

                # Insert ke USER
                cursor.execute("""
                    INSERT INTO USER (Email, Password, Alamat, Nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, address, phone])

                pegawai_id = f"VET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO PEGAWAI (No_pegawai, Tanggal_mulai_kerja, Tanggal_akhir_kerja, Email_user)
                    VALUES (%s, %s, %s, %s)
                """, [pegawai_id, hire_date, None, email])

                medis_id = f"MED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO TENAGA_MEDIS (No_tenaga_medis, No_pegawai_hewan)
                    VALUES (%s, %s)
                """, [medis_id, pegawai_id])

                cursor.execute("""
                    INSERT INTO DOKTER_HEWAN (No_dokter_hewan, Nomor_izin_praktik)
                    VALUES (%s, %s)
                """, [medis_id, license_no])

                cursor.execute("""
                    INSERT INTO SERTIFIKAT_KOMPETENSI (Sertifikat_kompetensi, Nama_sertifikat)
                    VALUES (%s, %s)
                """, [cert_number, cert_name])

                cursor.execute("""
                    INSERT INTO JADWAL_PRAKTIK (No_dokter_hewan, Hari, Jam)
                    VALUES (%s, %s, %s)
                """, [medis_id, day, time])

            messages.success(request, 'Registrasi dokter hewan berhasil! Silakan login.')
            return redirect('login')

        except Exception as e:
            return render(request, 'register_vet.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

@transaction.atomic
def register_nurse(request):
    """Veterinary nurse registration"""
    if request.method == 'GET':
        return render(request, 'register_nurse.html')
    
    elif request.method == 'POST':
        license_no = request.POST.get('license', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        hire_date = request.POST.get('hire_date', '').strip()
        address = request.POST.get('address', '').strip()
        cert_number = request.POST.get('cert_number', '').strip()
        cert_name = request.POST.get('cert_name', '').strip()
        
        if not all([license_no, email, password, phone, hire_date, address, cert_number, cert_name]):
            return render(request, 'register_nurse.html', {
                'error': 'Semua field wajib diisi'
            })
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT Email FROM USER WHERE Email = %s", [email])
                if cursor.fetchone():
                    return render(request, 'register_nurse.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                # Insert into USER table (tanpa hash password)
                cursor.execute("""
                    INSERT INTO USER (Email, Password, Alamat, Nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, address, phone])
                
                # Insert into PEGAWAI table
                pegawai_id = f"NUR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO PEGAWAI (No_pegawai, Tanggal_mulai_kerja, Tanggal_akhir_kerja, Email_user)
                    VALUES (%s, %s, %s, %s)
                """, [pegawai_id, hire_date, None, email])
                
                # Insert into TENAGA_MEDIS table
                medis_id = f"MED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO TENAGA_MEDIS (No_tenaga_medis, No_pegawai_hewan)
                    VALUES (%s, %s)
                """, [medis_id, pegawai_id])
                
                # Insert into PERAWAT_HEWAN table
                cursor.execute("""
                    INSERT INTO PERAWAT_HEWAN (No_perawat_hewan, Nomor_izin_praktik)
                    VALUES (%s, %s)
                """, [medis_id, license_no])
                
                # Insert into SERTIFIKAT_KOMPETENSI table
                cursor.execute("""
                    INSERT INTO SERTIFIKAT_KOMPETENSI (Sertifikat_kompetensi, Nama_sertifikat)
                    VALUES (%s, %s)
                """, [cert_number, cert_name])
            
            messages.success(request, 'Registrasi perawat hewan berhasil! Silakan login.')
            return redirect('login')
        
        except Exception as e:
            return render(request, 'register_nurse.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })
        
@transaction.atomic  # Add this decorator
def register_frontdesk(request):
    if request.method == 'GET':
        return render(request, 'register_frontdesk.html')
        
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        hire_date = request.POST.get('hire-date', '').strip()
        address = request.POST.get('address', '').strip()
        
        # Validation
        if not all([email, password, phone, hire_date, address]):
            return render(request, 'register_frontdesk.html', {
                'error': 'Semua field harus diisi'
            })
                
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Check if email exists
                    cursor.execute("""
                        SELECT email FROM users WHERE email = %s
                    """, [email])
                    if cursor.fetchone():
                        return render(request, 'register_frontdesk.html', {
                            'error': 'Email sudah terdaftar'
                        })

                    # Generate UUID for pegawai ID
                    pegawai_id = str(uuid4())

                    # 1. Insert into user table - store password without hashing
                    cursor.execute("""
                        INSERT INTO users (email, password, nomor_telepon, alamat)
                        VALUES (%s, %s, %s, %s)
                    """, [email, password, phone, address])  # Remove hashed_password
                    
                    # 2. Insert into pegawai table
                    cursor.execute("""
                        INSERT INTO pegawai (no_pegawai, email_user, tanggal_mulai_kerja, tanggal_akhir_kerja)
                        VALUES (%s, %s, %s, NULL)
                    """, [pegawai_id, email, hire_date])
                    
                    # 3. Insert into front_desk table
                    cursor.execute("""
                        INSERT INTO front_desk (no_front_desk)
                        VALUES (%s)
                    """, [pegawai_id])
                    
                    messages.success(request, 'Registrasi front desk berhasil! Silakan login.')
                    return redirect('login')
                
            
        except Exception as e:
            print(f"Database error: {str(e)}")  # Add logging
            connection.rollback()  # Rollback on error
            return render(request, 'register_frontdesk.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })
        
def dashboard(request):
    if 'user_email' not in request.session:
        return redirect('login')
    
    email = request.session['user_email']
    user_type = request.session.get('specific_user_type', 'user')
    profile_data = {}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email, alamat, nomor_telepon 
            FROM users 
            WHERE email = %s
        """, [email])
        user_data = cursor.fetchone()
        if not user_data:
            return redirect('login')

        profile_data = {
            'email': user_data[0],
            'address': user_data[1],
            'phone': user_data[2],
            'user_type': user_type,
        }

        if user_type == 'individual':
            cursor.execute("""
                SELECT k.no_identitas, i.nama_depan, i.nama_tengah, i.nama_belakang, k.tanggal_registrasi
                FROM individu i
                JOIN klien k ON i.no_identitas_klien = k.no_identitas
                WHERE k.email = %s
            """, [email])
            data = cursor.fetchone()
            if data:
                profile_data.update({
                    'id_number': data[0],
                    'first_name': data[1],
                    'middle_name': data[2],
                    'last_name': data[3],
                    'join_date': data[4],
                })

        elif user_type == 'company':
            cursor.execute("""
                SELECT k.no_identitas, p.nama_perusahaan, k.tanggal_registrasi
                FROM perusahaan p
                JOIN klien k ON p.no_identitas_klien = k.no_identitas
                WHERE k.email = %s
            """, [email])
            data = cursor.fetchone()
            if data:
                profile_data.update({
                    'id_number': data[0],
                    'company_name': data[1],
                    'join_date': data[2],
                })

        elif user_type == 'frontdesk':
            cursor.execute("""
                SELECT p.no_pegawai, p.tanggal_mulai_kerja, p.tanggal_akhir_kerja
                FROM pegawai p
                WHERE p.email_user = %s
            """, [email])
            data = cursor.fetchone()
            if data:
                profile_data.update({
                    'id_number': data[0],
                    'join_date': data[1],
                    'end_date': data[2],
                })

        elif user_type == 'veterinarian':
            cursor.execute("""
                SELECT p.no_pegawai, p.tanggal_mulai_kerja, p.tanggal_akhir_kerja, dh.no_dokter_hewan
                FROM pegawai p
                JOIN tenaga_medis tm ON p.no_pegawai = tm.no_tenaga_medis
                JOIN dokter_hewan dh ON tm.no_tenaga_medis = dh.no_dokter_hewan
                WHERE p.email_user = %s
            """, [email])
            data = cursor.fetchone()
            if data:
                profile_data.update({
                    'id_number': data[0],
                    'join_date': data[1],
                    'end_date': data[2],
                    'license_no': data[3],
                })
            # Sertifikat
            cursor.execute("""
                SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
                FROM sertifikat_kompetensi sk
                JOIN tenaga_medis tm ON sk.no_sertifikat_kompetensi = tm.no_tenaga_medis::text
                JOIN pegawai p ON tm.no_tenaga_medis = p.no_pegawai
                WHERE p.email_user = %s
            """, [email])
            certs = cursor.fetchall()
            profile_data['certificates'] = [
                {'number': c[0], 'name': c[1]} for c in certs
            ]
            # Jadwal praktik
            cursor.execute("""
                SELECT hari, jam FROM jadwal_praktik
                WHERE no_dokter_hewan = (
                    SELECT dh.no_dokter_hewan
                    FROM pegawai p
                    JOIN tenaga_medis tm ON p.no_pegawai = tm.no_tenaga_medis
                    JOIN dokter_hewan dh ON tm.no_tenaga_medis = dh.no_dokter_hewan
                    WHERE p.email_user = %s
                )
            """, [email])
            schedules = cursor.fetchall()
            profile_data['schedules'] = [
                {'day': s[0], 'time': s[1]} for s in schedules
            ]

        elif user_type == 'nurse':
            cursor.execute("""
                SELECT p.no_pegawai, p.tanggal_mulai_kerja, p.tanggal_akhir_kerja
                FROM pegawai p
                JOIN tenaga_medis tm ON p.no_pegawai = tm.no_tenaga_medis
                JOIN perawat_hewan ph ON tm.no_tenaga_medis = ph.no_perawat_hewan
                WHERE p.email_user = %s
            """, [email])
            data = cursor.fetchone()
            if data:
                profile_data.update({
                    'id_number': data[0],
                    'join_date': data[1],
                    'end_date': data[2],
                })
            # Sertifikat
            cursor.execute("""
                SELECT sk.sertifikat_kompetensi, sk.nama_sertifikat
                FROM sertifikat_kompetensi sk
                JOIN tenaga_medis tm ON sk.no_sertifikat_kompetensi = tm.no_tenaga_medis
                JOIN pegawai p ON tm.no_tenaga_medis = p.no_pegawai
                WHERE p.email_user = %s
            """, [email])
            certs = cursor.fetchall()
            profile_data['certificates'] = [
                {'number': c[0], 'name': c[1]} for c in certs
            ]

    return render(request, '[p]dashboard.html', {'profile': profile_data})

def logout_view(request):
    """Logout user and clear session"""
    request.session.flush()
    return redirect('index')

# Helper functions
def get_user_specific_type(email):
    """Determine specific user type (individual/company/employee)"""
    with connection.cursor() as cursor:
        # Check if individual client
        cursor.execute("""
            SELECT 1 FROM KLIEN k 
            JOIN INDIVIDU i ON k.No_identitas = i.No_identitas_klien 
            WHERE k.Email = %s
        """, [email])
        if cursor.fetchone():
            return 'individual'
        
        # Check if company client
        cursor.execute("""
            SELECT 1 FROM KLIEN k 
            JOIN PERUSAHAAN p ON k.No_identitas = p.No_identitas_klien 
            WHERE k.Email = %s
        """, [email])
        if cursor.fetchone():
            return 'company'
        
        # Check if employee
        cursor.execute("""
            SELECT 1 FROM PEGAWAI WHERE Email_user = %s
        """, [email])
        if cursor.fetchone():
            return get_employee_specific_type(email)
    
    return 'user'

def get_employee_specific_type(email):
    with connection.cursor() as cursor:
        # Check if veterinarian
        cursor.execute("""
            SELECT 1 FROM PEGAWAI p
            JOIN TENAGA_MEDIS tm ON p.No_pegawai = tm.No_tenaga_medis
            JOIN DOKTER_HEWAN dh ON tm.No_tenaga_medis = dh.No_dokter_hewan
            WHERE p.Email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'veterinarian'
        
        # Check if nurse
        cursor.execute("""
            SELECT 1 FROM PEGAWAI p
            JOIN TENAGA_MEDIS tm ON p.No_pegawai = tm.No_tenaga_medis
            JOIN PERAWAT_HEWAN ph ON tm.No_tenaga_medis = ph.No_perawat_hewan
            WHERE p.Email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'nurse'
        
        # Check if front desk
        cursor.execute("""
            SELECT 1 FROM PEGAWAI p
            JOIN FRONT_DESK fd ON p.No_pegawai = fd.No_front_desk
            WHERE p.Email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'frontdesk'
    
    return 'employee'


def hewan_list(request):
    """Display list of animals with optional type filter"""
    if 'user_email' not in request.session:
        return redirect('login')
        
    try:
        jenis = request.GET.get('jenis')
        
        with connection.cursor() as cursor:
            if jenis:
                cursor.execute("""
                    SELECT h.id_hewan, h.nama_hewan, h.jenis_hewan, h.tanggal_lahir, h.warna
                    FROM hewan h
                    WHERE h.jenis_hewan = %s
                    ORDER BY h.nama_hewan
                """, [jenis])
            else:
                cursor.execute("""
                    SELECT h.id_hewan, h.nama_hewan, h.jenis_hewan, h.tanggal_lahir, h.warna
                    FROM hewan h
                    ORDER BY h.nama_hewan
                """)
            
            hewan_list = cursor.fetchall()
            hewan = [
                {
                    'id': row[0],
                    'nama': row[1],
                    'jenis': row[2],
                    'tanggal_lahir': row[3],
                    'warna': row[4]
                }
                for row in hewan_list
            ]
            
        return render(request, 'hewan_list.html', {
            'hewan': hewan,
            'selected_jenis': jenis
        })
        
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('dashboard')
    

from uuid import uuid4

def jenis_hewan_list(request):
    if 'user_email' not in request.session:
        return redirect('login')
    user_type = request.session.get('specific_user_type', 'user')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_jenis, nama_jenis FROM jenis_hewan ORDER BY id_jenis
        """)
        jenis_list = cursor.fetchall()
        jenis_hewan = [{'id': row[0], 'nama': row[1]} for row in jenis_list]
    return render(request, 'jenis_hewan_list.html', {
        'jenis_hewan': jenis_hewan,
        'user_type': user_type
    })

@transaction.atomic
def create_jenis_hewan(request):
    if request.method == 'POST':
        nama_jenis = request.POST.get('nama_jenis')
        if not nama_jenis:
            messages.error(request, "Nama jenis wajib diisi.")
            return redirect('jenis_hewan_list')
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jenis_hewan (id_jenis, nama_jenis) VALUES (%s, %s)
            """, [str(uuid4()), nama_jenis])
        messages.success(request, "Jenis hewan berhasil ditambahkan.")
        return redirect('jenis_hewan_list')
    return render(request, 'jenis_hewan_create.html')

@transaction.atomic
def update_jenis_hewan(request, id_jenis):
    if request.method == 'POST':
        nama_jenis = request.POST.get('nama_jenis')
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE jenis_hewan SET nama_jenis=%s WHERE id_jenis=%s
            """, [nama_jenis, id_jenis])
        messages.success(request, "Jenis hewan berhasil diupdate.")
        return redirect('jenis_hewan_list')
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_jenis, nama_jenis FROM jenis_hewan WHERE id_jenis=%s", [id_jenis])
        row = cursor.fetchone()
    return render(request, 'jenis_hewan_update.html', {'id_jenis': row[0], 'nama_jenis': row[1]})

@transaction.atomic
def delete_jenis_hewan(request, id_jenis):
    # Cek apakah ada hewan yang memakai jenis ini
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM hewan WHERE jenis_hewan=%s", [id_jenis])
        if cursor.fetchone():
            messages.error(request, "Tidak bisa hapus, masih ada hewan memakai jenis ini.")
            return redirect('jenis_hewan_list')
        cursor.execute("DELETE FROM jenis_hewan WHERE id_jenis=%s", [id_jenis])
    messages.success(request, "Jenis hewan berhasil dihapus.")
    return redirect('jenis_hewan_list')    

@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        email = request.session.get('user_email')
        user_type = request.session.get('specific_user_type')
        try:
            with connection.cursor() as cursor:
                # Update data umum
                phone = request.POST.get('phone')
                address = request.POST.get('address')
                cursor.execute("""
                    UPDATE users SET nomor_telepon=%s, alamat=%s WHERE email=%s
                """, [phone, address, email])

                if user_type == 'individual':
                    first_name = request.POST.get('first_name')
                    middle_name = request.POST.get('middle_name')
                    last_name = request.POST.get('last_name')
                    cursor.execute("""
                        UPDATE individu SET nama_depan=%s, nama_tengah=%s, nama_belakang=%s
                        WHERE no_identitas_klien = (
                            SELECT no_identitas FROM klien WHERE email=%s
                        )
                    """, [first_name, middle_name, last_name, email])

                elif user_type == 'company':
                    company_name = request.POST.get('company_name')
                    cursor.execute("""
                        UPDATE perusahaan SET nama_perusahaan=%s
                        WHERE no_identitas_klien = (
                            SELECT no_identitas FROM klien WHERE email=%s
                        )
                    """, [company_name, email])

                elif user_type in ['veterinarian', 'nurse', 'frontdesk']:
                    join_date = request.POST.get('join_date')
                    end_date = request.POST.get('end_date')
                    cursor.execute("""
                        UPDATE pegawai SET tanggal_mulai_kerja=%s, tanggal_akhir_kerja=%s
                        WHERE email_user=%s
                    """, [join_date, end_date, email])

                    if user_type in ['veterinarian', 'nurse']:
                        cert_numbers = request.POST.getlist('cert_number[]')
                        cert_names = request.POST.getlist('cert_name[]')
                        cursor.execute("""
                            DELETE FROM sertifikat_kompetensi
                            WHERE no_sertifikat_kompetensi IN (
                                SELECT tm.no_tenaga_medis::text
                                FROM tenaga_medis tm
                                JOIN pegawai p ON tm.no_tenaga_medis = p.no_pegawai
                                WHERE p.email_user = %s
                            )
                        """, [email])
                        for num, name in zip(cert_numbers, cert_names):
                            if num and name:
                                cursor.execute("""
                                    INSERT INTO sertifikat_kompetensi
                                    (no_sertifikat_kompetensi, nama_sertifikat)
                                    VALUES (
                                        (SELECT tm.no_tenaga_medis::text
                                         FROM tenaga_medis tm
                                         JOIN pegawai p ON tm.no_tenaga_medis = p.no_pegawai
                                         WHERE p.email_user = %s
                                        ), %s
                                    )
                                """, [email, name])

                    if user_type == 'veterinarian':
                        days = request.POST.getlist('schedule_day[]')
                        times = request.POST.getlist('schedule_time[]')
                        cursor.execute("""
                            DELETE FROM jadwal_praktik
                            WHERE no_dokter_hewan = (
                                SELECT dh.no_dokter_hewan
                                FROM pegawai p
                                JOIN tenaga_medis tm ON p.no_pegawai = tm.no_tenaga_medis
                                JOIN dokter_hewan dh ON tm.no_tenaga_medis = dh.no_dokter_hewan
                                WHERE p.email_user = %s
                            )
                        """, [email])
                        for day, time in zip(days, times):
                            if day and time:
                                cursor.execute("""
                                    INSERT INTO jadwal_praktik (no_dokter_hewan, hari, jam)
                                    VALUES (
                                        (SELECT dh.no_dokter_hewan
                                         FROM pegawai p
                                         JOIN tenaga_medis tm ON p.no_pegawai = tm.no_tenaga_medis
                                         JOIN dokter_hewan dh ON tm.no_tenaga_medis = dh.no_dokter_hewan
                                         WHERE p.email_user = %s
                                        ), %s, %s
                                    )
                                """, [email, day, time])

            messages.success(request, "Profil berhasil diupdate.")
        except Exception as e:
            messages.error(request, f"Update profil gagal: {e}")
        return redirect('dashboard')
    return redirect('dashboard')

@transaction.atomic
def update_password(request):
    if request.method == 'POST':
        email = request.session.get('user_email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Password baru dan konfirmasi tidak cocok')
            return redirect('dashboard')

        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE email = %s", [email])
            row = cursor.fetchone()
            if not row or row[0] != old_password:
                messages.error(request, 'Password lama salah')
                return redirect('dashboard')

            cursor.execute("UPDATE users SET password = %s WHERE email = %s", [new_password, email])
            messages.success(request, 'Password berhasil diupdate')
            return redirect('dashboard')
    return redirect('dashboard')