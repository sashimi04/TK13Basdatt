from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
import json
from datetime import datetime

def index(request):
    """Home page with login and register options"""
    return render(request, 'index.html')

def login_view(request):
    """Login page and authentication logic"""
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Email dan password harus diisi'
            })
        
        with connection.cursor() as cursor:
            print(f"DEBUG: Trying to login with email: {email}")
            cursor.execute("""
                SELECT email, password, nomor_telepon, alamat 
                FROM users 
                WHERE email = %s
            """, [email])
            user_data = cursor.fetchone()
            print(f"DEBUG: User data found: {user_data}")
            
            if user_data:
                print(f"DEBUG: Checking password: {password} vs {user_data[1]}")
                
                password_check_hashed = check_password(password, user_data[1])
                password_check_plain = (password == user_data[1])
                
                print(f"DEBUG: Hashed password check result: {password_check_hashed}")
                print(f"DEBUG: Plain text password check result: {password_check_plain}")
                
                if password_check_hashed or password_check_plain:
                    print("DEBUG: Login successful, setting session")
                    request.session['user_email'] = email
                    request.session['user_type'] = 'user'
                    
                    user_type = get_user_specific_type(email)
                    request.session['specific_user_type'] = user_type
                    print(f"DEBUG: User type: {user_type}")
                    
                    print("DEBUG: About to redirect to dashboard")
                    return redirect('/')
            
            cursor.execute("""
                SELECT email_user, tanggal_mulai_kerja, tanggal_akhir_kerja 
                FROM pegawai 
                WHERE email_user = %s
            """, [email])
            pegawai_data = cursor.fetchone()
            
            if pegawai_data:
                cursor.execute("""
                    SELECT password FROM users WHERE email = %s
                """, [email])
                user_pass = cursor.fetchone()
                
                if user_pass:
                    password_check_hashed = check_password(password, user_pass[0])
                    password_check_plain = (password == user_pass[0])
                    
                    if password_check_hashed or password_check_plain:
                        request.session['user_email'] = email
                        request.session['user_type'] = 'pegawai'
                        
                        employee_type = get_employee_specific_type(email)
                        request.session['specific_user_type'] = employee_type
                        
                        return redirect('/')
        
        print("DEBUG: Login failed - invalid credentials")
        return render(request, 'login.html', {
            'error': 'Email atau password salah. Silakan coba lagi.'
        })

def register_type(request):
    """Registration type selection page"""
    return render(request, 'register_type.html')

