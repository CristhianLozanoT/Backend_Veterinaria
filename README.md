Crear el entorno virtual
python -m venv venv

Se activa
venv\Scripts\activate   o source venv/bin/activate

Instalar dependencias
pip install -r requirements.txt

Ejecutar el programa
uvicorn app.main:app --reload


