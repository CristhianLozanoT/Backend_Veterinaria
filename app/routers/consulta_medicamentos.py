from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.consulta_medicamentos import ConsultaMedicamentoUpdate, ConsultaMedicamentoCreate, ConsultaMedicamentoResponse

router = APIRouter(prefix="/consulta-medicamentos", tags=["Consulta Medicamentos"])


@router.post("/agregar", response_model=dict)
def agregar_medicamento(data: ConsultaMedicamentoCreate, user=Depends(get_current_user)):

    if user["role"] not in ["veterinario"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(
            "SELECT fn_agregar_medicamento_consulta(%s, %s, %s)",
            (data.consulta_id, data.medicamento_id, data.cantidad)
        )
        result = cur.fetchone()
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Error SQL: {e}")

    finally:
        conn.close()

    if not result:
        raise HTTPException(500, "Error inesperado: función sin retorno")

    respuesta = result.get("fn_agregar_medicamento_consulta")

    if not respuesta:
        raise HTTPException(500, "La función SQL no retornó datos")

    # Manejo de respuestas personalizadas desde SQL
    if respuesta.get("status") == "error":
        raise HTTPException(
            status_code=400,
            detail=respuesta.get("message", "Error al agregar medicamento")
        )

    return respuesta




@router.get("/listar/{consulta_id}", response_model=list)
def listar_medicamentos_consulta(consulta_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_listar_medicamentos_consulta(%s)",
        (consulta_id,)
    )

    result = cur.fetchone()
    conn.close()

    if not result:
        return []  # ← devolver lista vacía

    respuesta = result.get("fn_listar_medicamentos_consulta")

    # Si no hay medicamentos → lista vacía, NO error
    if respuesta is None:
        return []

    if isinstance(respuesta, list) and len(respuesta) == 0:
        return []

    return respuesta



@router.put("/actualizar", response_model=dict)
def actualizar_medicamento(data: ConsultaMedicamentoCreate, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_medicamento_consulta(%s, %s, %s)",
        (data.consulta_id, data.medicamento_id, data.cantidad)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    if not result:
        raise HTTPException(500, "No se pudo actualizar el medicamento")

    respuesta = result.get("fn_actualizar_medicamento_consulta")

    if isinstance(respuesta, dict) and respuesta.get("status") == "error":
        raise HTTPException(400, respuesta.get("message", "Error al actualizar"))

    return respuesta



@router.delete("/eliminar/{consulta_id}/{medicamento_id}", response_model=dict)
def eliminar_medicamento(consulta_id: int,medicamento_id: int,
    user=Depends(get_current_user)):

    if user["role"] not in ["veterinario"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_eliminar_medicamento_consulta(%s, %s)",
        (consulta_id, medicamento_id)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    if not result:
        raise HTTPException(404, "No se pudo eliminar, no existe registro")

    respuesta = result.get("fn_eliminar_medicamento_consulta")

    if isinstance(respuesta, dict) and respuesta.get("status") == "error":
        raise HTTPException(400, respuesta.get("message", "Error al eliminar"))

    return respuesta
