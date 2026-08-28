from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import api_router
from core.errors import register_error_handlers
from core.logging import logger, setup_logging
from core.settings import settings

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "KARONEXT API başladı — LLM=%s, koleksiyon=%s, CORS=%s",
        settings.llm_model,
        settings.qdrant_collection,
        settings.cors_origin_list,
    )
    yield


app = FastAPI(
    title="KARONEXT — Katılım Bankacılığı Platformu API",
    version="2.0.0",
    description="Finansman • Kampanya • Karşılaştırma • Hesaplama • Yapay Zekâ Asistanı",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def kok():
    return {"servis": "KARONEXT API", "dokuman": "/docs", "surum": app.version}


# ---------------------------------------------------------------------------
# Eski uçlar (/extract, /search, /compare, /chat) — Aşama 5-7'de /api/v1 altına
# taşınacak ve LangChain ile yeniden yazılacak. Geçiş döneminde korunur.
# ---------------------------------------------------------------------------
try:
    from api.models import ChatRequest, CompareRequest, ExtractRequest, SearchRequest
    from services.pipeline import (
        chat_pipeline,
        compare_pipeline,
        extract_pipeline,
        search_pipeline,
    )
    from fastapi import HTTPException

    @app.post("/extract", tags=["eski"], include_in_schema=False)
    def _extract(req: ExtractRequest):
        try:
            return extract_pipeline(
                {
                    "banka": req.banka or "",
                    "baslik": req.baslik or "",
                    "metin": req.metin,
                    "url": req.url or "",
                    "banka_id": "",
                    "kaynak": "api",
                }
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail="Çıkarım servisi yanıt vermedi.") from exc

    @app.post("/search", tags=["eski"], include_in_schema=False)
    def _search(req: SearchRequest):
        try:
            return {"results": search_pipeline(query=req.query, top_k=req.top_k, bankalar=req.bankalar)}
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail="Arama servisi yanıt vermedi.") from exc

    @app.post("/compare", tags=["eski"], include_in_schema=False)
    def _compare(req: CompareRequest):
        try:
            return compare_pipeline(query=req.query, top_k=req.top_k, bankalar=req.bankalar)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail="Karşılaştırma servisi yanıt vermedi.") from exc

    @app.post("/chat", tags=["eski"], include_in_schema=False)
    def _chat(req: ChatRequest):
        try:
            return chat_pipeline(query=req.query, top_k=req.top_k, bankalar=req.bankalar)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail="Asistan servisi yanıt vermedi.") from exc

except Exception as exc:  # noqa: BLE001
    logger.warning("Eski uçlar yüklenemedi (Aşama 5-7'de yenilenecek): %s", exc)
