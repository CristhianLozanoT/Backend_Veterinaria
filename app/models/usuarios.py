from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    rol: Optional[str] = None

class UsuarioResponse(BaseModel):
    status: str
    id: int

    class Config:
        orm_mode = True
    
    
# inicio de sesión
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    id: int
    email: str
    role: str
