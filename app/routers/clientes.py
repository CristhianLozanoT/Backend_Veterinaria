from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.clientes import ClienteCreate, ClienteUpdate

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/crear-cliente", response_model=dict)
def crear_cliente(data: ClienteCreate, user=Depends(get_current_user)):

    if user["role"] != "veterinario":
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # OPCIONAL: verificar si el cliente ya existe por nombre + telefono
    cur.execute("""
        SELECT id FROM clientes 
        WHERE nombre = %s AND telefono = %s
    """, (data.nombre, data.telefono))

    existe = cur.fetchone()
    
    if existe:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="El cliente ya existe."
        )

    # Crear cliente
    cur.execute(
        "SELECT fn_crear_cliente(%s, %s, %s)",
        (data.nombre, data.telefono, data.direccion)
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()

    # Manejo de errores: resultado vacío o función retornó NULL
    if not row or not row["fn_crear_cliente"]:
        raise HTTPException(
            status_code=500,
            detail="No se pudo crear el cliente. Intenta nuevamente."
        )

    return row["fn_crear_cliente"]


@router.get("/obtener-cliente/{cliente_id}", response_model=dict)
def obtener_cliente(cliente_id: int, user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_cliente(%s)", (cliente_id,))
    row = cur.fetchone()
    conn.close()

    # Manejo de ambos errores:
    # 1) No llegó fila
    # 2) La función retornó NULL
    if not row or not row["fn_obtener_cliente"]:
        raise HTTPException(
            status_code=404,
            detail=f"El cliente con ID {cliente_id} no existe."
        )

    return row["fn_obtener_cliente"]


@router.get("/listar-clientes", response_model=list)
def listar_clientes(user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_clientes()")
    row = cur.fetchone()
    conn.close()

    clientes = row["fn_listar_clientes"] if row else None

    # Si no hay clientes → devolvemos mensaje dentro de una lista
    if not clientes:
        return [{"message": "Aún no hay clientes registrados"}]

    return clientes



@router.put("/actualizar-cliente/{cliente_id}", response_model=dict)
def actualizar_cliente(cliente_id: int, data: ClienteUpdate, user=Depends(get_current_user)):

    if user["role"] not in ["veterinario", "administrador"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_cliente(%s, %s, %s, %s)",
        (cliente_id, data.nombre, data.telefono, data.direccion)
    )

    row = cur.fetchone()
    conn.commit()
    conn.close()

    # Manejo correcto de ambos casos:
    # 1) No llegó fila
    # 2) La función retornó NULL
    if not row or not row["fn_actualizar_cliente"]:
        raise HTTPException(
            status_code=404,
            detail=f"El cliente con ID {cliente_id} no existe o no pudo actualizarse."
        )

    return row["fn_actualizar_cliente"]



@router.delete("/eliminar-cliente/{cliente_id}", response_model=dict)
def eliminar_cliente(cliente_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["veterinario", "administrador"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_cliente(%s)", (cliente_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()

    # Manejo de ambos casos:
    # 1) La función no retorno fila
    # 2) La función retornó NULL
    if not row or not row["fn_eliminar_cliente"]:
        raise HTTPException(
            status_code=404,
            detail=f"El cliente con ID {cliente_id} no existe o ya fue eliminado."
        )

    return row["fn_eliminar_cliente"]
