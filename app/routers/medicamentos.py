from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.medicamentos import MedicamentoCreate, MedicamentoUpdate

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"])


# ----------------------------------------------------------
# Crear medicamento  (solo administrador)
# ----------------------------------------------------------
@router.post("/crear-medicamento", response_model=dict)
def crear_medicamento(data: MedicamentoCreate, user=Depends(get_current_user)):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_crear_medicamento(%s, %s)",
        (data.nombre, data.precio)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si la función no devolvió nada
    if not result:
        raise HTTPException(500, "Error al crear el medicamento")

    medicamento = result.get("fn_crear_medicamento")

    # Si la función retorna un JSON de error tipo:
    # RETURN json_build_object('status','error','message','Ya existe el medicamento');
    if isinstance(medicamento, dict) and medicamento.get("status") == "error":
        raise HTTPException(400, medicamento.get("message", "Error al crear medicamento"))

    # Si retorna NULL
    if medicamento is None:
        raise HTTPException(500, "Error inesperado al crear el medicamento")

    return medicamento



# ----------------------------------------------------------
# Obtener medicamento por ID
# ----------------------------------------------------------
@router.get("/obtener-medicamento/{medicamento_id}", response_model=dict)
def obtener_medicamento(medicamento_id: int, user=Depends(get_current_user)):

    # Todos pueden ver: administrador, veterinario, secretaria
    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_medicamento(%s)", (medicamento_id,))
    result = cur.fetchone()
    conn.close()

    # No devolvió ninguna fila
    if not result:
        raise HTTPException(404, "Medicamento no encontrado")

    medicamento = result.get("fn_obtener_medicamento")

    # Si la función devuelve un objeto tipo:
    # { "status": "error", "message": "Medicamento no existe" }
    if isinstance(medicamento, dict) and medicamento.get("status") == "error":
        raise HTTPException(404, medicamento.get("message", "Medicamento no encontrado"))

    # Si viene NULL por alguna razón
    if medicamento is None:
        raise HTTPException(404, "Medicamento no encontrado")

    return medicamento



# ----------------------------------------------------------
# Listar medicamentos
# ----------------------------------------------------------
@router.get("/listar-medicamentos", response_model=list)
def listar_medicamentos(user=Depends(get_current_user)):

    # Todos pueden ver: administrador, veterinario, secretaria
    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_medicamentos()")
    result = cur.fetchone()
    conn.close()

    # Si PostgreSQL no retornó ninguna fila
    if not result:
        raise HTTPException(404, "No se encontraron medicamentos")

    medicamentos = result.get("fn_listar_medicamentos")

    # Si la función retorna algo tipo:
    # { "status": "error", "message": "No hay medicamentos" }
    if isinstance(medicamentos, dict) and medicamentos.get("status") == "error":
        raise HTTPException(404, medicamentos.get("message", "No se encontraron medicamentos"))

    # Si retorna NULL
    if medicamentos is None:
        raise HTTPException(404, "No se encontraron medicamentos")

    # Si retorna lista vacía
    if isinstance(medicamentos, list) and len(medicamentos) == 0:
        raise HTTPException(404, "No hay medicamentos registrados aún")

    return medicamentos



# ----------------------------------------------------------
# Actualizar medicamento (solo administrador)
# ----------------------------------------------------------
@router.put("/actualizar-medicamento/{medicamento_id}", response_model=dict)
def actualizar_medicamento(medicamento_id: int, data: MedicamentoUpdate, user=Depends(get_current_user)):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_medicamento(%s, %s, %s)",
        (medicamento_id, data.nombre, data.precio)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # No regresó ninguna fila
    if not result:
        raise HTTPException(404, "Medicamento no encontrado")

    medicamento = result.get("fn_actualizar_medicamento")

    # Si PL/pgSQL retorna algo tipo:
    # RETURN json_build_object('status','error','message','Medicamento no existe')
    if isinstance(medicamento, dict) and medicamento.get("status") == "error":
        raise HTTPException(404, medicamento.get("message", "Medicamento no encontrado"))

    # Si viene NULL
    if medicamento is None:
        raise HTTPException(404, "Medicamento no encontrado")

    return medicamento



# ----------------------------------------------------------
# Eliminar medicamento (solo administrador)
# ----------------------------------------------------------
@router.delete("/eliminar-medicamento/{medicamento_id}", response_model=dict)
def eliminar_medicamento(medicamento_id: int, user=Depends(get_current_user)):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_medicamento(%s)", (medicamento_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si PL/pgSQL no retornó ninguna fila
    if not result:
        raise HTTPException(404, "Medicamento no encontrado")

    medicamento = result.get("fn_eliminar_medicamento")

    # Si PL/pgSQL devuelve un JSON tipo error:
    # { "status": "error", "message": "Medicamento no existe" }
    if isinstance(medicamento, dict) and medicamento.get("status") == "error":
        raise HTTPException(404, medicamento.get("message", "Medicamento no encontrado"))

    # Si viene NULL
    if medicamento is None:
        raise HTTPException(404, "Medicamento no encontrado")

    return medicamento
