from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('petclinic', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION prevent_duplicate_jenis_hewan_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                IF EXISTS (SELECT 1 FROM jenis_hewan WHERE lower(nama_jenis) = lower(NEW.nama_jenis) AND id != NEW.id) THEN
                    RAISE EXCEPTION 'ERROR: Jenis hewan dengan nama "%" sudah ada', NEW.nama_jenis;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            CREATE OR REPLACE TRIGGER prevent_duplicate_jenis_hewan_before_insert_update
            BEFORE INSERT OR UPDATE ON jenis_hewan
            FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_jenis_hewan_trigger();
            
            CREATE OR REPLACE FUNCTION update_vaccine_stock_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    UPDATE petclinic_vaccine 
                    SET stock = stock - 1 
                    WHERE vaccine_id = NEW.vaccine_id;
                    
                    IF (SELECT stock FROM petclinic_vaccine WHERE vaccine_id = NEW.vaccine_id) < 0 THEN
                        RAISE EXCEPTION 'ERROR: Stok vaksin "%" tidak mencukupi untuk vaksinasi.', 
                            (SELECT name FROM petclinic_vaccine WHERE vaccine_id = NEW.vaccine_id);
                    END IF;
                    
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE petclinic_vaccine 
                    SET stock = stock + 1 
                    WHERE vaccine_id = OLD.vaccine_id;
                    
                    RETURN OLD;
                END IF;
            END;
            $$ LANGUAGE plpgsql;
            
            CREATE OR REPLACE TRIGGER vaccination_stock_trigger
            AFTER INSERT OR DELETE ON petclinic_vaccination
            FOR EACH ROW EXECUTE FUNCTION update_vaccine_stock_trigger();
            
            CREATE OR REPLACE FUNCTION prevent_vaccine_deletion_trigger()
            RETURNS TRIGGER AS $$
            BEGIN
                IF EXISTS (SELECT 1 FROM petclinic_vaccination WHERE vaccine_id = OLD.vaccine_id) THEN
                    RAISE EXCEPTION 'ERROR: Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi.';
                END IF;
                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql;
            
            CREATE OR REPLACE TRIGGER prevent_vaccine_deletion
            BEFORE DELETE ON petclinic_vaccine
            FOR EACH ROW EXECUTE FUNCTION prevent_vaccine_deletion_trigger();
            """
        )
    ]