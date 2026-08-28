"""Chunk'ları EVREN Qdrant'a indeksler (chunk-başına bir vektör).

    python scripts/03_index.py --recreate     # koleksiyonu sıfırla
    python scripts/03_index.py --limit 50      # hızlı deneme

Kaynak: data/processed/chunks/chunks_*.jsonl  (scripts/chunk_dataset.py çıktısı)
Metadata SQLite'tan zenginleştirilir (urun_ailesi, aktif_mi).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_core.documents import Document

from core.settings import settings
from data_layer import repository as repo
from rag.vectorstore import ensure_collection, get_vectorstore

CHUNK_DIR = Path(__file__).resolve().parent.parent / "data" / "processed" / "chunks"


def _chunk_dosyalari() -> list[Path]:
    return sorted(CHUNK_DIR.glob("chunks_*.jsonl"))


def _kayit_indeksi() -> dict[str, dict]:
    return {r["record_id"]: r for r in repo.all_records(tum_aileler=True)}


def build_documents(limit: int = 0) -> list[Document]:
    kayitlar = _kayit_indeksi()
    docs: list[Document] = []
    for dosya in _chunk_dosyalari():
        for line in dosya.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            c = json.loads(line)
            rid = c.get("record_id")
            kayit = kayitlar.get(rid, {})
            docs.append(
                Document(
                    page_content=c["text"],
                    metadata={
                        "chunk_id": c.get("chunk_id"),
                        "record_id": rid,
                        "banka": kayit.get("banka") or c.get("banka"),
                        "urun_ailesi": kayit.get("urun_ailesi", "diger"),
                        "kampanya_turu": kayit.get("kampanya_turu") or c.get("kampanya_turu"),
                        "aktif_mi": bool(kayit.get("aktif_mi", True)),
                        "url": kayit.get("url") or c.get("url"),
                    },
                )
            )
            if limit and len(docs) >= limit:
                return docs
    return docs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recreate", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--batch", type=int, default=48)
    args = parser.parse_args()

    if not repo.veritabani_var_mi():
        print("Önce scripts/02_build_db.py çalıştırın.", file=sys.stderr)
        return 1

    docs = build_documents(args.limit)
    print(f"İndekslenecek chunk: {len(docs)}  (koleksiyon: {settings.qdrant_collection})")

    ensure_collection(recreate=args.recreate)
    vs = get_vectorstore()

    toplam = len(docs)
    for i in range(0, toplam, args.batch):
        parca = docs[i : i + args.batch]
        vs.add_documents(parca)
        print(f"  {min(i + args.batch, toplam)}/{toplam}")

    from rag.qdrant_client import get_qdrant_client

    sayim = get_qdrant_client().count(settings.qdrant_collection).count
    print(f"Tamamlandı. Qdrant'taki nokta sayısı: {sayim}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
