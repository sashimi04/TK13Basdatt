# path=petclinic/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import JenisHewan, Hewan, Klien, Individu, Perusahaan, FrontDesk, DokterHewan, Kunjungan
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import PermissionDenied
from django.db.models import Q
import uuid
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages

def get_user_role(request):
    """Helper function to get user role from session"""
    return request.session.get('user_role', 'Guest')

def check_role_access(request, allowed_roles):
    """Helper function to check if user has required role"""
    user_role = get_user_role(request)
    if user_role not in allowed_roles and user_role != 'Guest':
        raise PermissionDenied("You don't have permission to access this page.")

def get_owner_name(klien_id):
    """Helper function to get owner name based on Klien UUID using raw SQL"""
    with connection.cursor() as cursor:
        # Try to get Individual name
        cursor.execute("""
            SELECT nama_depan, nama_tengah, nama_belakang
            FROM individu
            WHERE no_identitas_klien = %s
        """, [klien_id])
        row = cursor.fetchone()
        if row:
            names = [row[0]]
            if row[1]:
                names.append(row[1])
            names.append(row[2])
            return ' '.join(names)

        # If not Individual, try to get Company name
        cursor.execute("""
            SELECT nama_perusahaan
            FROM perusahaan
            WHERE no_identitas_klien = %s
        """, [klien_id])
        row = cursor.fetchone()
        if row:
            return row[0]

    return "Unknown Owner"

