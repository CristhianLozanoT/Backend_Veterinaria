from pydantic import BaseModel
from typing import Optional

class ConsultaBase(BaseModel):
    cita_id: int
    cliente_id: int
    mascota_id: int
    veterinario_id: int
    diagnostico: str
    total: float

class ConsultaCreate(ConsultaBase):
    pass

class ConsultaUpdate(BaseModel):
    cliente_id: Optional[int] = None
    mascota_id: Optional[int] = None
    diagnostico: Optional[str] = None
    total: Optional[float] = None

class ConsultaResponse(BaseModel):
    id: int
    cita_id: int
    cliente_id: int
    mascota_id: int
    veterinario_id: int
    diagnostico: str
    total: float

    class Config:
        from_attributes = True
