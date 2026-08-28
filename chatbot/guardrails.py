"""Yanıt güvenlik süzgeçleri — halüsinasyon ve terim kontrolü."""

from __future__ import annotations

import re

_TEKNIK_TERIMLER = re.compile(
    r"\b(embedding|vekt[öo]r|qdrant|\brag\b|\bnlp\b|prompt|token|LLM|pipeline|"
    r"cosine|chunk)\b",
    re.IGNORECASE,
)

# "faiz" -> "kâr payı" ama "faizsiz" bozulmasın
_FAIZ = re.compile(r"\bfaiz(?!siz)(i|in|ler|li)?\b", re.IGNORECASE)

_SAYI_KALIP = re.compile(
    r"%\s?\d[\d.,]*|\d[\d.,]*\s?(?:tl|₺|lira)|\d+\s?(?:ay|yıl|yil)\b",
    re.IGNORECASE,
)


def terminoloji_duzelt(metin: str) -> str:
    return _FAIZ.sub("kâr payı", metin)


def teknik_terim_var_mi(metin: str) -> bool:
    return bool(_TEKNIK_TERIMLER.search(metin))


def teknik_terimleri_temizle(metin: str) -> str:
    return _TEKNIK_TERIMLER.sub("ilgili bilgi", metin)


def _normalize(s: str) -> str:
    return re.sub(r"[.,\s₺]", "", s.lower()).replace("tl", "").replace("lira", "")


def dogrulanmamis_sayilar(yanit: str, baglam: str, hesaplama_metni: str = "") -> list[str]:
    """Yanıttaki sayısal ifadelerden bağlamda (kayıtlar + hesaplama) bulunmayanları döndürür."""
    baglam_norm = _normalize(baglam + " " + hesaplama_metni)
    bulunamayan: list[str] = []
    for eslesme in _SAYI_KALIP.findall(yanit):
        if _normalize(eslesme) and _normalize(eslesme) not in baglam_norm:
            bulunamayan.append(eslesme.strip())
    return bulunamayan


def uygula(
    yanit: str,
    baglam: str,
    hesaplama_metni: str = "",
    mevcut_uyari: str | None = None,
) -> tuple[str, str | None]:
    """Yanıtı düzeltir, gerekli uyarıları ekler. (temiz_yanit, uyari) döner."""
    y = terminoloji_duzelt(yanit)

    if teknik_terim_var_mi(y):
        y = teknik_terimleri_temizle(y)

    uyarilar = [mevcut_uyari] if mevcut_uyari else []

    dogrulanmamis = dogrulanmamis_sayilar(y, baglam, hesaplama_metni)
    if dogrulanmamis:
        uyarilar.append(
            "Yanıttaki bazı sayısal değerler kaynaklarda birebir doğrulanamadı "
            "(" + ", ".join(dogrulanmamis[:5]) + "). Lütfen güncel bilgiyi bankadan teyit edin."
        )

    uyari = " ".join(u for u in uyarilar if u) or None
    return y, uyari
