from pydantic import BaseModel
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    telefono: str
    direccion: str

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    telefono: str
    direccion: str

    class Config:
        from_attributes = True
