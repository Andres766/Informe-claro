"""Conexión a la base de datos con SQLAlchemy 2."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrar_columnas_nuevas():
    """Añade columnas que se agregaron al modelo después de crear las tablas.

    create_all() no modifica tablas existentes (p. ej. la BD ya desplegada en Render).
    """
    from sqlalchemy import inspect, text

    columnas = {c["name"] for c in inspect(engine).get_columns("usuario")}
    if "password_hash" not in columnas:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE usuario ADD COLUMN password_hash VARCHAR(100)"))
