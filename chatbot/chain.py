"""Katılım Bankacılığı Asistanı — LCEL tabanlı akış.

soru → analiz → getir (RAG) → [gerekiyorsa] hesapla / karşılaştır → yanıt →
guardrail → kaynak.

Dashboard bağlamı (aktif filtreler / seçili kayıtlar) `bankalar`, `urun_ailesi`,
`kayit_idleri` ile taşınır (şartname madde 34).
"""

from __future__ import annotations

from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage

from calculations.finance import hesapla as _hesapla
from calculations.schemas import CalculateRequest
from chatbot import guardrails
from chatbot.prompts import ANALIZ_SISTEM, YANIT_SISTEM
from chatbot.schemas import SoruAnalizi
from core.logging import logger
from data_layer import repository as repo
from llm.base import get_chat_model
from rag.retriever import retrieve
from services.comparison import compare

BOS_YANIT = (
    "Bu konuda elimdeki kaynaklarda yeterli bilgi bulamadım. Farklı bir şekilde "
    "sorabilir ya da banka/ürün adını belirtebilirsiniz."
)

_AILELER = ("finansman", "mevduat", "kart", "yatirim", "diger")

# "Bilgi bulunamadı" tarzı yanıtları tespit eder (kaynak listesini temizlemek için)
_RED_KALIPLARI = (
    "yer almıyor",
    "yer almamaktadır",
    "bulunmamaktadır",
    "bulunamadı",
    "bulamadım",
    "bilgi mevcut değil",
    "kaynaklarda yok",
    "elimdeki kaynaklarda yer almı",
)


def _reddi_mi(yanit: str) -> bool:
    y = yanit.casefold()
    return any(k in y for k in _RED_KALIPLARI)


@lru_cache(maxsize=1)
def _bilinen_bankalar() -> set[str]:
    try:
        return {b.casefold(): b for b in repo.filter_values()["bankalar"]}  # type: ignore
    except Exception:  # noqa: BLE001
        return {}


