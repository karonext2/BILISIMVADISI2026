from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from banks_config import BANKALAR, ANAHTAR_KELIMELER
from utils import linkleri_topla, sayfa_metni_cek

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw_kampanyalar.csv"

def fingerprint(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()

def main():
    rows = []
    seen = set()

    print(f"Toplam banka: {len(BANKALAR)}")

    for bank_key, bank in BANKALAR.items():
        print("\n" + "=" * 60)
        print(f"Banka: {bank['ad']}")
        print(f"Site : {bank['base_url']}")

        links = linkleri_topla(
            bank["base_url"],
            ANAHTAR_KELIMELER
        )

        print(f"Aday link sayısı: {len(links)}")

        basarili = 0

        for i, url in enumerate(links, start=1):
            print(f"[{i}/{len(links)}] {url}")

            result = sayfa_metni_cek(url)
            if not result:
                continue

            title, text = result
            fp = fingerprint(text)

            if fp in seen:
                print("  -> duplicate, atlandı")
                continue

            seen.add(fp)

            rows.append({
                "banka": bank["ad"],
                "banka_id": bank_key,
                "baslik": title,
                "metin": text,
                "url": url,
            })

            basarili += 1

        print(f"{bank['ad']} için kaydedilen sayfa: {basarili}")

    with OUT.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "banka",
                "banka_id",
                "baslik",
                "metin",
                "url",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 60)
    print(f"Toplam kaydedilen sayfa: {len(rows)}")
    print(f"CSV oluşturuldu: {OUT}")
    print("=" * 60)

if __name__ == "__main__":
    main()