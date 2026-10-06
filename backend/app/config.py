"""Configuración central leída desde variables de entorno / archivo .env."""
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # En desarrollo se usa SQLite; en producción apuntar a PostgreSQL (Render / Supabase / Neon).
    database_url: str = "sqlite:///./informeclaro.db"

    # Si no hay API key, el orquestador trabaja en "modo demo" (extracción por reglas).
    anthropic_api_key: str | None = None
    llm_model: str = "claude-opus-5"

    # Se acepta separado por comas: "https://app.vercel.app,http://localhost:5173"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    max_pdf_mb: int = 10

    @field_validator("database_url")
    @classmethod
    def usar_driver_psycopg(cls, url: str) -> str:
        # Render/Neon/Supabase entregan "postgres://" o "postgresql://"; SQLAlchemy necesita el driver explícito.
        for prefijo in ("postgres://", "postgresql://"):
            if url.startswith(prefijo):
                return "postgresql+psycopg://" + url[len(prefijo):]
        return url

    @field_validator("cors_origins", mode="before")
    @classmethod
    def separar_origenes(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip().strip("[]")
            return [o.strip().strip("\"'").rstrip("/") for o in valor.split(",") if o.strip()]
        return valor


settings = Settings()
