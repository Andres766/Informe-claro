"""Esquemas Pydantic de la API (respuestas al frontend)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ValorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_valor: str
    unidad: str
    valor: str
    rango_referencia: str
    estado: str
    explicacion_ia: str


class PreguntaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    texto_pregunta: str


class InformeResumenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_archivo: str
    fecha_carga: datetime
    motor: str
    total_valores: int
    fuera_de_rango: int


class InformeDetalleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_archivo: str
    fecha_carga: datetime
    motor: str
    resumen: str
    valores: list[ValorOut]
    preguntas: list[PreguntaOut]
    aviso: str
