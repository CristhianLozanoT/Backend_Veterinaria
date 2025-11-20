import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection(role: str):
    """
    Abre una conexión usando el rol PostgreSQL correcto
    """
    if role == "administrador":
        user = os.getenv("ADMIN_USER")
        password = os.getenv("ADMIN_PASSWORD")
    elif role == "veterinario":
        user = os.getenv("VETERINARIO_USER")
        password = os.getenv("VETERINARIO_PASSWORD")
    elif role == "secretaria":
        user = os.getenv("SECRETARIA_USER")
        password = os.getenv("SECRETARIA_PASSWORD")
    else:
        raise Exception("Rol inválido")
    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=user,
        password=password,
        # cursor_factory=RealDictCursor
    )
    return conn
