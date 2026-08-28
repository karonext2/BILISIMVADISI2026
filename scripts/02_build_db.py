"""extracted_records.jsonl  ->  data/final/karonext.sqlite  (TEK DOĞRU KAYNAK)

- Ham *_raw alanları DÜZELTİLMİŞ normalizer'dan geçirir (LLM çağrısı YOK).
- Kanonik türetilmiş alanları üretir (urun_ailesi, kar_payi_turu, aktif_mi, *_min/max).
- Her kaydı Pydantic `Record` ile doğrular; geçmeyenler errors_build.jsonl'a yazılır.

    python scripts/02_build_db.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from data_layer.db import DB_PATH, get_connection, init_schema, record_to_row
from data_layer.derive import (
    aktif_mi,
    finansman_orani_duzelt,
    kar_payi_turu,
    parse_tr_date,
    urun_ailesi,
)
from data_layer.katalog import enrich as katalog_enrich
from data_layer.manuel import enrich as manuel_enrich
from nlp.normalizer import normalize_extraction
from schemas.record import Record

SRC = config.PROCESSED_JSONL
ERR = Path(__file__).resolve().parent.parent / "data" / "processed" / "errors_build.jsonl"


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except json.JSONDecodeError:
                pass
        return [s] if s else []
    return []


def _str(v) -> str | None:
    """*_raw alanları her zaman metin olmalı (LLM bazen sayı döndürüyor)."""
    if v is None or v == "":
        return None
    return str(v).strip() or None


def build_record(raw: dict) -> Record:
    # Küratörlü karşılaştırma tablosuyla BOŞ finansal alanları doldur (LLM'siz).
    raw = dict(raw)
    raw["avantajlar"] = _as_list(raw.get("avantajlar"))
    for _a in (
        "kar_payi_orani_raw", "vade_raw", "finansman_tutari_raw", "tahsis_ucreti_raw",
        "odul_miktari_raw", "alisveris_puani_raw", "indirim_orani_raw", "masraf_bilgisi",
    ):
        raw[_a] = _str(raw.get(_a))
    katalog_enrich(raw)  # küratörlü tablo: BOŞ finansal alanları doldur
    manuel_enrich(raw)   # data/input/manuel_veri.csv: elle girilen değerleri uygula (EZER)

    norm = normalize_extraction(raw)

    kp_turu = kar_payi_turu(raw.get("kar_payi_orani_raw"))
    bitis_iso = parse_tr_date(raw.get("kampanya_bitis_tarihi"))

    payload = {
        "record_id": raw["record_id"],
        "banka": (raw.get("banka") or "").strip() or "Bilinmiyor",
        "banka_id": (raw.get("banka_id") or "").strip(),
        "urun_adi": (raw.get("urun_adi") or None),
        "baslik": (raw.get("baslik") or "").strip(),
        "kampanya_turu": raw.get("kampanya_turu") or "Kampanya Değil",
        "urun_kategorisi": raw.get("urun_kategorisi"),
        "kuratorlu": bool(raw.get("kuratorlu")),
        "kar_payi_orani_min": norm.get("kar_payi_orani_min"),
        "kar_payi_orani_max": norm.get("kar_payi_orani_max"),
        "kar_payi_turu": kp_turu,
        "kar_payi_orani_raw": raw.get("kar_payi_orani_raw"),
        "finansman_orani": finansman_orani_duzelt(
            norm.get("finansman_orani"), raw.get("finansman_tutari_raw")
        ),
        "finansman_tutari_min": norm.get("finansman_tutari_min"),
        "finansman_tutari_max": norm.get("finansman_tutari_max"),
        "finansman_tutari_raw": raw.get("finansman_tutari_raw"),
        "vade_min_ay": norm.get("vade_min_ay"),
        "vade_max_ay": norm.get("vade_max_ay"),
        "vade_raw": raw.get("vade_raw"),
        "taksit_sayisi": norm.get("taksit_sayisi"),
        "tahsis_ucreti_tl": norm.get("tahsis_ucreti_tl"),
        "tahsis_ucreti_orani": norm.get("tahsis_ucreti_orani"),
        "tahsis_ucreti_raw": raw.get("tahsis_ucreti_raw"),
        "masraf_bilgisi": raw.get("masraf_bilgisi"),
        "odul_miktari_tl": norm.get("odul_miktari_tl"),
        "odul_miktari_raw": raw.get("odul_miktari_raw"),
        "alisveris_puani": norm.get("alisveris_puani"),
        "alisveris_puani_raw": raw.get("alisveris_puani_raw"),
        "indirim_orani": norm.get("indirim_orani"),
        "indirim_orani_raw": raw.get("indirim_orani_raw"),
        "kampanya_baslangic_tarihi": raw.get("kampanya_baslangic_tarihi"),
        "kampanya_bitis_tarihi": raw.get("kampanya_bitis_tarihi"),
        "kampanya_bitis_iso": bitis_iso,
        "aktif_mi": aktif_mi(bitis_iso),
        "hedef_kitle": _as_list(raw.get("hedef_kitle")),
        "kampanya_kosullari": _as_list(raw.get("kampanya_kosullari")),
        "avantajlar": _as_list(raw.get("avantajlar")),
        "url": (raw.get("url") or None),
        "kaynak": (raw.get("kaynak") or None),
        "metin": (raw.get("metin") or "").strip(),
    }
    # Katalog eşleşmesi ürün ailesini belirlediyse onu kullan (regex'ten güvenilir)
    if raw.get("urun_ailesi"):
        payload["urun_ailesi"] = raw["urun_ailesi"]
    else:
        payload["urun_ailesi"] = urun_ailesi(payload, kp_turu)
    return Record.model_validate(payload)


def main() -> int:
    if not SRC.exists():
        print(f"Kaynak yok: {SRC}", file=sys.stderr)
        return 1

    raw_rows = [json.loads(line) for line in SRC.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Okunan ham kayıt: {len(raw_rows)}")

    records: list[Record] = []
    errors: list[dict] = []
    for raw in raw_rows:
        try:
            records.append(build_record(raw))
        except Exception as exc:  # noqa: BLE001
            errors.append({"record_id": raw.get("record_id"), "hata": f"{type(exc).__name__}: {exc}"})

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = get_connection()
    init_schema(conn)

    cols = list(Record.model_fields.keys())
    placeholders = ", ".join([f":{c}" for c in cols])
    conn.executemany(
        f"INSERT INTO records ({', '.join(cols)}) VALUES ({placeholders})",
        [record_to_row(r.model_dump()) for r in records],
    )
    conn.commit()

    ERR.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in errors) + ("\n" if errors else ""),
        encoding="utf-8",
    )

    (n,) = conn.execute("SELECT COUNT(*) FROM records").fetchone()
    aile = conn.execute(
        "SELECT urun_ailesi, COUNT(*) FROM records GROUP BY urun_ailesi ORDER BY 2 DESC"
    ).fetchall()
    aktif = conn.execute("SELECT COUNT(*) FROM records WHERE aktif_mi=1").fetchone()[0]
    kp = conn.execute("SELECT COUNT(*) FROM records WHERE kar_payi_orani_min IS NOT NULL").fetchone()[0]
    conn.close()

    print(f"SQLite'a yazılan kayıt : {n}")
    print(f"Doğrulama hatası       : {len(errors)}  ({ERR.name})")
    print(f"Aktif kampanya         : {aktif}")
    print(f"Kâr payı oranı olan     : {kp}")
    print("Ürün ailesi dağılımı   :", {r[0]: r[1] for r in aile})
    print(f"Veritabanı             : {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
