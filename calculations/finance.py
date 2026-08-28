"""Finansal hesaplama motoru — SAF fonksiyonlar (I/O yok, LLM yok, deterministik).

Yöntem: Murabaha eşit taksitli (anüite) ödeme planı.
Ayrıntılı formül ve varsayımlar: docs/FORMULAS.md
Şartname madde 14-21, KURAL 5 (formül uydurma yasak) — kullanılan formül açıkça
dokümante edilmiştir ve sonuç "TAHMİNİ" olarak etiketlenir.
"""

from __future__ import annotations

from calculations.schemas import CalculateRequest, CalculateResponse, TaksitSatiri


def yillik_to_aylik(r_yillik_yuzde: float) -> float:
    """Yıllık % oranı aylık % orana çevirir (bankaların standart basit bölme uygulaması)."""
    return r_yillik_yuzde / 12.0


def _aylik_oran_ondalik(req: CalculateRequest) -> float:
    yuzde = req.kar_payi_orani
    if req.oran_periyodu == "yillik":
        yuzde = yillik_to_aylik(yuzde)
    return yuzde / 100.0


def aylik_taksit(P: float, n: int, r_aylik: float) -> float:
    """Eşit taksit (anüite) tutarı.

    r > 0 :  A = P * r * (1+r)^n / ((1+r)^n - 1)
    r = 0 :  A = P / n
    """
    if P <= 0:
        raise ValueError("Finansman tutarı 0'dan büyük olmalı.")
    if n < 1:
        raise ValueError("Vade en az 1 ay olmalı.")
    if r_aylik < 0:
        raise ValueError("Kâr payı oranı negatif olamaz.")
    if r_aylik == 0:
        return P / n
    faktor = (1 + r_aylik) ** n
    return P * r_aylik * faktor / (faktor - 1)


def odeme_plani(P: float, n: int, r_aylik: float, taksit: float | None = None) -> list[TaksitSatiri]:
    """Ay ay kâr payı / anapara ayrışımı. Son taksit yuvarlama artığını massceder."""
    A = taksit if taksit is not None else aylik_taksit(P, n, r_aylik)
    plan: list[TaksitSatiri] = []
    kalan = P
    for t in range(1, n + 1):
        kar = kalan * r_aylik
        if t == n:
            anapara = kalan
            odeme = anapara + kar
        else:
            anapara = A - kar
            odeme = A
        kalan = kalan - anapara
        plan.append(
            TaksitSatiri(
                taksit_no=t,
                taksit_tutari=round(odeme, 2),
                kar_payi=round(kar, 2),
                anapara=round(anapara, 2),
                kalan_anapara=round(max(kalan, 0.0), 2),
            )
        )
    return plan


def _tahsis_ucreti(req: CalculateRequest) -> float:
    if req.tahsis_ucreti_tl:
        return float(req.tahsis_ucreti_tl)
    if req.tahsis_ucreti_orani:
        return req.finansman_tutari * req.tahsis_ucreti_orani / 100.0
    return 0.0


def hesapla(req: CalculateRequest) -> CalculateResponse:
    P = req.finansman_tutari
    n = req.vade_ay
    r = _aylik_oran_ondalik(req)

    A = aylik_taksit(P, n, r)
    toplam_odeme = A * n
    toplam_kar_payi = toplam_odeme - P
    tahsis = _tahsis_ucreti(req)

    plan = odeme_plani(P, n, r, taksit=A) if req.odeme_plani_dahil_et else None

    return CalculateResponse(
        girdiler={
            "finansman_tutari": P,
            "vade_ay": n,
            "kar_payi_orani": req.kar_payi_orani,
            "oran_periyodu": req.oran_periyodu,
            "aylik_kar_payi_orani_yuzde": round(r * 100, 4),
            "tahsis_ucreti_tl": round(tahsis, 2),
            "kaynak_record_id": req.kaynak_record_id,
        },
        aylik_odeme=round(A, 2),
        toplam_odeme=round(toplam_odeme, 2),
        toplam_kar_payi=round(toplam_kar_payi, 2),
        tahsis_ucreti_tl=round(tahsis, 2),
        toplam_maliyet=round(toplam_odeme + tahsis, 2),
        efektif_aylik_oran=round(r * 100, 4),
        odeme_plani=plan,
    )
