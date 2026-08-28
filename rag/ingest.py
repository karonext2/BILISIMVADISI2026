from __future__ import annotations
import uuid

import math
import pandas as pd
from qdrant_client.models import PointStruct

import config
from rag.embedding import embed_texts
from rag.qdrant_client import ensure_collection, get_qdrant_client

BATCH_SIZE = 24

def _safe(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value

def build_embedding_text(row: dict) -> str:
    parts = [
        f"Banka: {row.get('banka', '')}",
        f"Ürün: {row.get('urun_adi') or row.get('baslik', '')}",
        f"Kampanya türü: {row.get('kampanya_turu', '')}",
        f"Başlık: {row.get('baslik', '')}",
        f"Metin: {row.get('metin', '')}",
    ]
    return "\n".join(parts)

def ingest_processed_csv(recreate: bool = False) -> int:
    if not config.PROCESSED_CSV.exists():
        raise FileNotFoundError(
            f"İşlenmiş CSV bulunamadı: {config.PROCESSED_CSV}"
        )

    df = pd.read_csv(config.PROCESSED_CSV).fillna("")
    if df.empty:
        raise ValueError("İşlenmiş CSV boş.")

    ensure_collection(recreate=recreate)
    client = get_qdrant_client()

    total = len(df)
    for start in range(0, total, BATCH_SIZE):
        batch = df.iloc[start:start+BATCH_SIZE].to_dict(orient="records")
        texts = [build_embedding_text(r) for r in batch]
        vectors = embed_texts(texts)

        points = []
        for row, vector in zip(batch, vectors):
            payload = {k: _safe(v) for k, v in row.items()}

            points.append(
                PointStruct(
                    id=str(
                        uuid.uuid5(
                            uuid.NAMESPACE_URL,
                            str(row["record_id"])
                        )
                    ),
                    vector=vector,
                    payload=payload,
                )
            )

        client.upsert(
            collection_name=config.QDRANT_COLLECTION,
            points=points,
            wait=True,
        )
        print(f"Qdrant: {min(start+BATCH_SIZE, total)}/{total}")

    return total
