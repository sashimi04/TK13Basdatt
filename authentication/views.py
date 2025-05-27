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
        
        # Check in USER table first
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Email, Password, Nomor_telepon, Alamat 
                FROM USER 
                WHERE Email = %s
            """, [email])
            user_data = cursor.fetchone()
            
            if user_data and check_password(password, user_data[1]):
                # Store user session
                request.session['user_email'] = email
                request.session['user_type'] = 'user'
                
                # Determine specific user type
                user_type = get_user_specific_type(email)
                request.session['specific_user_type'] = user_type
                
                return redirect('dashboard')
            
            # Check in PEGAWAI table
            cursor.execute("""
                SELECT Email_user, Tanggal_mulai_kerja, Tanggal_akhir_kerja 
                FROM PEGAWAI 
                WHERE Email_user = %s
            """, [email])
            pegawai_data = cursor.fetchone()
            
            if pegawai_data:
                # Get user data for password check
                cursor.execute("""
                    SELECT Password FROM USER WHERE Email = %s
                """, [email])
                user_pass = cursor.fetchone()
                
                if user_pass and check_password(password, user_pass[0]):
                    request.session['user_email'] = email
                    request.session['user_type'] = 'pegawai'
                    
                    # Determine specific employee type
                    employee_type = get_employee_specific_type(email)
                    request.session['specific_user_type'] = employee_type
                    
                    return redirect('dashboard')
        
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
        # Get form data
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first-name', '').strip()
        middle_name = request.POST.get('middle-name', '').strip()
        last_name = request.POST.get('last-name', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        # Validation
        if not all([email, first_name, last_name, password, phone, address]):
            return render(request, 'register_individual.html', {
                'error': 'Semua field wajib diisi kecuali nama tengah'
            })
        
        try:
            with connection.cursor() as cursor:
                # Check if email already exists
                cursor.execute("SELECT Email FROM USER WHERE Email = %s", [email])
                if cursor.fetchone():
                    return render(request, 'register_individual.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                # Hash password
                hashed_password = make_password(password)
                
                # Insert into USER table
                cursor.execute("""
                    INSERT INTO USER (Email, Password, Alamat, Nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                # Insert into KLIEN table
                cursor.execute("""
                    INSERT INTO KLIEN (No_identitas, Tanggal_registrasi, Email)
                    VALUES (%s, %s, %s)
                """, [f"IND-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                     datetime.now().date(), email])
                
                # Insert into INDIVIDU table
                cursor.execute("""
                    INSERT INTO INDIVIDU (No_identitas_klien, Nama_depan, Nama_tengah, Nama_belakang)
                    VALUES (%s, %s, %s, %s)
                """, [f"IND-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                     first_name, middle_name, last_name])
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
            
        except Exception as e:
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
                cursor.execute("SELECT Email FROM USER WHERE Email = %s", [email])
                if cursor.fetchone():
                    return render(request, 'register_company.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                
                # Insert into USER table
                cursor.execute("""
                    INSERT INTO USER (Email, Password, Alamat, Nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                # Insert into KLIEN table
                klien_id = f"COM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO KLIEN (No_identitas, Tanggal_registrasi, Email)
                    VALUES (%s, %s, %s)
                """, [klien_id, datetime.now().date(), email])
                
                # Insert into PERUSAHAAN table
                cursor.execute("""
                    INSERT INTO PERUSAHAAN (No_identitas_klien, Nama_perusahaan)
                    VALUES (%s, %s)
                """, [klien_id, company_name])
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')
            
        except Exception as e:
            return render(request, 'register_company.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def register_veterinarian(request):
    """Veterinarian registration"""
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
                cursor.execute("SELECT Email FROM USER WHERE Email = %s", [email])
                if cursor.fetchone():
                    return render(request, 'register_vet.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                
                # Insert into USER table
                cursor.execute("""
                    INSERT INTO USER (Email, Password, Alamat, Nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
                # Insert into PEGAWAI table
                cursor.execute("""
                    INSERT INTO PEGAWAI (No_pegawai, Tanggal_mulai_kerja, Tanggal_akhir_kerja, Email_user)
                    VALUES (%s, %s, %s, %s)
                """, [f"VET-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                     hire_date, None, email])
                
                # Insert into TENAGA_MEDIS table
                medis_id = f"MED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                cursor.execute("""
                    INSERT INTO TENAGA_MEDIS (No_tenaga_medis, No_pegawai_hewan)
                    VALUES (%s, %s)
                """, [medis_id, f"VET-{datetime.now().strftime('%Y%m%d%H%M%S')}"])
                
                # Insert into DOKTER_HEWAN table
                cursor.execute("""
                    INSERT INTO DOKTER_HEWAN (No_dokter_hewan, No_perawat_hewan)
                    VALUES (%s, %s)
                """, [f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}", medis_id])
                
                # Insert into SERTIFIKAT_KOMPETENSI table
                cursor.execute("""
                    INSERT INTO SERTIFIKAT_KOMPETENSI (Sertifikat_kompetensi, No_sertifikat_medis, Nama_sertifikat)
                    VALUES (%s, %s, %s)
                """, [cert_number, f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}", cert_name])
                
                # Insert into JADWAL_PRAKTIK table
                cursor.execute("""
                    INSERT INTO JADWAL_PRAKTIK (Hari, Jam, No_dokter_hewan)
                    VALUES (%s, %s, %s)
                """, [day, time, f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}"])
            
            messages.success(request, 'Registrasi dokter hewan berhasil! Silakan login.')
            return redirect('login')
            
        except Exception as e:
            return render(request, 'register_vet.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })

def register_nurse(request):
    """Veterinary nurse registration"""
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
                cursor.execute("SELECT Email FROM USER WHERE Email = %s", [email])
                if cursor.fetchone():
                    return render(request, 'register_nurse.html', {
                        'error': 'Email sudah terdaftar'
                    })
                
                hashed_password = make_password(password)
                
                # Insert into USER table
                cursor.execute("""
                    INSERT INTO USER (Email, Password, Alamat, Nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, address, phone])
                
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
                    INSERT INTO PERAWAT_HEWAN (No_perawat_hewan)
                    VALUES (%s)
                """, [medis_id])
                
                # Insert into SERTIFIKAT_KOMPETENSI table
                cursor.execute("""
                    INSERT INTO SERTIFIKAT_KOMPETENSI (Sertifikat_kompetensi, No_sertifikat_medis, Nama_sertifikat)
                    VALUES (%s, %s, %s)
                """, [cert_number, f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}", cert_name])
            
            messages.success(request, 'Registrasi perawat hewan berhasil! Silakan login.')
            return redirect('login')
            
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
        
        # Validation
        if not all([email, password, phone, hire_date, address]):
            return render(request, 'register_frontdesk.html', {
                'error': 'Semua field harus diisi'
            })
            
        try:
            with connection.cursor() as cursor:
                # Check if email already exists
                cursor.execute('SELECT Email FROM "USER" WHERE Email = %s', [email])
                if cursor.fetchone():
                    return render(request, 'register_frontdesk.html', {
                        'error': 'Email sudah terdaftar'
                    })

                # Generate employee ID
                pegawai_id = f"FD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                # 1. Insert into USER table
                hashed_password = make_password(password)
                cursor.execute("""
                    INSERT INTO "USER" (Email, Password, Nomor_telepon, Alamat)
                    VALUES (%s, %s, %s, %s)
                """, [email, hashed_password, phone, address])
                
                # 2. Insert into PEGAWAI table
                cursor.execute("""
                    INSERT INTO PEGAWAI (No_pegawai, Email_user, Tanggal_mulai_kerja, Tanggal_akhir_kerja)
                    VALUES (%s, %s, %s, NULL)
                """, [pegawai_id, email, hire_date])
                
                # 3. Insert into FRONT_DESK table
                cursor.execute("""
                    INSERT INTO FRONT_DESK (No_front_desk)
                    VALUES (%s)
                """, [pegawai_id])
                
                messages.success(request, 'Registrasi front desk berhasil! Silakan login.')
                return redirect('login')
            
        except Exception as e:
            return render(request, 'register_frontdesk.html', {
                'error': f'Terjadi kesalahan: {str(e)}'
            })        

def dashboard(request):
    """Dashboard page - shows user profile information"""
    if 'user_email' not in request.session:
        return redirect('login')
    
    email = request.session['user_email']
    user_type = request.session.get('specific_user_type', 'user')
    
    # Get user basic information
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Email, Alamat, Nomor_telepon 
            FROM USER 
            WHERE Email = %s
        """, [email])
        user_data = cursor.fetchone()
        
        if not user_data:
            return redirect('login')
        
        # Get specific user information based on type
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
        
        # Get additional info based on user type
        if user_type == 'individual':
            cursor.execute("""
                SELECT i.Nama_depan, i.Nama_tengah, i.Nama_belakang, k.Tanggal_registrasi
                FROM INDIVIDU i
                JOIN KLIEN k ON i.No_identitas_klien = k.No_identitas
                WHERE k.Email = %s
            """, [email])
            individual_data = cursor.fetchone()
            if individual_data:
                middle_name = f" {individual_data[1]}" if individual_data[1] else ""
                profile_data['name'] = f"{individual_data[0]}{middle_name} {individual_data[2]}"
                profile_data['join_date'] = individual_data[3]
        
        elif user_type == 'company':
            cursor.execute("""
                SELECT p.Nama_perusahaan, k.Tanggal_registrasi
                FROM PERUSAHAAN p
                JOIN KLIEN k ON p.No_identitas_klien = k.No_identitas
                WHERE k.Email = %s
            """, [email])
            company_data = cursor.fetchone()
            if company_data:
                profile_data['name'] = company_data[0]
                profile_data['join_date'] = company_data[1]
        
        elif user_type == 'veterinarian':
            cursor.execute("""
                SELECT p.Tanggal_mulai_kerja
                FROM PEGAWAI p
                WHERE p.Email_user = %s
            """, [email])
            vet_data = cursor.fetchone()
            if vet_data:
                profile_data['name'] = 'Dokter Hewan'
                profile_data['join_date'] = vet_data[0]
        
        elif user_type == 'nurse':
            cursor.execute("""
                SELECT p.Tanggal_mulai_kerja
                FROM PEGAWAI p
                WHERE p.Email_user = %s
            """, [email])
            nurse_data = cursor.fetchone()
            if nurse_data:
                profile_data['name'] = 'Perawat Hewan'
                profile_data['join_date'] = nurse_data[0]
        
        elif user_type == 'frontdesk':
            cursor.execute("""
                SELECT p.Tanggal_mulai_kerja
                FROM PEGAWAI p
                WHERE p.Email_user = %s
            """, [email])
            fd_data = cursor.fetchone()
            if fd_data:
                profile_data['name'] = 'Front Desk Officer'
                profile_data['join_date'] = fd_data[0]
    
    return render(request, 'dashboard.html', {'profile': profile_data})

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
    """Determine specific employee type"""
    with connection.cursor() as cursor:
        # Check if veterinarian
        cursor.execute("""
            SELECT 1 FROM PEGAWAI p
            JOIN TENAGA_MEDIS tm ON p.No_pegawai = tm.No_pegawai_hewan
            JOIN DOKTER_HEWAN dh ON tm.No_tenaga_medis = dh.No_dokter_hewan
            WHERE p.Email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'veterinarian'
        
        # Check if nurse
        cursor.execute("""
            SELECT 1 FROM PEGAWAI p
            JOIN TENAGA_MEDIS tm ON p.No_pegawai = tm.No_pegawai_hewan
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