from pydantic import BaseModel
from typing import Optional

class MedicamentoCreate(BaseModel):
    nombre: str
    precio: float

class MedicamentoUpdate(BaseModel):
    nombre: Optional[str] = None
    precio:  Optional[float] = None
