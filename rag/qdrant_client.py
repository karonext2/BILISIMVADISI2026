from __future__ import annotations

from functools import lru_cache
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

import config

@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    config.require_qdrant()
    return QdrantClient(
        url=config.QDRANT_URL,
        port=config.QDRANT_PORT,
        prefix=config.EVREN_TEAM,
        api_key=config.EVREN_QDRANT_KEY,
        timeout=config.QDRANT_TIMEOUT,
        # EVREN dokümantasyonuna göre gRPC kullanılmamalı.
        prefer_grpc=False,
    )

def ensure_collection(recreate: bool = False) -> None:
    client = get_qdrant_client()

    exists = client.collection_exists(config.QDRANT_COLLECTION)
    if exists and recreate:
        client.delete_collection(config.QDRANT_COLLECTION)
        exists = False

    if not exists:
        client.create_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=config.EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
