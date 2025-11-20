import os
from passlib.context import CryptContext
from app.database import get_connection

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

DEFAULT_ADMIN_NAME = "Administrador"
DEFAULT_ADMIN_EMAIL = "admin@admin.com"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_ROLE = "administrador"


def seed_admin():
    print("🔍 Ejecutando seeder de administrador...")

    # Conectar como administrador
    conn = get_connection("administrador")
    cur = conn.cursor()

    # Verificar si ya existe
    cur.execute(
        "SELECT id FROM usuarios WHERE email = %s",
        (DEFAULT_ADMIN_EMAIL,)
    )

    existe = cur.fetchone()

    if existe:
        print(" Administrador ya existe, no se genera de nuevo.")
        conn.close()
        return

    password_hash = pwd_context.hash(DEFAULT_ADMIN_PASSWORD)

    # Insertar usando tu función
    cur.execute(
        "SELECT fn_crear_usuario(%s, %s, %s, %s)",
        (DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_EMAIL, password_hash, DEFAULT_ADMIN_ROLE)
    )

    conn.commit()
    conn.close()

    print("Administrador creado correctamente.")


