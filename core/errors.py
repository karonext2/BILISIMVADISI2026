"""Alan (domain) hataları + FastAPI global hata yakalayıcıları.

Şartname: kullanıcı teknik hata / stack / model adı / Qdrant URL görmemeli.
Kullanıcıya sabit Türkçe mesaj + error_id döner; ayrıntı yalnızca log'a gider.
"""

from __future__ import annotations

import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.logging import logger


class KaronextError(Exception):
    """Tüm alan hatalarının atası."""

    status_code = 500
    kullanici_mesaji = "Beklenmeyen bir sorun oluştu. Lütfen daha sonra tekrar deneyin."

    def __init__(self, mesaj: str | None = None, kullanici_mesaji: str | None = None):
        super().__init__(mesaj or self.kullanici_mesaji)
        if kullanici_mesaji:
            self.kullanici_mesaji = kullanici_mesaji


class VeriBulunamadi(KaronextError):
    status_code = 404
    kullanici_mesaji = "Aradığınız kayıt bulunamadı."


class GecersizIstek(KaronextError):
    status_code = 400
    kullanici_mesaji = "Girdiğiniz bilgilerde bir sorun var. Lütfen kontrol edip tekrar deneyin."


class VeriKatmaniHatasi(KaronextError):
    status_code = 503
    kullanici_mesaji = "Veriler şu anda hazır değil. Lütfen kısa süre sonra tekrar deneyin."


class UpstreamHatasi(KaronextError):
    """EVREN / Qdrant gibi yukarı akış servisi hatası."""

    status_code = 502
    kullanici_mesaji = "Yapay zekâ servisi şu anda yanıt veremiyor. Lütfen biraz sonra tekrar deneyin."


def _zarf(mesaj: str, error_id: str) -> dict:
    return {"hata": True, "mesaj": mesaj, "error_id": error_id}


def register_error_handlers(app) -> None:
    @app.exception_handler(KaronextError)
    async def _karonext(request: Request, exc: KaronextError):
        eid = uuid.uuid4().hex[:12]
        logger.warning("[%s] %s %s -> %s: %s", eid, request.method, request.url.path,
                       type(exc).__name__, exc)
        return JSONResponse(status_code=exc.status_code,
                            content=_zarf(exc.kullanici_mesaji, eid))

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        eid = uuid.uuid4().hex[:12]
        logger.info("[%s] doğrulama hatası %s: %s", eid, request.url.path, exc.errors())
        return JSONResponse(
            status_code=422,
            content=_zarf("Gönderilen bilgiler geçersiz. Lütfen alanları kontrol edin.", eid),
        )

    @app.exception_handler(Exception)
    async def _beklenmeyen(request: Request, exc: Exception):
        eid = uuid.uuid4().hex[:12]
        logger.exception("[%s] beklenmeyen hata %s %s", eid, request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=_zarf("Beklenmeyen bir sorun oluştu. Lütfen daha sonra tekrar deneyin.", eid),
        )
