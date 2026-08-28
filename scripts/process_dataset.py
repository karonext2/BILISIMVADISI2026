from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

import config
from nlp.processor import process_record, build_record_id

def load_done_ids(path: Path) -> set[str]:
    done = set()
    if not path.exists():
        return done

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                if item.get("record_id"):
                    done.add(item["record_id"])
            except json.JSONDecodeError:
                pass
    return done

def rebuild_csv(jsonl_path: Path, csv_path: Path) -> int:
    rows = []
    if jsonl_path.exists():
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))

    if not rows:
        return 0

    # List/dict alanları CSV'de JSON string olarak sakla.
    normalized = []
    for row in rows:
        out = {}
        for key, value in row.items():
            if isinstance(value, (list, dict)):
                out[key] = json.dumps(value, ensure_ascii=False)
            else:
                out[key] = value
        normalized.append(out)

    fieldnames = sorted({k for row in normalized for k in row.keys()})
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized)

    return len(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="İlk test için 3 veya 5 verilebilir. 0 = tüm veri.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Çağrılar arasında bekleme (saniye).",
    )
    args = parser.parse_args()

    if not config.INPUT_CSV.exists():
        raise FileNotFoundError(f"Girdi CSV yok: {config.INPUT_CSV}")

    df = pd.read_csv(config.INPUT_CSV).fillna("")
    if args.limit > 0:
        df = df.head(args.limit)

    config.PROCESSED_JSONL.parent.mkdir(parents=True, exist_ok=True)
    done = load_done_ids(config.PROCESSED_JSONL)

    print("Toplam hedef:", len(df))
    print("Daha önce tamamlanan:", len(done))

    success = 0
    failed = 0

    for idx, row in df.iterrows():
        row_dict = row.to_dict()

        rid = build_record_id(
            str(row_dict.get("banka", "")),
            str(row_dict.get("baslik", "")),
            str(row_dict.get("url", "")),
            str(row_dict.get("metin", "")),
        )

        if rid in done:
            print(f"[SKIP] {idx+1}/{len(df)} {rid}")
            continue

        try:
            result = process_record(row_dict)

            with config.PROCESSED_JSONL.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

            done.add(result["record_id"])
            success += 1
            print(
                f"[OK] {idx+1}/{len(df)} "
                f"{result.get('banka')} | {result.get('kampanya_turu')}"
            )

        except Exception as exc:
            failed += 1
            error_record = {
                "record_id": rid,
                "index": int(idx),
                "banka": row_dict.get("banka", ""),
                "baslik": row_dict.get("baslik", ""),
                "url": row_dict.get("url", ""),
                "error": str(exc),
            }
            with config.ERROR_JSONL.open("a", encoding="utf-8") as f:
                f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
            print(f"[HATA] {idx+1}/{len(df)} -> {exc}")

        if args.sleep > 0:
            time.sleep(args.sleep)

    total_written = rebuild_csv(
        config.PROCESSED_JSONL,
        config.PROCESSED_CSV,
    )

    print("\nBitti.")
    print("Bu çalışmada başarılı:", success)
    print("Bu çalışmada hatalı:", failed)
    print("Toplam işlenmiş kayıt:", total_written)
    print("CSV:", config.PROCESSED_CSV)

if __name__ == "__main__":
    main()
