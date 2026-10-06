"""Configuración central leída desde variables de entorno / archivo .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # En desarrollo se usa SQLite; en producción apuntar a PostgreSQL (Supabase / Neon):
    #   postgresql+psycopg://usuario:clave@host:5432/informeclaro
    database_url: str = "sqlite:///./informeclaro.db"

    # Si no hay API key, el orquestador trabaja en "modo demo" (extracción por reglas).
    anthropic_api_key: str | None = None
    llm_model: str = "claude-opus-5"

    cors_origins: list[str] = ["http://localhost:5173"]
    max_pdf_mb: int = 10


settings = Settings()
