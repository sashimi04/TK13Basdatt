from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('petclinic', '0001_initial'),
    ]

    operations = [
        # Trigger to prevent duplicate jenis_hewan (case-insensitive)
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION prevent_duplicate_jenis_hewan_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                IF EXISTS (SELECT 1 FROM jenis_hewan WHERE lower(nama_jenis) = lower(NEW.nama_jenis) AND id != NEW.id)
                THEN
                    RAISE EXCEPTION 'Jenis hewan dengan nama %% sudah ada.', NEW.nama_jenis;
                END IF;
                RETURN NEW;
            END;
            $$
            LANGUAGE plpgsql;

            CREATE TRIGGER prevent_duplicate_jenis_hewan
            BEFORE INSERT OR UPDATE ON jenis_hewan
            FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_jenis_hewan_trigger();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS prevent_duplicate_jenis_hewan ON jenis_hewan;
            DROP FUNCTION IF EXISTS prevent_duplicate_jenis_hewan_trigger();
            """
        ),
        
        # Trigger to prevent deleting hewan with active kunjungan
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION prevent_delete_hewan_aktif_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                IF EXISTS (SELECT 1 FROM kunjungan WHERE nama_hewan = OLD.nama AND no_identitas_klien = OLD.no_identitas_klien AND timestamp_akhir IS NULL)
                THEN
                    -- Custom error message for the foreign key constraint violation
                    -- Note: This trigger fires *before* the DELETE, so it prevents the FK violation.
                    -- The error message needs to reflect the reason for prevention.
                    RAISE EXCEPTION 'Hewan "%%" milik klien dengan ID %% masih memiliki kunjungan aktif sehingga tidak dapat dihapus.', OLD.nama, OLD.no_identitas_klien;
                END IF;
                RETURN OLD;
            END;
            $$
            LANGUAGE plpgsql;

            CREATE TRIGGER prevent_delete_hewan_aktif
            BEFORE DELETE ON hewan
            FOR EACH ROW EXECUTE FUNCTION prevent_delete_hewan_aktif_trigger();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS prevent_delete_hewan_aktif ON hewan;
            DROP FUNCTION IF EXISTS prevent_delete_hewan_aktif_trigger();
            """
        ),
    ] 