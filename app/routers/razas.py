from fastapi import APIRouter, HTTPException, Depends
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.razas import RazaCreate, RazaUpdate, RazaResponse

router = APIRouter(prefix="/razas", tags=["Razas"])


# ------------------------------
#   CREAR RAZA (solo admin)
# ------------------------------
@router.post("/crear-raza", response_model=dict)
def crear_raza(data: RazaCreate, user=Depends(get_current_user)):
    
    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_crear_raza(%s, %s)",
        (data.nombre, data.descripcion)
    )
    result = cur.fetchone()
    conn.commit()
    conn.close()

    # No devolvió ninguna fila
    if not result:
        raise HTTPException(500, "Error al crear la raza")

    raza = result.get("fn_crear_raza")

    # Si la función retorna error en JSON
    # Ejemplo:
    # RETURN json_build_object('status','error','message','La raza ya existe')
    if isinstance(raza, dict) and raza.get("status") == "error":
        raise HTTPException(400, raza.get("message", "No se pudo crear la raza"))

    # Si retorna NULL
    if raza is None:
        raise HTTPException(500, "Error inesperado al crear la raza")

    return raza



# ------------------------------
#   LISTAR RAZAS (todos)
# ------------------------------
@router.get("/listar-razas", response_model=list)
def listar_razas(user=Depends(get_current_user)):

    # admin / vet / secretaria → pueden ver
    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_razas()")
    result = cur.fetchone()
    conn.close()

    # Si PostgreSQL no devolvió ninguna fila
    if not result:
        raise HTTPException(404, "No se encontraron razas")

    razas = result.get("fn_listar_razas")

    # Si PL/pgSQL retorna un error tipo:
    # { "status": "error", "message": "No hay razas" }
    if isinstance(razas, dict) and razas.get("status") == "error":
        raise HTTPException(404, razas.get("message", "No se encontraron razas"))

    # Si retorna NULL
    if razas is None:
        raise HTTPException(404, "No se encontraron razas")

    # Si retorna una lista vacía
    if isinstance(razas, list) and len(razas) == 0:
        raise HTTPException(404, "No hay razas registradas aún")

    return razas



# ------------------------------
#   OBTENER UNA RAZA (todos)
# ------------------------------
@router.get("/obtener-raza/{raza_id}", response_model=dict)
def obtener_raza(raza_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_raza(%s)", (raza_id,))
    result = cur.fetchone()
    conn.close()

    # Nada retornado por la función
    if not result:
        raise HTTPException(404, "Raza no encontrada")

    raza = result.get("fn_obtener_raza")

    # Función devolvió NULL
    if raza is None:
        raise HTTPException(404, "Raza no encontrada")

    # Manejo si la función retorna:
    # { "status": "error", "message": "La raza no existe" }
    if isinstance(raza, dict) and raza.get("status") == "error":
        raise HTTPException(404, raza.get("message", "Raza no encontrada"))

    return raza



# ------------------------------
#   ACTUALIZAR RAZA (solo admin)
# ------------------------------
@router.put("/actualizar-raza/{raza_id}", response_model=dict)
def actualizar_raza(raza_id: int, data: RazaUpdate, user=Depends(get_current_user)):

    # Solo el admin puede actualizar razas
    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        "SELECT fn_actualizar_raza(%s, %s, %s)",
        (raza_id, data.nombre, data.descripcion)
    )
    result = cur.fetchone()
    conn.commit()
    conn.close()

    # La función no devolvió nada
    if not result:
        raise HTTPException(404, "Raza no encontrada")

    raza = result.get("fn_actualizar_raza")

    # La función devolvió NULL
    if raza is None:
        raise HTTPException(404, "Raza no encontrada")

    # La función devolvió error JSON:
    # { "status": "error", "message": "La raza no existe" }
    if isinstance(raza, dict) and raza.get("status") == "error":
        raise HTTPException(404, raza.get("message", "Raza no encontrada"))

    return raza



# ------------------------------
#   ELIMINAR RAZA (solo admin)
# ------------------------------
@router.delete("/eliminar-raza/{raza_id}", response_model=dict)
def eliminar_raza(raza_id: int, user=Depends(get_current_user)):

    # Solo el admin puede eliminar
    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_raza(%s)", (raza_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si no retorna nada = no existe
    if not result:
        raise HTTPException(404, "Raza no encontrada")

    data = result.get("fn_eliminar_raza")

    # Si retorna NULL
    if data is None:
        raise HTTPException(404, "Raza no encontrada")

    # Si tu función retorna errores estilo:
    # { "status": "error", "message": "algo" }
    if isinstance(data, dict) and data.get("status") == "error":
        raise HTTPException(404, data.get("message", "Raza no encontrada"))

    return data
