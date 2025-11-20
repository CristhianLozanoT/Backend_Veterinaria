from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.consultas import ConsultaCreate, ConsultaUpdate

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.post("/crear-consulta", response_model=dict)
def crear_consulta(data: ConsultaCreate, user=Depends(get_current_user)):

    if user["role"] not in ("administrador", "veterinario"):
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Validación opcional: una consulta por mascota en el día
    cur.execute("""
        SELECT id FROM consultas 
        WHERE mascota_id = %s 
        AND DATE(created_at) = CURRENT_DATE
    """, (data.mascota_id,))

    existe = cur.fetchone()

    if existe:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Ya existe una consulta registrada hoy para esta mascota."
        )

    # Crear consulta (ahora incluyendo cita_id)
    cur.execute(
    "SELECT fn_crear_consulta(%s, %s, %s, %s, %s, %s)",
    (
        data.cita_id,
        data.cliente_id,
        data.mascota_id,
        data.veterinario_id,
        data.diagnostico,
        data.total
    )
)

    row = cur.fetchone()
    conn.commit()
    conn.close()

    # Validar retorno
    if not row or not row["fn_crear_consulta"]:
        raise HTTPException(
            status_code=500,
            detail="No se pudo crear la consulta debido a un error interno."
        )

    return row["fn_crear_consulta"]



@router.get("/obtener-consulta/{consulta_id}", response_model=dict)
def obtener_consulta(consulta_id: int, user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_consulta(%s)", (consulta_id,))
    row = cur.fetchone()
    conn.close()

    # Manejo de ambos casos:
    # 1) No llegó fila
    # 2) La función retornó NULL
    if not row or not row["fn_obtener_consulta"]:
        raise HTTPException(
            status_code=404,
            detail=f"La consulta con ID {consulta_id} no existe."
        )

    return row["fn_obtener_consulta"]



@router.get("/listar-consultas", response_model=list)
def listar_consultas(user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor()
    cur.execute("SELECT fn_listar_consultas()")
    row = cur.fetchone()
    conn.close()

    raw = row[0] if row else None

    if not raw:
        return [{"message": "Aún no hay consultas registradas"}]

    # 🔥 Convertir string JSON a lista Python
    import json
    try:
        return json.loads(raw)
    except:
        # Si ya viene como json_agg real
        return raw



@router.put("/actualizar-consulta/{consulta_id}", response_model=dict)
def actualizar_consulta(consulta_id: int, data: ConsultaUpdate, user=Depends(get_current_user)):

    if user["role"] not in ("administrador", "veterinario"):
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_consulta(%s, %s, %s, %s, %s)",
        (
            consulta_id,data.cliente_id,data.mascota_id,data.diagnostico,data.total        
        )
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    #  Si no retorna nada → no existe
    if not result:
        raise HTTPException(404, "Consulta no encontrada")

    respuesta = result["fn_actualizar_consulta"]

    #  Si la función devuelve un error interno
    if isinstance(respuesta, dict) and respuesta.get("status") == "error":
        raise HTTPException(
            400,
            respuesta.get("message", "Error al actualizar la consulta")
        )

    return respuesta


@router.delete("/eliminar-consulta/{consulta_id}", response_model=dict)
def eliminar_consulta(consulta_id: int, user=Depends(get_current_user)):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_consulta(%s)", (consulta_id,))
    result = cur.fetchone()

    conn.commit()
    conn.close()

    #  No regresó nada → No existe
    if not result:
        raise HTTPException(404, "Consulta no encontrada")

    respuesta = result["fn_eliminar_consulta"]

    #  Si la función devuelve un error tipo:
    # { "status": "error", "message": "No existe la consulta" }
    if isinstance(respuesta, dict) and respuesta.get("status") == "error":
        raise HTTPException(400, respuesta.get("message", "Error al eliminar"))

    return respuesta


