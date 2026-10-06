"""API Backend (FastAPI) — orquestador central de InformeClaro.

Flujo de POST /api/informes:
  1. recibe el PDF  2. extrae texto  3-5. prompt con guardrails + LLM
  6. persiste valores y preguntas (sin el PDF) y responde al frontend.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from . import models
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .schemas import InformeDetalleOut, InformeResumenOut
from .services.pdf_parser import PDFInvalidoError, anonimizar, extraer_texto
from .services.prompt_orchestrator import AVISO_MEDICO, interpretar

logging.basicConfig(level=logging.INFO)

EMAIL_DEMO = "paciente.demo@informeclaro.co"


def _crear_usuario_demo():
    with SessionLocal() as db:
        if not db.scalar(select(models.Usuario).where(models.Usuario.email == EMAIL_DEMO)):
            db.add(models.Usuario(nombre="Paciente Demo", email=EMAIL_DEMO))
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    _crear_usuario_demo()
    yield


app = FastAPI(title="InformeClaro API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def usuario_actual(db: Session = Depends(get_db)) -> models.Usuario:
    # TODO (siguiente entrega): autenticación con JWT. Por ahora todo se asocia al usuario demo.
    return db.scalar(select(models.Usuario).where(models.Usuario.email == EMAIL_DEMO))


def _detalle(informe: models.InformeCargado) -> InformeDetalleOut:
    return InformeDetalleOut(
        id=informe.id,
        nombre_archivo=informe.nombre_archivo,
        fecha_carga=informe.fecha_carga,
        motor=informe.motor,
        resumen=informe.resumen,
        valores=informe.valores,
        preguntas=informe.preguntas,
        aviso=AVISO_MEDICO,
    )


def _informe_del_usuario(informe_id: int, usuario: models.Usuario, db: Session) -> models.InformeCargado:
    informe = db.scalar(
        select(models.InformeCargado)
        .where(models.InformeCargado.id == informe_id, models.InformeCargado.usuario_id == usuario.id)
        .options(selectinload(models.InformeCargado.valores), selectinload(models.InformeCargado.preguntas))
    )
    if not informe:
        raise HTTPException(404, "Informe no encontrado")
    return informe


@app.get("/api/salud")
def salud():
    return {"estado": "ok", "motor": settings.llm_model if settings.anthropic_api_key else "demo (reglas)"}


@app.post("/api/informes", response_model=InformeDetalleOut, status_code=201)
async def subir_informe(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_actual),
):
    if archivo.content_type != "application/pdf" and not (archivo.filename or "").lower().endswith(".pdf"):
        raise HTTPException(415, "Solo se aceptan archivos PDF")

    contenido = await archivo.read()
    if len(contenido) > settings.max_pdf_mb * 1024 * 1024:
        raise HTTPException(413, f"El PDF supera {settings.max_pdf_mb} MB")

    try:
        texto = extraer_texto(contenido)
    except PDFInvalidoError as exc:
        raise HTTPException(422, str(exc))
    del contenido  # el PDF original no se conserva

    resultado = interpretar(anonimizar(texto))
    if not resultado.valores:
        raise HTTPException(422, "No se encontraron valores de laboratorio en el PDF")

    informe = models.InformeCargado(
        usuario_id=usuario.id,
        nombre_archivo=archivo.filename or "informe.pdf",
        resumen=resultado.resumen,
        motor=resultado.motor,
        valores=[
            models.ValorExamen(
                nombre_valor=v.nombre_valor, unidad=v.unidad, valor=v.valor,
                rango_referencia=v.rango_referencia, estado=v.estado, explicacion_ia=v.explicacion,
            )
            for v in resultado.valores
        ],
        preguntas=[models.PreguntaSugerida(texto_pregunta=p) for p in resultado.preguntas],
    )
    db.add(informe)
    db.commit()
    return _detalle(informe)


@app.get("/api/informes", response_model=list[InformeResumenOut])
def listar_informes(db: Session = Depends(get_db), usuario: models.Usuario = Depends(usuario_actual)):
    informes = db.scalars(
        select(models.InformeCargado)
        .where(models.InformeCargado.usuario_id == usuario.id)
        .options(selectinload(models.InformeCargado.valores))
        .order_by(models.InformeCargado.fecha_carga.desc())
    ).all()
    return [
        InformeResumenOut(
            id=i.id, nombre_archivo=i.nombre_archivo, fecha_carga=i.fecha_carga, motor=i.motor,
            total_valores=len(i.valores),
            fuera_de_rango=sum(v.estado in ("alto", "bajo") for v in i.valores),
        )
        for i in informes
    ]


@app.get("/api/informes/{informe_id}", response_model=InformeDetalleOut)
def ver_informe(informe_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(usuario_actual)):
    return _detalle(_informe_del_usuario(informe_id, usuario, db))


@app.delete("/api/informes/{informe_id}", status_code=204)
def eliminar_informe(informe_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(usuario_actual)):
    db.delete(_informe_del_usuario(informe_id, usuario, db))
    db.commit()
