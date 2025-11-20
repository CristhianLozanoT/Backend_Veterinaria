from pydantic import BaseModel
from typing import Optional

class RazaCreate(BaseModel):
    nombre: str
    descripcion: str


class RazaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class RazaResponse(BaseModel):
    status: str
    id: int