from pydantic import BaseModel
from typing import Optional

class FacturaBase(BaseModel):
    consulta_id: int
    total: float


class FacturaCreate(FacturaBase):
    pass


class FacturaUpdate(BaseModel):
    total: Optional[float] = None


class FacturaResponse(BaseModel):
    id: int
    consulta_id: int
    total: float

    class Config:
        from_attributes = True
