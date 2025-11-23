Crear el entorno virtual
python -m venv venv

Se activa
venv\Scripts\activate   o source venv/bin/activate

Instalar dependencias
pip install -r requirements.txt

Ejecutar el programa
uvicorn app.main:app --reload

Para ejecutar la base de datos:
cd "C:/ProgramFiles/PostgreSQL/17/bin

psql .U postgres -f "C:/RUTA/full_backup.sql"
