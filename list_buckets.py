from supabase import create_client

# Configuración de Supabase
url = "https://gonsfiizpyknwhjufqea.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdvbnNmaWl6cHlrbndoanVmcWVhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjU0NzM1NiwiZXhwIjoyMDQ4MTIzMzU2fQ.Mwz3gQeI-oGGjBwm3uwdNPvtQMqppTOWs_Dwx54XQPY"

# Inicializar Supabase
try:
    supabase = create_client(url, key)
    
    # Listar buckets disponibles
    buckets = supabase.storage.list_buckets()
    
    print("Buckets disponibles:")
    for bucket in buckets:
        print(f"- {bucket.name}")
        
        # Listar archivos en cada bucket
        try:
            archivos = supabase.storage.from_(bucket.name).list()
            print(f"  Archivos en {bucket.name}:")
            for archivo in archivos:
                print(f"  - {archivo['name']}")
        except Exception as e:
            print(f"  Error al listar archivos en {bucket.name}: {e}")
        
        print("---")
except Exception as e:
    print(f"Error de conexión: {e}")
    import traceback
    traceback.print_exc()
