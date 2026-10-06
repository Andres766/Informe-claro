"""Modelo de datos (ER): Usuario 1:N InformeCargado 1:N ValorExamen / PreguntaSugerida.

El PDF original NO se guarda: solo los valores extraídos y la explicación de la IA.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)

    informes: Mapped[list["InformeCargado"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class InformeCargado(Base):
    __tablename__ = "informe_cargado"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), index=True)
    fecha_carga: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    # Campos de apoyo (no están en el ER mínimo): resumen general y qué motor generó la explicación.
    resumen: Mapped[str] = mapped_column(Text, default="")
    motor: Mapped[str] = mapped_column(String(40), default="demo")

    usuario: Mapped[Usuario] = relationship(back_populates="informes")
    valores: Mapped[list["ValorExamen"]] = relationship(
        back_populates="informe", cascade="all, delete-orphan"
    )
    preguntas: Mapped[list["PreguntaSugerida"]] = relationship(
        back_populates="informe", cascade="all, delete-orphan"
    )


class ValorExamen(Base):
    __tablename__ = "valor_examen"

    id: Mapped[int] = mapped_column(primary_key=True)
    informe_id: Mapped[int] = mapped_column(ForeignKey("informe_cargado.id"), index=True)
    nombre_valor: Mapped[str] = mapped_column(String(160))
    unidad: Mapped[str] = mapped_column(String(40), default="")
    valor: Mapped[str] = mapped_column(String(40))
    rango_referencia: Mapped[str] = mapped_column(String(80), default="")
    # "normal" | "alto" | "bajo" | "sin_rango" — se calcula en el backend, no lo decide el LLM.
    estado: Mapped[str] = mapped_column(String(12), default="sin_rango")
    explicacion_ia: Mapped[str] = mapped_column(Text, default="")

    informe: Mapped[InformeCargado] = relationship(back_populates="valores")


class PreguntaSugerida(Base):
    __tablename__ = "pregunta_sugerida"

    id: Mapped[int] = mapped_column(primary_key=True)
    informe_id: Mapped[int] = mapped_column(ForeignKey("informe_cargado.id"), index=True)
    texto_pregunta: Mapped[str] = mapped_column(Text)

    informe: Mapped[InformeCargado] = relationship(back_populates="preguntas")
