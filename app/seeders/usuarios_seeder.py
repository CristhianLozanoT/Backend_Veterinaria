from passlib.context import CryptContext
from app.database import get_connection

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

USUARIOS = [
    ("Veterinario", "vet@correo.com", "vet123", "veterinario"),
    ("Secretaria", "secretaria@correo.com", "sec123", "secretaria")
]


def seed_usuarios():
    print("🔍 Ejecutando seeder de usuarios...")

    conn = get_connection("administrador")
    cur = conn.cursor()

    for nombre, email, password, rol in USUARIOS:

        # 1. verificar si existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        existe = cur.fetchone()

        if existe:
            print(f"✔ El usuario '{email}' ya existe, se omite.")
            continue

        # 2. generar hash
        password_hash = pwd_context.hash(password)

        # 3. insertar usando tu función SQL
        cur.execute(
            "SELECT fn_crear_usuario(%s, %s, %s, %s)",
            (nombre, email, password_hash, rol)
        )

        print(f"➕ Usuario '{email}' creado como '{rol}'.")

    conn.commit()
    conn.close()

    print("✅ Seeder de usuarios completado.\n")
