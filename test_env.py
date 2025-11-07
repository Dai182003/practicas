import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env', override=False)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("📌 Verificación de .env:")
print(f"SUPABASE_URL: {' Encontrada' if url else ' No encontrada'}")
print(f"SUPABASE_KEY: {' Encontrada' if key else ' No encontrada'}")

print(f"URL comienza con: {url[:30] if url else 'N/A'}")
