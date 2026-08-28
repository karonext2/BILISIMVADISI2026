from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ---------------- EVREN ----------------
EVREN_BASE_URL = os.getenv(
    "EVREN_BASE_URL",
    "https://evren-llmapi.ssyz.org.tr/v1",
).rstrip("/")

EVREN_API_KEY = os.getenv("EVREN_API_KEY", "").strip()

LLM_MODEL = os.getenv("LLM_MODEL", "llm-fast").strip()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3-embed").strip()

# Dokümantasyonda istemci için 1800 saniye öneriliyor.
EVREN_TIMEOUT = int(os.getenv("EVREN_TIMEOUT", "1800"))

# ---------------- QDRANT ----------------
# EVREN Qdrant: REST + 443 + takım prefix'i
QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "https://evren-vektor.ssyz.org.tr",
).rstrip("/")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "443"))
EVREN_TEAM = os.getenv("EVREN_TEAM", "").strip()  # ör. team07
EVREN_QDRANT_KEY = os.getenv("EVREN_QDRANT_KEY", "").strip()

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "karonext_products",
).strip()

# bge-m3-embed dokümana göre 1024 boyutlu.
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))
QDRANT_TIMEOUT = int(os.getenv("QDRANT_TIMEOUT", "600"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# ---------------- DATA ----------------
INPUT_CSV = Path(os.getenv(
    "INPUT_CSV",
    str(BASE_DIR / "data/input/kaynak_469.csv")
))
PROCESSED_CSV = Path(os.getenv(
    "PROCESSED_CSV",
    str(BASE_DIR / "data/processed/finansal_veriler_yapilandirilmis.csv")
))
PROCESSED_JSONL = Path(os.getenv(
    "PROCESSED_JSONL",
    str(BASE_DIR / "data/processed/extracted_records.jsonl")
))
ERROR_JSONL = Path(os.getenv(
    "ERROR_JSONL",
    str(BASE_DIR / "data/processed/errors.jsonl")
))

def require_evren() -> None:
    if not EVREN_API_KEY:
        raise RuntimeError(
            "EVREN_API_KEY tanımlı değil. .env dosyasına takım anahtarını ekleyin."
        )

def require_qdrant() -> None:
    missing = []
    if not EVREN_TEAM:
        missing.append("EVREN_TEAM")
    if not EVREN_QDRANT_KEY:
        missing.append("EVREN_QDRANT_KEY")
    if missing:
        raise RuntimeError(
            ".env içinde eksik Qdrant ayarları: " + ", ".join(missing)
        )