def _analiz_et(soru: str) -> SoruAnalizi:
    model = get_chat_model(max_tokens=400).with_structured_output(
        SoruAnalizi, method="json_schema"
    )
    try:
        return model.invoke(
            [SystemMessage(content=ANALIZ_SISTEM), HumanMessage(content=soru)]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Soru analizi başarısız, ham sorgu kullanılacak: %s", exc)
        return SoruAnalizi(niyet="bilgi", arama_metni=soru)


def _eslesen_bankalar(adlar: list[str]) -> list[str]:
    harita = _bilinen_bankalar()
    if not isinstance(harita, dict):
        return []
    bulunan = []
    for ad in adlar:
        for anahtar, gercek in harita.items():
            if ad.casefold() in anahtar or anahtar in ad.casefold():
                bulunan.append(gercek)
    return list(dict.fromkeys(bulunan))


def _kayit_blogu(k: dict) -> str:
    return (
        f"[{k['record_id']}] {k.get('banka')} — {k.get('urun_adi') or k.get('baslik')}\n"
        f"  ürün ailesi: {k.get('urun_ailesi')}, kampanya türü: {k.get('kampanya_turu')}\n"
        f"  kâr payı (ham): {k.get('kar_payi_orani_raw') or 'belirtilmemiş'} "
        f"({k.get('kar_payi_turu')})\n"
        f"  vade (ham): {k.get('vade_raw') or 'belirtilmemiş'}\n"
        f"  finansman tutarı (ham): {k.get('finansman_tutari_raw') or 'belirtilmemiş'}\n"
        f"  tahsis ücreti (ham): {k.get('tahsis_ucreti_raw') or 'belirtilmemiş'}\n"
        f"  masraf: {k.get('masraf_bilgisi') or 'belirtilmemiş'}\n"
        f"  ödül (ham): {k.get('odul_miktari_raw') or 'belirtilmemiş'}\n"
        f"  kampanya bitiş: {k.get('kampanya_bitis_tarihi') or 'belirtilmemiş'}\n"
        f"  avantajlar: {', '.join(k.get('avantajlar') or []) or 'belirtilmemiş'}\n"
        f"  koşullar: {', '.join(k.get('kampanya_kosullari') or []) or 'belirtilmemiş'}\n"
        f"  kaynak: {k.get('url') or k.get('kaynak') or 'belirtilmemiş'}"
    )


def _hesaplama_metni(h) -> str:
    if not h:
        return ""
    return (
        f"HESAPLAMA (TAHMİNİ): aylık ödeme {h.aylik_odeme:,.2f} TL, "
        f"toplam ödeme {h.toplam_odeme:,.2f} TL, toplam kâr payı {h.toplam_kar_payi:,.2f} TL. "
        f"Girdiler: {h.girdiler}"
    )


def _hesaplama_yap(analiz: SoruAnalizi, kayitlar: list[dict]) -> tuple[object | None, str | None]:
    tutar = analiz.finansman_tutari
    vade = analiz.vade_ay
    oran = analiz.kar_payi_orani
    periyot = analiz.oran_periyodu or "aylik"
    kaynak_id = None

    if oran is None:
        # Kullanıcı oran vermediyse, getirilen bir finansman kaydının oranını KULLAN
        # (uydurma değil — kaynağı belirtilecek). madde 30.
        for k in kayitlar:
            if k.get("urun_ailesi") == "finansman" and k.get("kar_payi_orani_min") is not None:
                oran = k["kar_payi_orani_min"]
                periyot = "aylik" if k.get("kar_payi_turu") == "aylik" else "yillik"
                kaynak_id = k["record_id"]
                break

    if tutar is None or vade is None or oran is None:
        return None, (
            "Hesaplama için finansman tutarı, vade ve kâr payı oranı gerekli. "
            "Eksik bilgileri belirtirseniz tahmini hesaplama yapabilirim."
        )

    try:
        sonuc = _hesapla(
            CalculateRequest(
                finansman_tutari=tutar,
                vade_ay=int(vade),
                kar_payi_orani=oran,
                oran_periyodu=periyot if periyot in ("aylik", "yillik") else "aylik",
                kaynak_record_id=kaynak_id,
            )
        )
        return sonuc, None
    except ValueError as exc:
        return None, str(exc)


def _cok_bankali_getir(
    sorgu: str, bankalar: list[str], aile: str | None, top_k: int
) -> list[dict]:
    """Karşılaştırma sorularında her banka için ayrı getirme yapıp birleştirir.

    Tek bir vektör aramasında baskın banka diğerlerini bastırabildiğinden
    (senaryo 7), banka başına en az birkaç kayıt garanti edilir.
    """
    banka_basi = max(2, top_k // max(1, len(bankalar)) + 1)
    birlesik: dict[str, dict] = {}
    for b in bankalar:
        for k in retrieve(
            sorgu,
            top_k=banka_basi,
            bankalar=[b],
            urun_ailesi=aile if aile in _AILELER else None,
        ):
            birlesik.setdefault(k["record_id"], k)
    return sorted(birlesik.values(), key=lambda k: k.get("_skor", 0.0), reverse=True)


def cevapla(
    soru: str,
    top_k: int = 5,
    bankalar: list[str] | None = None,
    urun_ailesi: str | None = None,
    kayit_idleri: list[str] | None = None,
) -> dict:
    analiz = _analiz_et(soru)

    aktif_bankalar = list(
        dict.fromkeys((bankalar or []) + _eslesen_bankalar(analiz.bankalar))
    )
    aile = urun_ailesi or (analiz.urun_ailesi or None)

    if kayit_idleri:
        kayitlar = repo.records_for_ids(kayit_idleri)
    elif analiz.niyet == "karsilastirma" and len(aktif_bankalar) >= 2:
        kayitlar = _cok_bankali_getir(
            analiz.arama_metni or soru, aktif_bankalar, aile, top_k
        )
    else:
        kayitlar = retrieve(
            analiz.arama_metni or soru,
            top_k=top_k,
            bankalar=aktif_bankalar or None,
            urun_ailesi=aile if aile in _AILELER else None,
        )

    hesaplama = None
    hesaplama_uyari = None
    if analiz.niyet == "hesaplama":
        hesaplama, hesaplama_uyari = _hesaplama_yap(analiz, kayitlar)

    if not kayitlar and hesaplama is None:
        return {
            "yanit": BOS_YANIT,
            "kaynaklar": [],
            "hesaplama": None,
            "karsilastirma": None,
            "uyari": hesaplama_uyari,
        }

    karsilastirma = None
    if analiz.niyet == "karsilastirma" and len(kayitlar) >= 2:
        karsilastirma = compare(kayitlar, urun_ailesi=aile)

    baglam_parcalari = [_kayit_blogu(k) for k in kayitlar]
    hesaplama_str = _hesaplama_metni(hesaplama)
    if hesaplama_str:
        baglam_parcalari.append(hesaplama_str)
    if karsilastirma:
        baglam_parcalari.append("KARŞILAŞTIRMA SONUCU: " + karsilastirma["neden"])
    baglam = "\n\n".join(baglam_parcalari)

    # Düz metin yanıt — strict JSON şema EVREN llm-fast'te uzun karşılaştırmalarda
    # completion bütçesini aşıp parse hatası veriyordu. Metin çok daha sağlam.
    model = get_chat_model(max_tokens=700)
    kullanici_mesaji = f"SORU:\n{soru}\n\nKAYITLAR:\n{baglam}"
    ham = model.invoke(
        [SystemMessage(content=YANIT_SISTEM), HumanMessage(content=kullanici_mesaji)]
    ).content
    yanit_metni = "".join(str(p) for p in ham) if isinstance(ham, list) else str(ham)

    kayit_blob = "\n".join(baglam_parcalari)
    temiz_yanit, uyari = guardrails.uygula(
        yanit_metni,
        baglam=kayit_blob,
        hesaplama_metni=hesaplama_str,
        mevcut_uyari=hesaplama_uyari,
    )

    gecerli = {k["record_id"]: k for k in kayitlar}
    if _reddi_mi(temiz_yanit) and hesaplama is None:
        # "Bilgi bulunamadı" yanıtında alakasız kaynak kartı gösterme
        kullanilan: list[str] = []
    elif analiz.niyet == "karsilastirma":
        # Karşılaştırmada tüm getirilen kayıtları kaynak göster (her iki banka da)
        kullanilan = list(gecerli.keys())
    else:
        # Yanıt metninde adı/ürünü geçen kayıtları kaynak göster; hiçbiri yoksa hepsi
        y_cf = temiz_yanit.casefold()
        kullanilan = [
            rid for rid, k in gecerli.items()
            if (k.get("banka") or "").casefold() in y_cf
            or ((k.get("urun_adi") or "").casefold() in y_cf and len(k.get("urun_adi") or "") > 4)
        ]
        if not kullanilan:
            kullanilan = list(gecerli.keys())

    kaynaklar = [
        {
            "record_id": rid,
            "banka": gecerli[rid].get("banka"),
            "urun_adi": gecerli[rid].get("urun_adi") or gecerli[rid].get("baslik"),
            "url": gecerli[rid].get("url"),
            "veri_tarihi": gecerli[rid].get("veri_tarihi"),
        }
        for rid in kullanilan
        if rid in gecerli
    ]

    return {
        "yanit": temiz_yanit,
        "kaynaklar": kaynaklar,
        "hesaplama": hesaplama.model_dump() if hesaplama else None,
        "karsilastirma": karsilastirma,
        "uyari": uyari,
    }
