from app.database import get_connection

MEDICAMENTOS = [
    ("Amoxicilina", 25000),
    ("Metronidazol", 18000),
    ("Enrofloxacina", 32000),
    ("Prednisolona", 15000),
    ("Carprofeno", 28000),
    ("Meloxicam", 24000),
    ("Ketoconazol", 30000),
    ("Ivermectina", 12000),
    ("Furosemida", 17000),
    ("Sucralfato", 20000),
    ("Omeprazol", 16000),
    ("Dipirona", 10000),
    ("Doxiciclina", 22000),
    ("Fenbendazol", 14000),
    ("Ciprofloxacina", 26000)
]


def seed_medicamentos():
    print("🔍 Ejecutando seeder de medicamentos...")

    conn = get_connection("administrador")
    cur = conn.cursor()

    for nombre, precio in MEDICAMENTOS:

        # 1. verificar si ya existe
        cur.execute(
            "SELECT id FROM medicamentos WHERE nombre = %s",
            (nombre,)
        )
        existe = cur.fetchone()

        if existe:
            print(f"✔ El medicamento '{nombre}' ya existe, se omite.")
            continue

        # 2. insertar usando la función fn_crear_medicamento
        cur.execute(
            "SELECT fn_crear_medicamento(%s, %s)",
            (nombre, precio)
        )

        print(f"➕ Medicamento '{nombre}' insertado con fn_crear_medicamento().")

    conn.commit()
    conn.close()
    print("✅ Seeder de medicamentos completado.\n")
