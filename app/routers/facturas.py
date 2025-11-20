from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.facturas import FacturaCreate, FacturaUpdate, FacturaResponse

router = APIRouter(prefix="/facturas", tags=["Facturas"])


# -----------------------------
#   CREAR FACTURA
# -----------------------------
@router.post("/crear-factura", response_model=dict)
def crear_factura(data: FacturaCreate, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_crear_factura(%s, %s)",
        (data.consulta_id, data.total)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si la función no retornó nada → error interno
    if not result:
        raise HTTPException(500, "fn_crear_factura no retornó datos")

    respuesta = result["fn_crear_factura"]

    # Si la función devuelve algo como:
    # { "status": "error", "message": "El cliente no existe" }
    if isinstance(respuesta, dict) and respuesta.get("status") == "error":
        raise HTTPException(400, respuesta.get("message", "Error al crear factura"))

    return respuesta

# -----------------------------
#   OBTENER FACTURA POR ID
# -----------------------------
@router.get("/obtener-factura/{factura_id}", response_model=dict)
def obtener_factura(factura_id: int, user=Depends(get_current_user)):

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_factura(%s)", (factura_id,))
    result = cur.fetchone()
    conn.close()

    # Si no existe ninguna respuesta desde PostgreSQL
    if not result:
        raise HTTPException(404, "Factura no encontrada")

    factura = result["fn_obtener_factura"]

    # Si la función devuelve un error desde PostgreSQL:
    # { "status": "error", "message": "Factura no existe" }
    if isinstance(factura, dict) and factura.get("status") == "error":
        raise HTTPException(404, factura.get("message", "Factura no encontrada"))

    return factura



# -----------------------------
#   LISTAR TODAS LAS FACTURAS
# -----------------------------
@router.get("/listar-facturas", response_model=list)
def listar_facturas(user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_facturas()")
    result = cur.fetchone()
    conn.close()

    # Si PostgreSQL no devolvió nada
    if not result:
        raise HTTPException(404, "No se encontraron facturas")

    facturas = result["fn_listar_facturas"]

    # Si la función devuelve un error estructurado
    if isinstance(facturas, dict) and facturas.get("status") == "error":
        raise HTTPException(400, facturas.get("message", "Error al listar facturas"))

    # Si la lista está vacía → enviar mensaje amigable al frontend
    if isinstance(facturas, list) and len(facturas) == 0:
        raise HTTPException(404, "Aún no existen facturas registradas")

    return facturas



# -----------------------------
#   ACTUALIZAR FACTURA
# -----------------------------
@router.put("/actualizar-factura/{factura_id}", response_model=dict)
def actualizar_factura(factura_id: int, data: FacturaUpdate, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_factura(%s, %s)",
        (factura_id, data.total)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si PostgreSQL no devolvió nada
    if not result:
        raise HTTPException(404, "Factura no encontrada")

    factura = result["fn_actualizar_factura"]

    # Si la función maneja errores internos
    # Por ejemplo:
    # RETURN json_build_object('status', 'error', 'message', 'Factura no existe');
    if isinstance(factura, dict) and factura.get("status") == "error":
        raise HTTPException(404, factura.get("message", "Factura no encontrada"))

    return factura


# -----------------------------
#   ELIMINAR FACTURA
# -----------------------------
@router.delete("/eliminar-factura/{factura_id}", response_model=dict)
def eliminar_factura(factura_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_factura(%s)", (factura_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si PostgreSQL no regresó ninguna fila
    if not result:
        raise HTTPException(404, "Factura no encontrada")

    factura = result["fn_eliminar_factura"]

    # Validar si la función retorna un JSON de error interno
    # Ejemplo desde PostgreSQL:
    # RETURN json_build_object('status', 'error', 'message', 'Factura no existe');
    if isinstance(factura, dict) and factura.get("status") == "error":
        raise HTTPException(404, factura.get("message", "Factura no encontrada"))

    return factura

