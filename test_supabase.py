from supabase import create_client

# Configuración de Supabase
url = "https://gonsfiizpyknwhjufqea.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdvbnNmaWl6cHlrbndoanVmcWVhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMjU0NzM1NiwiZXhwIjoyMDQ4MTIzMzU2fQ.Mwz3gQeI-oGGjBwm3uwdNPvtQMqppTOWs_Dwx54XQPY"

# Inicializar Supabase
try:
    supabase = create_client(url, key)
    
    # Intentar listar archivos en el bucket
    archivos = supabase.storage.from_('CBAMECAPACITA').list()
    
    print("Conexión exitosa. Archivos en el bucket CBAMECAPACITA:")
    for archivo in archivos:
        print(f"- {archivo['name']}")
        
    # Intentar descargar el archivo
    print("\nIntentando descargar ALUMNOS_X_LOCALIDAD.parquet:")
    respuesta = supabase.storage.from_('CBAMECAPACITA').download('ALUMNOS_X_LOCALIDAD.parquet')
    print(f"Tamaño del archivo descargado: {len(respuesta)} bytes")
    
except Exception as e:
    print(f"Error de conexión: {e}")
    import traceback
    traceback.print_exc()
