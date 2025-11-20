from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
from app.database import get_connection
from app.models.usuarios import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from passlib.context import CryptContext
from psycopg2.extras import RealDictCursor


router = APIRouter()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

@router.post("/crear-usuario", response_model=dict)
def crear_usuario(data: UsuarioCreate, user=Depends(get_current_user)):
    
    # Solo el administrador puede crear usuarios
    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    # Hashear contraseña antes de guardar
    password_hash = pwd_context.hash(data.password)

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_crear_usuario(%s, %s, %s, %s)",
        (data.nombre, data.email, password_hash, data.rol)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si no retorna nada → error interno
    if not result:
        raise HTTPException(500, "fn_crear_usuario no retornó datos")

    usuario = result["fn_crear_usuario"]

    # Si la función retorna NULL → error
    if usuario is None:
        raise HTTPException(500, "Error creando el usuario")

    # Si tu función maneja errores estilo:
    # { "status": "error", "message": "El correo ya existe" }
    if isinstance(usuario, dict) and usuario.get("status") == "error":
        raise HTTPException(400, usuario.get("message", "Error creando usuario"))

    return usuario



@router.get("/obtener-usuario/{usuario_id}", response_model=dict)
def obtener_usuario(usuario_id: int, user=Depends(get_current_user)):

    # Solo el administrador puede ver usuarios
    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_obtener_usuario(%s)", (usuario_id,))
    result = cur.fetchone()

    conn.close()

    # Si la función no retorna nada → usuario no existe
    if not result:
        raise HTTPException(404, "Usuario no encontrado")

    usuario = result["fn_obtener_usuario"]

    # Si retorna NULL como resultado
    if usuario is None:
        raise HTTPException(404, "Usuario no encontrado")

    # Si retorna estructura estilo:
    # { "status": "error", "message": "Usuario no existe" }
    if isinstance(usuario, dict) and usuario.get("status") == "error":
        raise HTTPException(404, usuario.get("message", "Usuario no encontrado"))

    return usuario




@router.get("/listar-usuarios", response_model=list)
def listar_usuarios(user=Depends(get_current_user)):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_listar_usuarios()")
    result = cur.fetchone()

    conn.close()

    # Si no viene nada
    if not result:
        raise HTTPException(404, "No se encontraron usuarios")

    usuarios = result["fn_listar_usuarios"]

    # Si la función devuelve NULL
    if usuarios is None:
        raise HTTPException(404, "No se encontraron usuarios")

    # Si devuelve lista vacía
    if isinstance(usuarios, list) and len(usuarios) == 0:
        raise HTTPException(404, "No hay usuarios registrados")

    return usuarios


@router.put("/actualizar-usuario/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario( usuario_id: int,data: UsuarioUpdate,
    user=Depends(get_current_user)
):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    # Si envía contraseña nueva, se encripta
    password_hash = pwd_context.hash(data.password) if data.password else None

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT fn_actualizar_usuario(%s, %s, %s, %s, %s);",
        (usuario_id, data.nombre, data.email, password_hash, data.rol)
    )

    result = cur.fetchone()
    conn.commit()
    conn.close()

    # Si la función no retornó nada
    if not result or result["fn_actualizar_usuario"] is None:
        raise HTTPException(404, "Usuario no encontrado")

    return result["fn_actualizar_usuario"]



@router.delete("/eliminar-usuario/{usuario_id}", response_model=dict)
def eliminar_usuario(usuario_id: int, user=Depends(get_current_user)):

    if user["role"] != "administrador":
        raise HTTPException(403, "No autorizado")

    conn = get_connection("administrador")
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT fn_eliminar_usuario(%s);", (usuario_id,))
    result = cur.fetchone()

    conn.commit()
    conn.close()

    # Si la función no retornó nada o retornó NULL
    if not result or result["fn_eliminar_usuario"] is None:
        raise HTTPException(404, "Usuario no encontrado")

    return result["fn_eliminar_usuario"]
