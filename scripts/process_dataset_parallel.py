"""process_dataset.py'nin paralel sürümü — aynı çıktı formatı, çoklu iş parçacığıyla.

    python scripts/process_dataset_parallel.py --workers 12
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

import config
from nlp.processor import process_record, build_record_id

WRITE_LOCK = threading.Lock()
PROGRESS_LOCK = threading.Lock()
_done_count = 0
_fail_count = 0


def handle_row(idx: int, row_dict: dict, total: int) -> None:
    global _done_count, _fail_count

    rid = build_record_id(
        str(row_dict.get("banka", "")),
        str(row_dict.get("baslik", "")),
        str(row_dict.get("url", "")),
        str(row_dict.get("metin", "")),
    )

    try:
        result = process_record(row_dict)
        with WRITE_LOCK:
            with config.PROCESSED_JSONL.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        with PROGRESS_LOCK:
            _done_count += 1
            print(f"[OK] {_done_count+_fail_count}/{total} {result.get('banka')} | {result.get('kampanya_turu')}")
    except Exception as exc:
        error_record = {
            "record_id": rid,
            "index": int(idx),
            "banka": row_dict.get("banka", ""),
            "baslik": row_dict.get("baslik", ""),
            "url": row_dict.get("url", ""),
            "error": str(exc),
        }
        with WRITE_LOCK:
            with config.ERROR_JSONL.open("a", encoding="utf-8") as f:
                f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
        with PROGRESS_LOCK:
            _fail_count += 1
            print(f"[HATA] {_done_count+_fail_count}/{total} -> {exc}")


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--resume", action="store_true", help="Mevcut PROCESSED_JSONL'deki kayıtları atla, sadece eksikleri işle.")
    args = parser.parse_args()

    if not config.INPUT_CSV.exists():
        raise FileNotFoundError(f"Girdi CSV yok: {config.INPUT_CSV}")

    df = pd.read_csv(config.INPUT_CSV).fillna("")
    if args.limit > 0:
        df = df.head(args.limit)

    config.PROCESSED_JSONL.parent.mkdir(parents=True, exist_ok=True)

    done = load_done_ids(config.PROCESSED_JSONL) if args.resume else set()
    if done:
        print(f"Devam modu: {len(done)} kayıt zaten tamam, atlanıyor.")

    rows = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        if done:
            rid = build_record_id(
                str(row_dict.get("banka", "")),
                str(row_dict.get("baslik", "")),
                str(row_dict.get("url", "")),
                str(row_dict.get("metin", "")),
            )
            if rid in done:
                continue
        rows.append((idx, row_dict))

    total = len(rows)
    print("Toplam hedef:", total, "| workers:", args.workers)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(handle_row, idx, row_dict, total) for idx, row_dict in rows]
        for _ in as_completed(futures):
            pass

    print("\nBitti.")
    print("Basarili:", _done_count)
    print("Hatali:", _fail_count)


if __name__ == "__main__":
    main()
