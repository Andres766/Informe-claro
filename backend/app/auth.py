"""Autenticación: registro, inicio de sesión y dependencia `usuario_actual`."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .schemas import LoginIn, RegistroIn, SesionOut, UsuarioOut
from .security import crear_token, hashear_password, leer_token, verificar_password

router = APIRouter(prefix="/api/auth", tags=["autenticación"])
_bearer = HTTPBearer(auto_error=False)


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.Usuario:
    """Exige un token válido; cada usuario solo accede a su propio historial."""
    usuario_id = leer_token(credenciales.credentials) if credenciales else None
    usuario = db.get(models.Usuario, usuario_id) if usuario_id else None
    if not usuario:
        raise HTTPException(401, "Inicia sesión para continuar", headers={"WWW-Authenticate": "Bearer"})
    return usuario


def _sesion(usuario: models.Usuario) -> SesionOut:
    return SesionOut(access_token=crear_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.post("/registro", response_model=SesionOut, status_code=201)
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    email = datos.email.lower()
    if db.scalar(select(models.Usuario).where(models.Usuario.email == email)):
        raise HTTPException(409, "Ya existe una cuenta con ese correo")
    usuario = models.Usuario(
        nombre=datos.nombre.strip(), email=email, password_hash=hashear_password(datos.password)
    )
    db.add(usuario)
    db.commit()
    return _sesion(usuario)


@router.post("/login", response_model=SesionOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(models.Usuario).where(models.Usuario.email == datos.email.lower()))
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        # Mismo mensaje en ambos casos para no revelar qué correos están registrados.
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return _sesion(usuario)


@router.get("/yo", response_model=UsuarioOut)
def yo(usuario: models.Usuario = Depends(usuario_actual)):
    return usuario
