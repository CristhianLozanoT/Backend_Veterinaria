from app.database import get_connection

RAZAS = [
    ("Labrador Retriever", "Perro amigable, inteligente y sociable, ideal para familias."),
    ("Golden Retriever", "Dócil, cariñoso y muy obediente, excelente compañero de niños."),
    ("Pastor Alemán", "Perro fuerte y leal, usado en labores policiales y de rescate."),
    ("Bulldog Inglés", "Robusto y tranquilo, muy afectuoso y fácil de manejar."),
    ("Poodle", "Extremadamente inteligente con pelaje hipoalergénico."),
    ("Beagle", "Pequeño, curioso y con gran sentido del olfato."),
    ("Chihuahua", "Muy pequeño, valiente y leal a su dueño."),
    ("Shih Tzu", "Pequeño, dócil y cariñoso, ideal como perro de compañía."),
    ("Rottweiler", "Fuerte, protector y equilibrado con buena educación."),
    ("Husky Siberiano", "Activo, sociable y resistente, famoso por sus ojos claros.")
]


def seed_razas():
    print("🔍 Ejecutando seeder de razas...")

    conn = get_connection("administrador")
    cur = conn.cursor()

    for nombre, descripcion in RAZAS:

        # 1. verificar si ya existe
        cur.execute(
            "SELECT id FROM razas WHERE nombre = %s",
            (nombre,)
        )
        existe = cur.fetchone()

        if existe:
            print(f"✔ La raza '{nombre}' ya existe, se omite.")
            continue

        # 2. insertar usando la función fn_crear_raza
        cur.execute(
            "SELECT fn_crear_raza(%s, %s)",
            (nombre, descripcion)
        )

        print(f"➕ Raza '{nombre}' insertada con fn_crear_raza().")

    conn.commit()
    conn.close()
    print("✅ Seeder de razas completado.\n")
