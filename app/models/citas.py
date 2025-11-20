from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from datetime import time

class CitaBase(BaseModel):
    veterinario_id: int
    fecha: datetime


class CitaCreate(CitaBase):
    fecha: datetime
    hora: time
    veterinario_id: int

class CitaUpdate(BaseModel):
    fecha: Optional[datetime] = None
    hora: Optional[time] = None
    veterinario_id: Optional[int] = None
    estado: Optional[str] = None

class CitaResponse(BaseModel):
    id: int
    fecha: datetime
    hora: time
    veterinario_id: int
    estado: Optional[str] = None

    class Config:
        from_attributes = True
