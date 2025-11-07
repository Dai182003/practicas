import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Crea y retorna cliente Supabase autenticado"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(" Credenciales de Supabase no encontradas en .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializar tablas si no existen (ejecutar una vez)
def init_database():
    """Inicializa las tablas necesarias en Supabase"""
    sb = get_supabase_client()
    
    # Las tablas deben crearse en el dashboard de Supabase con SQL:
    """
    CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'estudiante',
        nombre TEXT,
        apellido TEXT,
        dni TEXT UNIQUE,
        telefono TEXT,
        carrera TEXT,
        universidad TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE ofertas_practicas (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        titulo TEXT NOT NULL,
        empresa TEXT NOT NULL,
        area TEXT NOT NULL,
        duracion TEXT,
        modalidad TEXT,
        ubicacion TEXT,
        requisitos TEXT,
        descripcion TEXT,
        estado TEXT DEFAULT 'activa',
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE postulaciones (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id),
        oferta_id UUID REFERENCES ofertas_practicas(id),
        estado TEXT DEFAULT 'pendiente',
        fecha_postulacion TIMESTAMP DEFAULT NOW(),
        archivo_cv TEXT
    );
    """
    print(" Verifica que las tablas estén creadas en Supabase")