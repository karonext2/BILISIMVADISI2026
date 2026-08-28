"""Finansal hesaplama motoru ucu — POST /api/v1/calculate.

Elle giriş kabul eder; opsiyonel `kaynak_record_id` yalnızca izleme amaçlıdır
(gerçek değerler her zaman istek gövdesinden gelir — şartname madde 16, KURAL 11).
"""

from __future__ import annotations

from fastapi import APIRouter

from calculations.finance import hesapla
from calculations.schemas import CalculateRequest, CalculateResponse
from core.errors import GecersizIstek

router = APIRouter()


@router.post("/calculate", response_model=CalculateResponse)
def calculate(req: CalculateRequest):
    try:
        return hesapla(req)
    except ValueError as exc:
        raise GecersizIstek(str(exc), kullanici_mesaji=str(exc)) from exc
