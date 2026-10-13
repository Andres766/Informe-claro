"""Esquemas Pydantic de la API (respuestas al frontend)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegistroIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)  # bcrypt solo usa los primeros 72 bytes


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str


class SesionOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


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
