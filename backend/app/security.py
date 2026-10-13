"""Seguridad: hash de contraseñas (bcrypt) y tokens de sesión (JWT)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings

ALGORITMO = "HS256"


def hashear_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verificar_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def crear_token(usuario_id: int) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {"sub": str(usuario_id), "iat": ahora, "exp": ahora + timedelta(hours=settings.jwt_horas)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITMO)


def leer_token(token: str) -> int | None:
    """Devuelve el id del usuario, o None si el token es inválido o expiró."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITMO])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
