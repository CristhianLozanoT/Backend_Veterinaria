from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from psycopg2.extras import RealDictCursor
from app.models.mascotas import MascotaCreate, MascotaUpdate, MascotaResponse

router = APIRouter(prefix="/mascotas", tags=["Mascotas"])

@router.post("/crear-mascota", response_model=dict)
def crear_mascota(data: MascotaCreate, user=Depends(get_current_user)):

    if user["role"] not in ["veterinario", "administrador"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_crear_mascota(%s, %s, %s, %s, %s)",
        (data.cliente_id, data.raza_id, data.nombre, data.edad, data.peso)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si no devuelve nada
    if not result:
        raise HTTPException(500, "No se pudo crear la mascota")

    mascota = result.get("fn_crear_mascota")

    # Si la función retorna un error personalizado
    # Ejemplo PostgreSQL:
    # RETURN json_build_object('status','error','message','La raza no existe');
    if isinstance(mascota, dict) and mascota.get("status") == "error":
        raise HTTPException(400, mascota.get("message", "Error al crear la mascota"))

    return mascota


@router.get("/obtener-mascota/{mascota_id}", response_model=dict)
def obtener_mascota(mascota_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_mascota(%s)", (mascota_id,))
    result = cur.fetchone()
    conn.close()

    # Si no regresó ninguna fila
    if not result:
        raise HTTPException(404, "Mascota no encontrada")

    mascota = result.get("fn_obtener_mascota")

    # Si tu función retorna algo como:
    # RETURN json_build_object('status','error','message','Mascota no existe')
    if isinstance(mascota, dict) and mascota.get("status") == "error":
        raise HTTPException(404, mascota.get("message", "Mascota no encontrada"))

    return mascota



@router.get("/listar-mascotas", response_model=dict)
def listar_mascotas(user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_mascotas()")
    result = cur.fetchone()
    conn.close()

    # Si PostgreSQL no devolvió ninguna fila
    if not result:
        raise HTTPException(404, "No se encontraron mascotas")

    mascotas = result.get("fn_listar_mascotas")

    # Si tu función retorna un error personalizado
    # Ejemplo:
    # RETURN json_build_object('status','error','message','No hay mascotas')
    if isinstance(mascotas, dict) and mascotas.get("status") == "error":
        raise HTTPException(404, mascotas.get("message", "No se encontraron mascotas"))

    # Si retorna null desde PostgreSQL
    if mascotas is None:
        raise HTTPException(404, "No se encontraron mascotas")

    # Si retorna una lista vacía — también mandamos mensaje al frontend
    if isinstance(mascotas, list) and len(mascotas) == 0:
        raise HTTPException(404, "No hay mascotas registradas aún")

    return {"data": mascotas}




@router.put("/actualizar-mascota/{mascota_id}", response_model=dict)
def actualizar_mascota(mascota_id: int, data: MascotaUpdate, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_mascota(%s, %s, %s, %s, %s)",
        (mascota_id, data.raza_id, data.nombre, data.edad, data.peso)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si la función no devolvió nada
    if not result:
        raise HTTPException(404, "Mascota no encontrada")

    mascota = result.get("fn_actualizar_mascota")

    # Si tu función retorna:
    # RETURN json_build_object('status','error','message','La mascota no existe');
    if isinstance(mascota, dict) and mascota.get("status") == "error":
        raise HTTPException(404, mascota.get("message", "Mascota no encontrada"))

    # Protección extra por si retorna NULL
    if mascota is None:
        raise HTTPException(404, "Mascota no encontrada")

    return mascota




@router.delete("/eliminar-mascota/{mascota_id}", response_model=dict)
def eliminar_mascota(mascota_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_mascota(%s)", (mascota_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si la función no devolvió nada
    if not result:
        raise HTTPException(404, "Mascota no encontrada")

    mascota = result.get("fn_eliminar_mascota")

    # Si la función retorna un error personalizado
    # Ejemplo:
    # RETURN json_build_object('status','error','message','Mascota no existe');
    if isinstance(mascota, dict) and mascota.get("status") == "error":
        raise HTTPException(404, mascota.get("message", "Mascota no encontrada"))

    # Protección por si retorna NULL
    if mascota is None:
        raise HTTPException(404, "Mascota no encontrada")

    return mascota


@router.get("/por-cliente/{cliente_id}", response_model=list[MascotaResponse])
def mascotas_por_cliente(cliente_id: int, user=Depends(get_current_user)):

    if user["role"] not in ["administrador", "veterinario", "secretaria"]:
        raise HTTPException(403, "No autorizado")

    conn = get_connection(user["role"])
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_mascotas_por_cliente(%s)", (cliente_id,))
    row = cur.fetchone()
    conn.close()

    # No llegó nada desde PostgreSQL
    if not row:
        raise HTTPException(404, "No se pudo consultar las mascotas")

    resultado = row["fn_mascotas_por_cliente"]

    # Si la función devuelve NULL
    if resultado is None:
        return [{"message": "Este cliente no tiene mascotas registradas"}]

    # Si devuelve una lista vacía
    if isinstance(resultado, list) and len(resultado) == 0:
        return [{"message": "Este cliente no tiene mascotas registradas"}]

    return resultado