def get_user_specific_type(email):
    """Helper function to get specific user type - FIXED VERSION"""
    with connection.cursor() as cursor:
        # Check if user is in klien table (individual or company)
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
        
        # Check if user is an employee (simplified queries)
        cursor.execute("""
            SELECT 1 FROM dokter_hewan WHERE email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'veterinarian'
        
        cursor.execute("""
            SELECT 1 FROM perawat WHERE email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'nurse'
        
        cursor.execute("""
            SELECT 1 FROM front_desk WHERE email_user = %s
        """, [email])
        if cursor.fetchone():
            return 'frontdesk'
    
    return 'user'

def dashboard(request):
    # Temporarily set user role to FrontDeskOfficer for testing
    request.session['user_role'] = 'FrontDeskOfficer'
    # Remove temporary klien ID from session as it's not needed for FrontDeskOfficer
    if 'no_identitas_klien' in request.session:
        del request.session['no_identitas_klien']
    print(f"Debug: User role automatically set to {request.session.get('user_role')} for testing.")

    user_role = get_user_role(request) # Mendapatkan peran

    # --- Tambahkan Context untuk Template --- #
    context = {
        'user_role': user_role,
        'user': request.user, # Meneruskan objek user (untuk {{ user.username }})
        # Tambahkan data dummy atau ambil dari DB sesuai peran jika diperlukan oleh template
        'total_hewan': 0, # Dummy data
        'total_klien': 0, # Dummy data
        'kunjungan_hari_ini': 0, # Dummy data
        'perawatan_aktif': 0, # Dummy data
        'aktivitas_terbaru': [], # Dummy data
        'jadwal_hari_ini': 0, # Dummy data
        'jadwal_list': [], # Dummy data
        'kunjungan_terakhir': 'N/A', # Dummy data
        'hewan_list': [], # Dummy data (untuk klien)
        'kunjungan_list': [], # Dummy data (untuk klien)
        'stok_obat_rendah': 0, # Dummy data
    }
    # --- Akhir Penambahan Context --- #

    return render(request, 'dashboard.html', context)

def hewan_list(request):
    # Check role access
    check_role_access(request, ['FrontDeskOfficer', 'Klien', 'Guest'])
    
    user_role = get_user_role(request)
    no_identitas_klien = request.session.get('no_identitas_klien')
    print(f"Debug - User Role: {user_role}")  # Debug print
    print(f"Debug - No Identitas Klien: {no_identitas_klien}")  # Debug print
    
    # Fetch hewan list using raw SQL
    with connection.cursor() as cursor:
        sql_query = """
            SELECT
                h.nama,
                h.no_identitas_klien,
                h.id_jenis,
                h.tanggal_lahir,
                h.url_foto,
                jh.nama_jenis AS jenis_nama,
                EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE nama_hewan = h.nama
                    AND no_identitas_klien = h.no_identitas_klien
                    AND timestamp_akhir IS NULL
                ) AS ada_kunjungan_aktif,
                EXISTS (
                    SELECT 1 FROM kunjungan k
                    WHERE k.nama_hewan = h.nama
                    AND k.no_identitas_klien = h.no_identitas_klien
                ) AS has_any_visit
            FROM hewan h
            JOIN jenis_hewan jh ON h.id_jenis = jh.id
        """
        query_params = []

        if user_role == 'Klien' and no_identitas_klien:
            sql_query += "\nWHERE h.no_identitas_klien = %s"
            query_params.append(no_identitas_klien)

        # Order by owner name (requires joins, complex in raw SQL here, skip for now)
        # and then by jenis and hewan name
        # Let's simplify ordering for the template view
        sql_query += "\nORDER BY jh.nama_jenis, h.nama"

        cursor.execute(sql_query, query_params)
        rows = cursor.fetchall()

        # Map raw results to a list of dictionaries
        hewan_list_data = []
        for row in rows:
            hewan_data = {
                'nama': row[0],
                'no_identitas_klien': row[1], # UUID object
                'id_jenis': row[2], # UUID object
                'tanggal_lahir': row[3], # date object
                'url_foto': row[4],
                'jenis': row[5], # jenis_nama
                'ada_kunjungan_aktif': row[6],
                'has_any_visit': row[7],
            }
            # Get owner name using the helper function (which now uses raw SQL)
            try:
                hewan_data['pemilik'] = get_owner_name(hewan_data['no_identitas_klien'])
            except Exception as e:
                print(f"Error getting owner name for hewan {row[0]}: {str(e)}")
                hewan_data['pemilik'] = "Error Fetching Owner"

            hewan_list_data.append(hewan_data)

    print(f"Debug - Fetched Hewan List (Raw SQL): {hewan_list_data}")  # Debug print

    # Fetch lists for dropdowns using raw SQL
    jenis_hewan_list_data = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama_jenis FROM jenis_hewan ORDER BY nama_jenis")
        jenis_rows = cursor.fetchall()
        for row in jenis_rows:
            jenis_hewan_list_data.append({'id': row[0], 'nama_jenis': row[1]})

    klien_list_data = []
    if user_role == 'FrontDeskOfficer': # Only needed for FrontDeskOfficer for the modal dropdown
        with connection.cursor() as cursor:
            # Join Klien with Individu and Perusahaan to get names
            cursor.execute("""
                SELECT
                    k.no_identitas,
                    CASE
                        WHEN i.no_identitas_klien IS NOT NULL THEN
                            CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                        WHEN p.no_identitas_klien IS NOT NULL THEN
                            p.nama_perusahaan
                        ELSE 'Unknown'
                    END AS nama_klien
                FROM klien k
                LEFT JOIN individu i ON k.no_identitas = i.no_identitas_klien
                LEFT JOIN perusahaan p ON k.no_identitas = p.no_identitas_klien
                ORDER BY nama_klien
            """
            )
            klien_rows = cursor.fetchall()
            for row in klien_rows:
                klien_list_data.append({'no_identitas': row[0], 'nama': row[1]})
        print(f"Debug - Fetched Klien List (Raw SQL): {klien_list_data}") # Debug print
    
    context = {
        'hewan_list': hewan_list_data,
        'jenis_hewan_list': jenis_hewan_list_data,
        'klien_list': klien_list_data,
        'user_role': user_role
    }
    return render(request, 'hewan_list.html', context)

def jenis_hewan_list(request):
    # Check role access
    check_role_access(request, ['FrontDeskOfficer', 'DokterHewan', 'Guest'])
    
    # Fetch jenis hewan list using raw SQL
    jenis_list_data = []
    with connection.cursor() as cursor:
        # Join with hewan to check if used
        cursor.execute("""
            SELECT
                jh.id,
                jh.nama_jenis,
                EXISTS(SELECT 1 FROM hewan h WHERE h.id_jenis = jh.id) AS is_used
            FROM jenis_hewan jh
            ORDER BY jh.nama_jenis
        """
    )
        rows = cursor.fetchall()
        for row in rows:
            jenis_list_data.append({'id': row[0], 'nama_jenis': row[1], 'is_used': row[2]})

    print(f"Debug - Jenis Hewan List (Raw SQL): {jenis_list_data}")  # Debug print
    context = {
        'jenis_hewan_list': jenis_list_data,
        'user_role': get_user_role(request)
    }
    return render(request, 'jenis_hewan_list.html', context)

# API endpoints for CRUD operations
@csrf_exempt
def api_hewan(request):
    # Check role access for all operations
    check_role_access(request, ['FrontDeskOfficer', 'Klien'])

    try:
        if request.method == 'GET':
            user_role = get_user_role(request)
            no_identitas_klien_session = request.session.get('no_identitas_klien')

            sql_query = """
                SELECT
                    h.nama,
                    h.no_identitas_klien,
                    h.id_jenis,
                    h.tanggal_lahir,
                    h.url_foto,
                    jh.nama_jenis AS jenis_nama,
                    EXISTS (
                        SELECT 1 FROM kunjungan k
                        WHERE k.nama_hewan = h.nama
                        AND k.no_identitas_klien = h.no_identitas_klien
                        AND k.timestamp_akhir IS NULL
                    ) AS ada_kunjungan_aktif,
                    EXISTS (
                        SELECT 1 FROM kunjungan k
                        WHERE k.nama_hewan = h.nama
                        AND k.no_identitas_klien = h.no_identitas_klien
                    ) AS has_any_visit
                FROM hewan h
                JOIN jenis_hewan jh ON h.id_jenis = jh.id
            """
            query_params = []

            if user_role == 'Klien' and no_identitas_klien_session:
                sql_query += "\nWHERE h.no_identitas_klien = %s"
                query_params.append(no_identitas_klien_session)

            # Order by nama
            sql_query += "\nORDER BY h.nama"

            data = []
            with connection.cursor() as cursor:
                cursor.execute(sql_query, query_params)
                rows = cursor.fetchall()

                for row in rows:
                    hewan_data = {
                        'nama': row[0],
                        'no_identitas_klien': str(row[1]), # Convert UUID to string for JSON
                        'id_jenis': str(row[2]), # Convert UUID to string for JSON
                        'tanggal_lahir': row[3].isoformat() if row[3] else None, # Convert date to ISO format
                        'url_foto': row[4],
                        'jenis': row[5], # jenis_nama
                        'ada_kunjungan_aktif': row[6],
                        'has_any_visit': row[7],
                    }
                     # Get owner name using the helper function (which now uses raw SQL)
                    try:
                        hewan_data['pemilik'] = get_owner_name(row[1]) # Pass the UUID object
                    except Exception as e:
                        print(f"Error getting owner name for hewan {row[0]}: {str(e)}")
                        hewan_data['pemilik'] = "Error Fetching Owner"

                    data.append(hewan_data)

            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            # Allow FrontDeskOfficer and Klien to create animals
            check_role_access(request, ['FrontDeskOfficer', 'Klien'])
            data = json.loads(request.body)
            try:
                user_role = get_user_role(request)

                # Get owner ID based on role
                if user_role == 'Klien':
                    no_identitas_klien_str = request.session.get('no_identitas_klien')
                    if not no_identitas_klien_str:
                        return JsonResponse({'error': 'Klien user ID not found in session.'}, status=400)
                else: # FrontDeskOfficer
                    # Assuming data contains: nama, no_identitas_klien (UUID string), id_jenis (UUID string), tanggal_lahir, url_foto
                    no_identitas_klien_str = data.get('no_identitas_klien')
                    if not no_identitas_klien_str:
                         return JsonResponse({'error': 'Pemilik is required for Front Desk Officer.'}, status=400)

                # Validate required fields (nama, id_jenis, tanggal_lahir) from request body
                if not all(k in data for k in ('nama', 'id_jenis', 'tanggal_lahir')):
                    return JsonResponse({'error': 'Missing required fields'}, status=400)

                # Validate UUID formats
                try:
                    no_identitas_klien_uuid = uuid.UUID(no_identitas_klien_str)
                    id_jenis_uuid = uuid.UUID(data['id_jenis'])
                except ValueError:
                    return JsonResponse({'error': 'Invalid UUID format for owner or jenis'}, status=400)

                # Insert into hewan table using raw SQL
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO hewan (nama, no_identitas_klien, id_jenis, tanggal_lahir, url_foto)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [data['nama'], no_identitas_klien_uuid, id_jenis_uuid, data['tanggal_lahir'], data.get('url_foto', '')])

                return JsonResponse({'message': 'Hewan added successfully'}) # No specific ID returned for creation

            except DatabaseError as e:
                print(f"Database Error during hewan POST: {str(e)}")
                error_message = str(e).split('\n')[0].replace('ERROR:', '').strip()
                if not error_message:
                    error_message = 'Database error occurred while adding animal.'
                return JsonResponse({'error': error_message}, status=400)
            except Exception as e:
                print(f"Unexpected error during hewan POST: {str(e)}")
                return JsonResponse({'error': 'An unexpected server error occurred during creation: ' + str(e)}, status=500)
        
        elif request.method == 'PUT':
            # Allow FrontDeskOfficer and Klien to update animals
            check_role_access(request, ['FrontDeskOfficer', 'Klien'])
            data = json.loads(request.body)
            try:
                # Validate required fields and UUID formats from payload
                if not all(k in data for k in ('original_nama', 'original_no_identitas_klien', 'nama', 'id_jenis', 'tanggal_lahir')):
                    return JsonResponse({'error': 'Missing required fields for update'}, status=400)

                try:
                    original_no_identitas_klien_uuid = uuid.UUID(data['original_no_identitas_klien'])
                    id_jenis_uuid = uuid.UUID(data['id_jenis'])
                     # Validate optional no_identitas_klien UUID format if present in payload (for FD)
                    if 'no_identitas_klien' in data:
                         uuid.UUID(data['no_identitas_klien'])

                except ValueError:
                     return JsonResponse({'error': 'Invalid UUID format in update data.'}, status=400)

                user_role = get_user_role(request)

                # Determine the final owner ID for the update based on role
                if user_role == 'Klien':
                    klien_session_id_str = request.session.get('no_identitas_klien')
                    if not klien_session_id_str:
                         return JsonResponse({'error': 'Klien user ID not found in session.'}, status=403) # Forbidden
                    klien_session_id_uuid = uuid.UUID(klien_session_id_str)

                    # Klien can only edit their own pets: verify original owner matches session ID
                    if original_no_identitas_klien_uuid != klien_session_id_uuid:
                         return JsonResponse({'error': 'You do not have permission to edit this animal.'}, status=403) # Forbidden

                    # The final owner for update is the Klien's session ID
                    final_no_identitas_klien_for_update = klien_session_id_uuid

                else: # FrontDeskOfficer
                    # FrontDeskOfficer can change owner, use the one from the payload
                    if 'no_identitas_klien' not in data:
                         return JsonResponse({'error': 'Pemilik is required for Front Desk Officer.'}, status=400)
                    final_no_identitas_klien_for_update = uuid.UUID(data['no_identitas_klien'])

                # Check if the animal to update exists using raw SQL (using original details)
                exists = False
                with connection.cursor() as cursor:
                     # Use original nama and owner to find the pet
                     cursor.execute("""
                         SELECT 1 FROM hewan
                         WHERE nama = %s AND no_identitas_klien = %s
                     """, [data['original_nama'], original_no_identitas_klien_uuid])
                     exists = cursor.fetchone() is not None

                if not exists:
                    return JsonResponse({'error': 'Animal not found'}, status=404)

                # Perform the update
                with connection.cursor() as cursor:
                     cursor.execute("""
                         UPDATE hewan
                         SET
                             nama = %s,
                             no_identitas_klien = %s, -- Use the determined final owner ID
                             id_jenis = %s,
                             tanggal_lahir = %s,
                             url_foto = %s
                         WHERE nama = %s AND no_identitas_klien = %s
                     """, [
                         data['nama'],
                         str(final_no_identitas_klien_for_update), # Ensure it's a string for execute
                         id_jenis_uuid,
                         data['tanggal_lahir'], data.get('url_foto', ''),
                         data['original_nama'], original_no_identitas_klien_uuid
                     ])

                return JsonResponse({'message': 'Hewan updated successfully'})

            except DatabaseError as e:
                print(f"Database Error during hewan PUT: {str(e)}")
                error_message = str(e).split('\n')[0].replace('ERROR:', '').strip()
                if not error_message:
                    error_message = 'Database error occurred while updating animal.'
                return JsonResponse({'error': error_message}, status=400)
            except Exception as e:
                print(f"Unexpected error during hewan PUT: {str(e)}")
                return JsonResponse({'error': 'An unexpected server error occurred during update: ' + str(e)}, status=500)
        
        elif request.method == 'DELETE':
            # Check role access
            check_role_access(request, ['FrontDeskOfficer', 'Klien'])
            # Get parameters from URL instead of request body
            nama = request.GET.get('nama')
            no_identitas_klien_str = request.GET.get('no_identitas_klien')

            if not nama or not no_identitas_klien_str:
                return JsonResponse({'error': 'Nama dan no_identitas_klien harus disediakan'}, status=400)

            try:
                # Convert UUID string to UUID object
                no_identitas_klien_uuid = uuid.UUID(no_identitas_klien_str)
            except ValueError:
                return JsonResponse({'error': 'Invalid UUID format for no_identitas_klien'}, status=400)

            try:
                # Delete from hewan table using raw SQL
                with connection.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM hewan
                        WHERE nama = %s AND no_identitas_klien = %s
                    """, [nama, no_identitas_klien_uuid])

                # Check if any row was deleted
                if cursor.rowcount == 0:
                    # If no rows were deleted, it might mean the animal was not found
                    # or the trigger prevented deletion without raising an explicit exception.
                    # We need to check for the trigger exception specifically.
                    # The trigger raises an exception, so if we reach here without an exception,
                    # it means the animal didn't exist.
                    return JsonResponse({'error': 'Hewan tidak ditemukan'}, status=404)

                return JsonResponse({'message': 'Hewan berhasil dihapus'})
            except DatabaseError as e:
                # Catch database errors, likely from the trigger
                print(f"Database Error during delete: {str(e)}")
                # Extract the trigger error message. DatabaseError often wraps the
                # original exception. The string representation contains the message.
                # The format is typically 'ERROR: your message\nDETAIL: ...'
                # Split by newline and take the first line, remove 'ERROR:' prefix.
                db_error_message = str(e)
                error_message = db_error_message.split('\n')[0].replace('ERROR:', '').strip()

                # Check for the specific foreign key violation related to active visits
                # and replace with the intended trigger message for better user feedback.
                # The constraint name might vary slightly, but it should contain 'kunjungan' and 'hewan'.
                # Let's use the exact constraint name from the error message image for precision.
                fk_constraint_name = 'kunjungan_nama_hewan_no_identitas_klien_fkey' # Adjust if constraint name is different
                if fk_constraint_name in db_error_message:
                    # Attempt to construct the intended trigger message
                    try:
                        owner_name_for_message = get_owner_name(uuid.UUID(no_identitas_klien_str)) # Use UUID from request
                        error_message = f'Hewan "{nama}" milik "{owner_name_for_message}" masih memiliki kunjungan aktif sehingga tidak dapat dihapus.'
                    except Exception as owner_e:
                        print(f"Error fetching owner name for custom error message: {owner_e}")
                        error_message = f'Hewan "{nama}" masih memiliki kunjungan aktif sehingga tidak dapat dihapus.' # Fallback message
                
                # If the extracted message is empty or just 'ERROR:', use a generic one
                if not error_message or error_message == 'ERROR:':
                    error_message = 'Gagal menghapus hewan karena ada ketergantungan data atau kesalahan database.'
                return JsonResponse({'error': error_message}, status=400) # Use 400 for bad request due to trigger

    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_jenis_hewan(request):
    # Check role access for write operations
    if request.method in ['POST', 'PUT', 'DELETE']:
        check_role_access(request, ['FrontDeskOfficer'])
    
    try:
        if request.method == 'GET':
            jenis_list = JenisHewan.objects.all().order_by('id')
            data = []
            for j in jenis_list:
                # Check if jenis is used by any hewan
                is_used = Hewan.objects.filter(id_jenis=j).exists()
                
                data.append({
                    'id': str(j.id),
                    'nama_jenis': j.nama_jenis,
                    'is_used': is_used
                })
            return JsonResponse(data, safe=False)
        
        elif request.method == 'POST':
            data = json.loads(request.body)
            try:
                # Generate UUID for new jenis
                jenis_id = uuid.uuid4()
                jenis = JenisHewan.objects.create(
                    id=jenis_id,
                    nama_jenis=data['nama_jenis']
                )
                return JsonResponse({
                    'id': str(jenis.id),
                    'message': 'Created successfully'
                })
            except DatabaseError as e:
                return JsonResponse({'error': str(e)}, status=400)
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            try:
                jenis = get_object_or_404(JenisHewan, id=data['id'])
                jenis.nama_jenis = data['nama_jenis']
                jenis.save()
                return JsonResponse({'message': 'Updated successfully'})
            except DatabaseError as e:
                return JsonResponse({'error': str(e)}, status=400)
        
        elif request.method == 'DELETE':
            jenis_id = request.GET.get('id')
            try:
                jenis = get_object_or_404(JenisHewan, id=jenis_id)
                
                # Check if jenis is used by any hewan
                if Hewan.objects.filter(id_jenis=jenis).exists():
                    return JsonResponse({
                        'error': f'Jenis hewan "{jenis.nama_jenis}" masih digunakan oleh hewan peliharaan sehingga tidak dapat dihapus.'
                    }, status=400)
                
                jenis.delete()
                return JsonResponse({'message': 'Deleted successfully'})
            except DatabaseError as e:
                return JsonResponse({'error': str(e)}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_klien(request):
    # Hanya FrontDeskOfficer yang boleh melihat daftar klien di sini
    check_role_access(request, ['FrontDeskOfficer'])

    try:
        if request.method == 'GET':
            print("Debug: Entering api_klien GET") # Debug log
            # Gabungkan data dari Individu dan Perusahaan
            sql_query = """
                SELECT
                    k.no_identitas,
                    CASE
                        WHEN i.no_identitas_klien IS NOT NULL THEN
                            CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                        WHEN p.no_identitas_klien IS NOT NULL THEN
                            p.nama_perusahaan
                        ELSE 'Unknown'
                    END AS nama_klien
                FROM klien k
                LEFT JOIN individu i ON k.no_identitas = i.no_identitas_klien
                LEFT JOIN perusahaan p ON k.no_identitas = p.no_identitas_klien
                ORDER BY nama_klien
            """

            data = []
            with connection.cursor() as cursor:
                print(f"Debug: Executing api_klien SQL: {sql_query}") # Debug log
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                print(f"Debug: Raw Klien data from DB in api_klien: {rows}") # Debug log

                for row in rows:
                    data.append({
                        'no_identitas': str(row[0]), # Convert UUID to string for JSON
                        'nama': row[1],
                    })
            print(f"Debug: Processed Klien data for JSON in api_klien: {data}") # Debug log

            return JsonResponse(data, safe=False)

    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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

def login_view(request):
   if request.method == 'GET':
       return render(request, 'login.html')
   elif request.method == 'POST':
       email = request.POST.get('email', '').strip()
       password = request.POST.get('password', '').strip()
       
       if not email or not password:
           return render(request, 'login.html', {'error': 'Email dan password harus diisi'})
       
       with connection.cursor() as cursor:
           cursor.execute("SELECT email, password FROM users WHERE email = %s", [email])
           user_data = cursor.fetchone()
           
           if user_data and (check_password(password, user_data[1]) or password == user_data[1]):
               request.session['user_email'] = email
               user_type = get_user_specific_type(email)
               request.session['specific_user_type'] = user_type
               return redirect('/')
       
       return render(request, 'login.html', {'error': 'Email atau password salah'})

def logout_view(request):
   request.session.flush()
   return redirect('/')

def register_type(request):
   return render(request, 'register_type.html')

def register_individual(request):
   return render(request, 'register_individual.html')

def register_company(request):
   return render(request, 'register_company.html')

def register_veterinarian(request):
   return render(request, 'register_vet.html')

def register_nurse(request):
   return render(request, 'register_nurse.html')

def register_frontdesk(request):
   return render(request, 'register_frontdesk.html')

# Klien Views
def kelola_hewan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'hewan_peliharaan.html')

def daftar_kunjungan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'list_list_vaccination.html')

def daftar_vaksinasi(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'list_list_vaccine.html')

# Front Desk Views
def kelola_jenis_hewan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'jenis_hewan_list.html')

def kelola_kunjungan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'list_client.html')

def daftar_klien(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'list_client.html')

# Dokter Hewan Views
def daftar_jenis_hewan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'jenis_hewan.html')

def perawatan_hewan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'hewan_list.html')

def manajemen_obat(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'hewan_list.html')

def manajemen_perawatan(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'hewan_list.html')

def pemberian_obat(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'hewan_list.html')

def manajemen_vaksinasi(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'create_list_vaccination.html')

# Perawat Views
def manajemen_vaksin(request):
   if 'user_email' not in request.session:
       return redirect('/login/')
   return render(request, 'create_list_vaccine.html')