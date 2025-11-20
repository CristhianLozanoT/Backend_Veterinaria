from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from datetime import date, datetime
from app.models.citas import CitaCreate, CitaUpdate

router = APIRouter(prefix="/citas", tags=["Citas"])


@router.post("/crear-cita", response_model=dict)
def crear_cita(data: CitaCreate, user=Depends(get_current_user)):

    if user["role"] not in ("administrador", "secretaria"):
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Verificar cita repetida (misma fecha + hora + veterinario)
    cur.execute("""
        SELECT id FROM citas
        WHERE fecha = %s
        AND hora = %s
        AND veterinario_id = %s
    """, (data.fecha, data.hora, data.veterinario_id))

    existe = cur.fetchone()

    if existe:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="El veterinario ya tiene una cita programada en esa fecha y hora."
        )
    # FECHA LLEGA COMO "2025-11-20" → LO FORZAMOS A DATE
    if isinstance(data.fecha, str):
        fecha = data.fecha.split("T")[0] if "T" in data.fecha else data.fecha
    elif isinstance(data.fecha, datetime):
        fecha = data.fecha.date().isoformat()
    elif isinstance(data.fecha, date):
        fecha = data.fecha.isoformat()
    else:
        fecha = str(data.fecha)

    # Crear la cita con tu función SQL correcta
    cur.execute(
        "SELECT fn_crear_cita(%s, %s, %s)",
        (fecha, data.hora, data.veterinario_id)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    if not result or not result["fn_crear_cita"]:
        raise HTTPException(500, "fn_crear_cita no retornó datos")

    return result["fn_crear_cita"]




@router.get("/obtener-cita/{cita_id}", response_model=dict)
def obtener_cita(cita_id: int, user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_cita(%s)", (cita_id,))
    result = cur.fetchone()

    conn.close()

    if not result or not result["fn_obtener_cita"]:
        raise HTTPException(
            status_code=404,
            detail=f"La cita con ID {cita_id} no existe."
        )

    cita = result["fn_obtener_cita"]

    # 🔒 Validación para veterinario
    if user["role"] == "veterinario" and cita["veterinario_id"] != user["id"]:
        raise HTTPException(
            status_code=403,
            detail="No autorizado a ver esta cita."
        )

    return cita



@router.get("/listar-citas", response_model=list)
def listar_citas(user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Veterinario
    if user["role"] == "veterinario":
        cur.execute("SELECT fn_listar_citas_por_veterinario(%s)", (user["id"],))
        row = cur.fetchone()
        conn.close()

        citas = row["fn_listar_citas_por_veterinario"] if row else None

        if not citas:
            return [{"message": "Aún no hay citas registradas para este veterinario"}]

        return citas

    # Admin o secretaria
    cur.execute("SELECT fn_listar_citas()")
    row = cur.fetchone()
    conn.close()

    citas = row["fn_listar_citas"] if row else None

    if not citas:
        return [{"message": "Aún no hay citas registradas"}]

    return citas



@router.put("/actualizar-cita/{cita_id}", response_model=dict)
def actualizar_cita(cita_id: int, data: CitaUpdate, user=Depends(get_current_user)):

    if user["role"] not in ["secretaria", "administrador", "veterinario"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # --- NORMALIZAR FECHA ---
    if isinstance(data.fecha, str):
        fecha = data.fecha.split("T")[0] if "T" in data.fecha else data.fecha
    elif isinstance(data.fecha, datetime):
        fecha = data.fecha.date().isoformat()
    elif isinstance(data.fecha, date):
        fecha = data.fecha.isoformat()
    else:
        fecha = str(data.fecha)

    # --- EJECUTAR FUNCIÓN SQL CON TIPOS CORRECTOS ---
    cur.execute(
        "SELECT fn_actualizar_cita(%s, %s::date, %s::time, %s, %s)",
        (cita_id, fecha, data.hora, data.veterinario_id, data.estado)
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()

    if not row or not row["fn_actualizar_cita"]:
        raise HTTPException(
            status_code=404,
            detail=f"La cita con ID {cita_id} no existe o no pudo ser actualizada."
        )

    return row["fn_actualizar_cita"]



@router.delete("/eliminar-cita/{cita_id}", response_model=dict)
def eliminar_cita(cita_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_cita(%s)", (cita_id,))
    row = cur.fetchone()

    conn.commit()
    conn.close()

    # Manejo de ambos casos:
    # 1) No hay fila
    # 2) Hay fila pero la función retornó NULL
    if not row or not row["fn_eliminar_cita"]:
        raise HTTPException(
            status_code=404,
            detail=f"La cita con ID {cita_id} no existe o ya fue eliminada."
        )

    return row["fn_eliminar_cita"]

@router.get("/listar-citas-veterinario", response_model=list)
def listar_citas_veterinario(user=Depends(get_current_user)):
    if user["role"] != "veterinario":
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_citas_por_veterinario(%s)", (user["id"],))
    row = cur.fetchone()
    conn.close()

    citas = row["fn_listar_citas_por_veterinario"] if row else None
    return citas or []

@router.put("/actualizar-estado/{cita_id}", response_model=dict)
def actualizar_estado(cita_id: int, data: dict, user=Depends(get_current_user)):

    if user["role"] != "veterinario":
        raise HTTPException(403, "No autorizado")

    estado = data.get("estado")
    if not estado:
        raise HTTPException(400, "El estado es requerido")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_estado_cita(%s, %s)",
        (cita_id, estado)
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()

    if not row or not row["fn_actualizar_estado_cita"]:
        raise HTTPException(
            status_code=404,
            detail=f"No se pudo actualizar el estado de la cita {cita_id}."
        )

    return row["fn_actualizar_estado_cita"]
