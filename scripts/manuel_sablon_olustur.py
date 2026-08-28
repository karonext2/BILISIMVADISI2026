"""data/input/manuel_veri.csv şablonunu üretir — eksik verili kayıtlarla ön-doldurulmuş.

Excel'de aç, boş kolonları doldur, kaydet, sonra:  python scripts/02_build_db.py

    python scripts/manuel_sablon_olustur.py                # sadece gerçek ürün/kampanyalar
    python scripts/manuel_sablon_olustur.py --tumu         # finansal alanı boş her kayıt
    python scripts/manuel_sablon_olustur.py --uzerine-yaz  # mevcut CSV'yi ez
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_layer import repository as repo
from data_layer.manuel import ALANLAR, LISTE_ALANLARI

CIKTI = Path(__file__).resolve().parent.parent / "data" / "input" / "manuel_veri.csv"

# Yalnızca menü/kurumsal olmayan kayıtları öner
_DOKUMAN = re.compile(
    r"icazet|bilgilendirme formu|müşteri bilgilendirme|misyon|vizyon|sözleşme|"
    r"akdi|akit|belgesi|ortaklık|yatırımcı ilişkil|swift|kvkk|çerez|aydınlatma|"
    r"güvenlik|şube|atm listesi|iletişim",
    re.I,
)
_SAYI = re.compile(r"%\s?\d|\d[\d.]*\s?(?:tl|₺)\b|\d+\s?(?:ay|yıl)\b|\d{2}\.\d{2}\.\d{4}", re.I)


def eksik_mi(r: dict) -> bool:
    return not (
        r.get("kar_payi_orani_raw") or r.get("vade_raw") or r.get("finansman_tutari_raw")
        or r.get("odul_miktari_raw") or r.get("alisveris_puani_raw") or r.get("indirim_orani_raw")
        or r.get("tahsis_ucreti_raw") or r.get("kampanya_bitis_iso")
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tumu", action="store_true")
    ap.add_argument("--uzerine-yaz", action="store_true")
    args = ap.parse_args()

    if CIKTI.exists() and not args.uzerine_yaz:
        print(f"{CIKTI.name} zaten var. Üzerine yazmak için --uzerine-yaz kullanın.")
        return 1

    if not repo.veritabani_var_mi():
        print("Önce: python scripts/02_build_db.py", file=sys.stderr)
        return 1

    kayitlar = repo.all_records()
    hedef = []
    for r in kayitlar:
        if not eksik_mi(r):
            continue
        blob = f"{r.get('urun_adi') or ''} {r.get('baslik') or ''}"
        if not args.tumu:
            if _DOKUMAN.search(blob) or not _SAYI.search(r.get("metin") or ""):
                continue
        hedef.append(r)

    kolonlar = ["banka", "urun_adi_veya_baslik", *ALANLAR, *LISTE_ALANLARI, "_kaynak_url", "_metin_ozeti"]
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    with CIKTI.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kolonlar)
        w.writeheader()
        for r in hedef:
            metin = re.sub(r"\s+", " ", r.get("metin") or "")[:300]
            w.writerow({
                "banka": r.get("banka"),
                "urun_adi_veya_baslik": r.get("urun_adi") or r.get("baslik"),
                "_kaynak_url": r.get("url") or "",
                "_metin_ozeti": metin,
            })

    print(f"{CIKTI}  ({len(hedef)} satır)")
    print("Excel'de aç, boş kolonları doldur (boş bırakılan alana dokunulmaz),")
    print("kaydet, sonra: python scripts/02_build_db.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
