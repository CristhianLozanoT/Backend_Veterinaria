from fastapi import APIRouter, HTTPException, Depends
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from app.database import get_connection
from app.models.usuarios import LoginRequest, TokenData

router = APIRouter(prefix="/auth", tags=["Auth"])

auth_scheme = HTTPBearer()


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

SECRET = os.environ["JWT_SECRET"]
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
EXPIRES = int(os.getenv("JWT_EXPIRES", "60"))

# ---------------------------------------
#      GENERAR TOKEN
# ---------------------------------------
def crear_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRES)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return token


# ---------------------------------------
#      LOGIN
# ---------------------------------------

@router.post("/login")
def login(credentials: LoginRequest):
    # Conectarse como administrador o superuser
    conn = get_connection("administrador")
    cur = conn.cursor()

    cur.execute("SELECT * FROM usuarios WHERE email = %s", (credentials.email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # Convertir la tupla de resultado en un dict usando los nombres de columna
    if cur.description:
        columns = [col[0] for col in cur.description]
        user = dict(zip(columns, row))
    else:
        # Ajusta esta lista si el orden de columnas de la tabla es distinto.
        fallback_columns = ["id", "nombre", "email", "password_hash", "rol"]
        user = dict(zip(fallback_columns, row))

    conn.close()

    stored_hash = user.get("password_hash") or user.get("password")
    if not stored_hash:
        raise HTTPException(status_code=500, detail="Hash de contraseña no disponible")
    if not pwd_context.verify(credentials.password, stored_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = crear_token({
        "id": user["id"],
        "email": user["email"],
        "role": user["rol"]
    })

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": user["id"],
            "email": user["email"],
            "role": user["rol"]}
}



# ---------------------------------------
#      OBTENER USUARIO DESDE TOKEN
# ---------------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    token = credentials.credentials 

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

        id_val = payload.get("id")
        email = payload.get("email")
        role = payload.get("role")

        if not id_val or not email or not role:
            raise HTTPException(status_code=401, detail="Token inválido: faltan campos obligatorios")

        try:
            id_int = int(id_val)
        except ValueError:
            raise HTTPException(status_code=401, detail="Token inválido: id no válido")

        # Construir TokenData
        user_data = TokenData(
            id=id_int,
            email=email,
            role=role
        )

        return user_data.dict()

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
