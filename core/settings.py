"""Merkezi yapılandırma (Pydantic BaseSettings). .env'den okunur.

Eski `config.py` modülü geriye dönük uyumluluk için korunur; yeni kod bu
`settings` nesnesini kullanır.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- EVREN LLM ---
    evren_base_url: str = Field("https://evren-llmapi.ssyz.org.tr/v1", alias="EVREN_BASE_URL")
    evren_api_key: str = Field("", alias="EVREN_API_KEY")
    evren_timeout: int = Field(1800, alias="EVREN_TIMEOUT")
    llm_model: str = Field("llm-fast", alias="LLM_MODEL")
    embedding_model: str = Field("bge-m3-embed", alias="EMBEDDING_MODEL")
    embedding_dim: int = Field(1024, alias="EMBEDDING_DIM")

    # --- EVREN Qdrant ---
    qdrant_url: str = Field("https://evren-vektor.ssyz.org.tr", alias="QDRANT_URL")
    qdrant_port: int = Field(443, alias="QDRANT_PORT")
    evren_team: str = Field("", alias="EVREN_TEAM")
    evren_qdrant_key: str = Field("", alias="EVREN_QDRANT_KEY")
    qdrant_collection: str = Field("karonext_products", alias="QDRANT_COLLECTION")
    qdrant_timeout: int = Field(600, alias="QDRANT_TIMEOUT")
    default_top_k: int = Field(5, alias="DEFAULT_TOP_K")

    # --- API / CORS ---
    cors_origins: str = Field(
        "http://localhost:5173,http://localhost:4173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")

    # --- Sağlayıcı seçimi (ileride lokal modele geçiş için) ---
    llm_backend: str = Field("evren", alias="LLM_BACKEND")  # evren | local
    embedding_backend: str = Field("evren", alias="EMBEDDING_BACKEND")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def db_path(self) -> Path:
        return BASE_DIR / "data" / "final" / "karonext.sqlite"


settings = Settings()