def register_individual(request):
    """Individual client registration"""
    if request.method == 'GET':
        return render(request, 'register_individual.html')
    
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first-name', '').strip()
        middle_name = request.POST.get('middle-name', '').strip()
        last_name = request.POST.get('last-name', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        if not all([email, first_name, last_name, password, phone, address]):
            return render(request, 'register_individual.html', {
                'error': 'Semua field wajib diisi kecuali nama tengah'
            })
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM users WHERE email = %s', [email])
                if cursor.fetchone():
                    return render(request, 'register_individual.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                print(f"DEBUG: Registration - Original password: {password}")
                print(f"DEBUG: Registration - Hashed password: {hashed_password}")
                
                klien_id = f"IND-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                cursor.execute("""
                    INSERT INTO users (email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                cursor.execute("""
                    INSERT INTO klien (no_identitas, tanggal_registrasi, email)
                    VALUES (%s, %s, %s)
                """, [klien_id, datetime.now().date(), email])
                
                cursor.execute("""
                    INSERT INTO individu (no_identitas_klien, nama_depan, nama_tengah, nama_belakang)
                    VALUES (%s, %s, %s, %s)
                """, [klien_id, first_name, middle_name, last_name])
                
                print(f"DEBUG: Registration successful for {email}")
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('/login/')
            
        except Exception as e:
            print(f"DEBUG: Registration error: {str(e)}")
            return render(request, 'register_individual.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def register_company(request):
    """Company client registration"""
    if request.method == 'GET':
        return render(request, 'register_company.html')
    
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        company_name = request.POST.get('company-name', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        if not all([email, company_name, password, phone, address]):
            return render(request, 'register_company.html', {
                'error': 'Semua field wajib diisi'
            })
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM users WHERE email = %s', [email])
                if cursor.fetchone():
                    return render(request, 'register_company.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                
                cursor.execute("""
                    INSERT INTO users (email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                klien_id = f"COM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO klien (no_identitas, tanggal_registrasi, email)
                    VALUES (%s, %s, %s)
                """, [klien_id, datetime.now().date(), email])
                
                cursor.execute("""
                    INSERT INTO perusahaan (no_identitas_klien, nama_perusahaan)
                    VALUES (%s, %s)
                """, [klien_id, company_name])
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('/login/')
            
        except Exception as e:
            return render(request, 'register_company.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def register_veterinarian(request):
    """Veterinarian registration - FIXED"""
    if request.method == 'GET':
        return render(request, 'register_vet.html')
    
    elif request.method == 'POST':
        license_no = request.POST.get('license', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        hire_date = request.POST.get('hire-date', '').strip()
        address = request.POST.get('address', '').strip()
        cert_number = request.POST.get('cert-number', '').strip()
        cert_name = request.POST.get('cert-name', '').strip()
        day = request.POST.get('day', '').strip()
        time = request.POST.get('time', '').strip()
        
        if not all([license_no, email, password, phone, hire_date, address, 
                   cert_number, cert_name, day, time]):
            return render(request, 'register_vet.html', {
                'error': 'Semua field wajib diisi'
            })
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM users WHERE email = %s', [email])
                if cursor.fetchone():
                    return render(request, 'register_vet.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                
                cursor.execute("""
                    INSERT INTO users (email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                pegawai_id = f"VET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email_user)
                    VALUES (%s, %s, %s, %s)
                """, [pegawai_id, hire_date, None, email])
                
                # FIXED: Insert into tenaga_medis with correct columns
                medis_id = f"MED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik)
                    VALUES (%s, %s)
                """, [medis_id, license_no])
                
                # Insert into dokter_hewan
                cursor.execute("""
                    INSERT INTO dokter_hewan (no_dokter_hewan)
                    VALUES (%s)
                """, [medis_id])
                
                cursor.execute("""
                    INSERT INTO sertifikat_kompetensi (sertifikat_kompetensi, no_sertifikat_medis, nama_sertifikat)
                    VALUES (%s, %s, %s)
                """, [cert_number, f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}", cert_name])
                
                cursor.execute("""
                    INSERT INTO jadwal_praktik (hari, jam, no_dokter_hewan)
                    VALUES (%s, %s, %s)
                """, [day, time, medis_id])
            
            messages.success(request, 'Registrasi dokter hewan berhasil! Silakan login.')
            return redirect('/login/')
            
        except Exception as e:
            return render(request, 'register_vet.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def register_nurse(request):
    """Veterinary nurse registration - FIXED"""
    if request.method == 'GET':
        return render(request, 'register_nurse.html')
    
    elif request.method == 'POST':
        license_no = request.POST.get('license', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        hire_date = request.POST.get('hire-date', '').strip()
        address = request.POST.get('address', '').strip()
        cert_number = request.POST.get('cert-number', '').strip()
        cert_name = request.POST.get('cert-name', '').strip()
        
        if not all([license_no, email, password, phone, hire_date, address, 
                   cert_number, cert_name]):
            return render(request, 'register_nurse.html', {
                'error': 'Semua field wajib diisi'
            })
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM users WHERE email = %s', [email])
                if cursor.fetchone():
                    return render(request, 'register_nurse.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                
                cursor.execute("""
                    INSERT INTO users (email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                pegawai_id = f"NUR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO pegawai (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email_user)
                    VALUES (%s, %s, %s, %s)
                """, [pegawai_id, hire_date, None, email])
                
                # FIXED: Insert into tenaga_medis with correct columns
                medis_id = f"MED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO tenaga_medis (no_tenaga_medis, no_izin_praktik)
                    VALUES (%s, %s)
                """, [medis_id, license_no])
                
                # Insert into perawat_hewan
                cursor.execute("""
                    INSERT INTO perawat_hewan (no_perawat_hewan)
                    VALUES (%s)
                """, [medis_id])
                
                cursor.execute("""
                    INSERT INTO sertifikat_kompetensi (sertifikat_kompetensi, no_sertifikat_medis, nama_sertifikat)
                    VALUES (%s, %s, %s)
                """, [cert_number, f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}", cert_name])
            
            messages.success(request, 'Registrasi perawat hewan berhasil! Silakan login.')
            return redirect('/login/')
            
        except Exception as e:
            return render(request, 'register_nurse.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def register_frontdesk(request):
    if request.method == 'GET':
        return render(request, 'register_frontdesk.html')
        
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        hire_date = request.POST.get('hire-date', '').strip()
        address = request.POST.get('address', '').strip()
        
        if not all([email, password, phone, hire_date, address]):
            return render(request, 'register_frontdesk.html', {
                'error': 'Semua field harus diisi'
            })
            
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT email FROM users WHERE email = %s', [email])
                if cursor.fetchone():
                    return render(request, 'register_frontdesk.html', {
                        'error': 'Email sudah terdaftar'
                    })

                pegawai_id = f"FD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                hashed_password = make_password(password)
                cursor.execute("""
                    INSERT INTO users (email, password, nomor_telepon, alamat)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, phone, address])
                
                cursor.execute("""
                    INSERT INTO pegawai (no_pegawai, email_user, tanggal_mulai_kerja, tanggal_akhir_kerja)
                    VALUES (%s, %s, %s, NULL)
                """, [pegawai_id, email, hire_date])
                
                cursor.execute("""
                    INSERT INTO front_desk (no_front_desk)
                    VALUES (%s)
                """, [pegawai_id])
                
                messages.success(request, 'Registrasi front desk berhasil! Silakan login.')
                return redirect('/login/')
            
        except Exception as e:
            return render(request, 'register_frontdesk.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def dashboard(request):
    """Dashboard page - shows user profile information"""
    print(f"DEBUG: Dashboard accessed, session data: {dict(request.session)}")
    
    if 'user_email' not in request.session:
        print("DEBUG: No user_email in session, redirecting to login")
        return redirect('/login/')
    
    email = request.session['user_email']
    user_type = request.session.get('specific_user_type', 'user')
    print(f"DEBUG: Dashboard for user: {email}, type: {user_type}")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email, alamat, nomor_telepon 
            FROM users 
            WHERE email = %s
        """, [email])
        user_data = cursor.fetchone()
        
        if not user_data:
            print("DEBUG: User data not found in database")
            return redirect('/login/')
        
        profile_data = {
            'email': user_data[0],
            'address': user_data[1],
            'phone': user_data[2],
            'user_type': user_type,
            'name': 'User',
            'join_date': '',
            'license_no': '',
            'specialization': ''
        }
        
        if user_type == 'individual':
            cursor.execute("""
                SELECT i.nama_depan, i.nama_tengah, i.nama_belakang, k.tanggal_registrasi
                FROM individu i
                JOIN klien k ON i.no_identitas_klien = k.no_identitas
                WHERE k.email = %s
            """, [email])
            individual_data = cursor.fetchone()
            if individual_data:
                middle_name = f" {individual_data[1]}" if individual_data[1] else ""
                profile_data['name'] = f"{individual_data[0]}{middle_name} {individual_data[2]}"
                profile_data['join_date'] = individual_data[3]
        
        elif user_type == 'company':
            cursor.execute("""
                SELECT p.nama_perusahaan, k.tanggal_registrasi
                FROM perusahaan p
                JOIN klien k ON p.no_identitas_klien = k.no_identitas
                WHERE k.email = %s
            """, [email])
            company_data = cursor.fetchone()
            if company_data:
                profile_data['name'] = company_data[0]
                profile_data['join_date'] = company_data[1]
        
        elif user_type == 'veterinarian':
            cursor.execute("""
                SELECT p.tanggal_mulai_kerja
                FROM pegawai p
                WHERE p.email_user = %s
            """, [email])
            vet_data = cursor.fetchone()
            if vet_data:
                profile_data['name'] = f"dr. {email.split('@')[0].title()}"
                profile_data['join_date'] = vet_data[0]
        
        elif user_type == 'nurse':
            cursor.execute("""
                SELECT p.tanggal_mulai_kerja
                FROM pegawai p
                WHERE p.email_user = %s
            """, [email])
            nurse_data = cursor.fetchone()
            if nurse_data:
                profile_data['name'] = f"{email.split('@')[0].title()}"
                profile_data['join_date'] = nurse_data[0]
        
        elif user_type == 'frontdesk':
            cursor.execute("""
                SELECT p.tanggal_mulai_kerja
                FROM pegawai p
                WHERE p.email_user = %s
            """, [email])
            fd_data = cursor.fetchone()
            if fd_data:
                profile_data['name'] = f"{email.split('@')[0].title()}"
                profile_data['join_date'] = fd_data[0]
    
    print(f"DEBUG: Rendering dashboard with profile: {profile_data}")
    return render(request, 'dashboard.html', {'profile': profile_data})

def update_profile(request):
    """Update user profile"""
    if 'user_email' not in request.session:
        return redirect('/login/')
    
    email = request.session['user_email']
    user_type = request.session.get('specific_user_type', 'user')
    
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT email, alamat, nomor_telepon 
                FROM users 
                WHERE email = %s
            """, [email])
            user_data = cursor.fetchone()
            
            profile_data = {
                'email': user_data[0],
                'address': user_data[1],
                'phone': user_data[2],
                'user_type': user_type,
                'name': 'User',
                'first_name': '',
                'middle_name': '',
                'last_name': '',
                'company_name': '',
                'end_date': ''
            }
            
            if user_type == 'individual':
                cursor.execute("""
                    SELECT i.nama_depan, i.nama_tengah, i.nama_belakang
                    FROM individu i
                    JOIN klien k ON i.no_identitas_klien = k.no_identitas
                    WHERE k.email = %s
                """, [email])
                individual_data = cursor.fetchone()
                if individual_data:
                    profile_data['first_name'] = individual_data[0]
                    profile_data['middle_name'] = individual_data[1] or ''
                    profile_data['last_name'] = individual_data[2]
            
            elif user_type == 'company':
                cursor.execute("""
                    SELECT p.nama_perusahaan
                    FROM perusahaan p
                    JOIN klien k ON p.no_identitas_klien = k.no_identitas
                    WHERE k.email = %s
                """, [email])
                company_data = cursor.fetchone()
                if company_data:
                    profile_data['company_name'] = company_data[0]
            
            elif user_type in ['veterinarian', 'nurse', 'frontdesk']:
                cursor.execute("""
                    SELECT tanggal_akhir_kerja
                    FROM pegawai
                    WHERE email_user = %s
                """, [email])
                employee_data = cursor.fetchone()
                if employee_data and employee_data[0]:
                    profile_data['end_date'] = employee_data[0]
        
        return render(request, 'update_profile.html', {'profile': profile_data})
    
    elif request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET alamat = %s, nomor_telepon = %s 
                    WHERE email = %s
                """, [
                    request.POST.get('address'),
                    request.POST.get('phone'),
                    email
                ])
                
                if user_type == 'individual':
                    cursor.execute("""
                        UPDATE individu 
                        SET nama_depan = %s, nama_tengah = %s, nama_belakang = %s
                        WHERE no_identitas_klien = (
                            SELECT no_identitas FROM klien WHERE email = %s
                        )
                    """, [
                        request.POST.get('first_name'),
                        request.POST.get('middle_name', ''),
                        request.POST.get('last_name'),
                        email
                    ])
                    
                elif user_type == 'company':
                    cursor.execute("""
                        UPDATE perusahaan 
                        SET nama_perusahaan = %s
                        WHERE no_identitas_klien = (
                            SELECT no_identitas FROM klien WHERE email = %s
                        )
                    """, [
                        request.POST.get('company_name'),
                        email
                    ])
                    
                elif user_type in ['frontdesk', 'veterinarian', 'nurse']:
                    end_date = request.POST.get('end_date')
                    if end_date:
                        cursor.execute("""
                            UPDATE pegawai 
                            SET tanggal_akhir_kerja = %s
                            WHERE email_user = %s
                        """, [end_date, email])
            
            messages.success(request, 'Profile berhasil diperbarui!')
            return redirect('/')
            
        except Exception as e:
            messages.error(request, f'Gagal memperbarui profile: {str(e)}')
            return redirect('/update-profile/')

def update_password(request):
    """Update user password"""
    if 'user_email' not in request.session:
        return redirect('/login/')
    
    if request.method == 'GET':
        return render(request, 'update_password.html')
    
    elif request.method == 'POST':
        email = request.session['user_email']
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Password baru dan konfirmasi tidak cocok!')
            return render(request, 'update_password.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Password harus minimal 8 karakter!')
            return render(request, 'update_password.html')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT password FROM users WHERE email = %s
                """, [email])
                user_data = cursor.fetchone()
                
                if not user_data:
                    messages.error(request, 'User tidak ditemukan!')
                    return render(request, 'update_password.html')
                
                password_check_hashed = check_password(current_password, user_data[0])
                password_check_plain = (current_password == user_data[0])
                
                if not (password_check_hashed or password_check_plain):
                    messages.error(request, 'Password lama tidak benar!')
                    return render(request, 'update_password.html')
                
                hashed_password = make_password(new_password)
                cursor.execute("""
                    UPDATE users 
                    SET password = %s 
                    WHERE email = %s
                """, [hashed_password, email])
            
            messages.success(request, 'Password berhasil diperbarui!')
            return redirect('/')
            
        except Exception as e:
            messages.error(request, f'Gagal memperbarui password: {str(e)}')
            return render(request, 'update_password.html')

def logout_view(request):
    """Logout user and clear session"""
    request.session.flush()
    return redirect('/')

# Placeholder functions untuk API
def hewan_list(request):
    return HttpResponse("Hewan List - Under Development")

def jenis_hewan_list(request):
    return HttpResponse("Jenis Hewan List - Under Development")

def api_hewan(request):
    return JsonResponse({"message": "API Hewan - Under Development"})

def api_jenis_hewan(request, id=None):
    return JsonResponse({"message": "API Jenis Hewan - Under Development"})

def api_klien(request):
    return JsonResponse({"message": "API Klien - Under Development"})

# Helper functions - COMPLETELY FIXED
def get_user_specific_type(email):
    """Determine specific user type - COMPLETELY FIXED"""
    with connection.cursor() as cursor:
        # Check if user is a klien (individual or company)
        cursor.execute("""
            SELECT no_identitas FROM klien WHERE email = %s
        """, [email])
        klien_data = cursor.fetchone()
        
        if klien_data:
            klien_id = klien_data[0]
            # Check if individual
            cursor.execute("""
                SELECT 1 FROM individu WHERE no_identitas_klien = %s
            """, [klien_id])
            if cursor.fetchone():
                return 'individual'
            
            # Check if company
            cursor.execute("""
                SELECT 1 FROM perusahaan WHERE no_identitas_klien = %s
            """, [klien_id])
            if cursor.fetchone():
                return 'company'
        
        cursor.execute

        # Check if user is an employee
        cursor.execute("""
            SELECT no_pegawai FROM pegawai WHERE email_user = %s
        """, [email])
        pegawai_data = cursor.fetchone()
        
        if pegawai_data:
            return get_employee_specific_type(email)
    
    return 'user'
# Di views.py
def daftar_vaksinasi(request):
    if 'user_email' not in request.session:
        return redirect('/login/')
    return render(request, 'list_list_vaccine.html')

def daftar_kunjungan(request):
    if 'user_email' not in request.session:
        return redirect('/login/')
    return render(request, 'list_list_vaccination.html')

def kelola_hewan(request):
    if 'user_email' not in request.session:
        return redirect('/login/')
    return render(request, 'hewan_peliharaan.html')

def get_employee_specific_type(email):
   """Determine specific employee type - COMPLETELY FIXED based on actual schema"""
   with connection.cursor() as cursor:
       # Get pegawai ID first
       cursor.execute("""
           SELECT no_pegawai FROM pegawai WHERE email_user = %s
       """, [email])
       pegawai_data = cursor.fetchone()
       
       if not pegawai_data:
           return 'employee'
       
       pegawai_id = pegawai_data[0]
       
       # Check if front desk (direct relationship - pegawai_id maps to front_desk)
       cursor.execute("""
           SELECT 1 FROM front_desk WHERE no_front_desk = %s
       """, [pegawai_id])
       if cursor.fetchone():
           return 'frontdesk'
       
      
       cursor.execute("""
           SELECT no_dokter_hewan FROM dokter_hewan 
           WHERE no_dokter_hewan LIKE %s
       """, [f'MED-{pegawai_id.split("-")[1] if "-" in pegawai_id else ""}%'])
       if cursor.fetchone():
           return 'veterinarian'
       
       # Check if this user has perawat_hewan records  
       cursor.execute("""
           SELECT no_perawat_hewan FROM perawat_hewan 
           WHERE no_perawat_hewan LIKE %s
       """, [f'MED-{pegawai_id.split("-")[1] if "-" in pegawai_id else ""}%'])
       if cursor.fetchone():
           return 'nurse'
       
       
       email_prefix = email.split('@')[0]
       
       # Check dokter_hewan with various patterns
       cursor.execute("""
           SELECT 1 FROM dokter_hewan 
           WHERE no_dokter_hewan LIKE %s OR no_dokter_hewan LIKE %s
       """, [f'%{email_prefix}%', f'MED-%'])
       
       if cursor.fetchone():
           return 'veterinarian'
       
       # Check perawat_hewan with various patterns
       cursor.execute("""
           SELECT 1 FROM perawat_hewan 
           WHERE no_perawat_hewan LIKE %s OR no_perawat_hewan LIKE %s  
       """, [f'%{email_prefix}%', f'MED-%'])
       
       if cursor.fetchone():
           return 'nurse'
   
   return 'employee'