"""Chatbot iç modelleri (LLM yapılandırılmış çıktıları)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Niyet = Literal["bilgi", "karsilastirma", "hesaplama"]


class SoruAnalizi(BaseModel):
    """Kullanıcı sorusundan çıkarılan parametreler."""

    niyet: Niyet = Field(description="bilgi | karsilastirma | hesaplama")
    arama_metni: str = Field(description="Vektör araması için sadeleştirilmiş sorgu")
    bankalar: list[str] = Field(default_factory=list, description="Soruda geçen banka adları")
    urun_ailesi: Literal["finansman", "mevduat", "kart", "yatirim", "diger", ""] = ""
    finansman_tutari: float | None = None
    vade_ay: int | None = None
    kar_payi_orani: float | None = None
    oran_periyodu: Literal["aylik", "yillik", ""] = ""


class ChatYaniti(BaseModel):
    """LLM'in ürettiği nihai yanıt (guardrail'den geçmeden önce)."""

    yanit: str
    kullanilan_record_idler: list[str] = Field(default_factory=list)
    uyari: str | None = None
