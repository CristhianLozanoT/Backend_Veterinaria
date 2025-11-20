from pydantic import BaseModel
from typing import Optional


class ConsultaMedicamentoBase(BaseModel):
    consulta_id: int
    medicamento_id: int
    cantidad: int


class ConsultaMedicamentoCreate(ConsultaMedicamentoBase):
    pass


class ConsultaMedicamentoUpdate(BaseModel):
    cantidad: Optional[int] = None


class ConsultaMedicamentoResponse(BaseModel):
    consulta_id: int
    medicamento_id: int
    cantidad: int

    class Config:
        from_attributes = True
