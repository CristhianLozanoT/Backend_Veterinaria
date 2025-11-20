from app.seeders.razas_seeder import seed_razas
from app.seeders.medicamentos_seeder import seed_medicamentos 
from app.seeders.usuarios_seeder import seed_usuarios

def run_all_seeders():
    print("\n=========== Ejecutando todos los seeders ===========\n")

    seed_razas()
    seed_medicamentos()
    seed_usuarios()
    

    print("\n=========== Todos los seeders ejecutados ===========\n")

if __name__ == "__main__":
    run_all_seeders()
