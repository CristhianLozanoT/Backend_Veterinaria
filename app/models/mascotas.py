from pydantic import BaseModel
from typing import Optional

class MascotaBase(BaseModel):
    nombre: str
    raza_id: int
    edad: int
    peso: float

class MascotaCreate(MascotaBase):
    cliente_id: int   # ← Este es el único que se agrega

class MascotaUpdate(BaseModel):
    nombre: Optional[str] = None
    raza_id: Optional[int] = None
    edad: Optional[int] = None
    peso: Optional[float] = None

class MascotaResponse(BaseModel):
    id: int
    cliente_id: int | None=None
    nombre: str
    raza_id: int
    edad: int
    peso: float

    class Config:
        from_attributes = True
