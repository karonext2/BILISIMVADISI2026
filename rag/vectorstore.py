"""EVREN Qdrant üzerinde LangChain vektör deposu."""

from __future__ import annotations

from functools import lru_cache

from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import Distance, VectorParams

from core.settings import settings
from llm.base import get_embeddings
from rag.qdrant_client import get_qdrant_client

CONTENT_KEY = "chunk_text"
METADATA_KEY = "meta"


def ensure_collection(recreate: bool = False) -> None:
    client = get_qdrant_client()
    var = client.collection_exists(settings.qdrant_collection)
    if var and recreate:
        client.delete_collection(settings.qdrant_collection)
        var = False
    if not var:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=settings.embedding_dim, distance=Distance.COSINE),
        )
    # Sunucu tarafı filtre için payload index'leri
    for alan in ("banka", "urun_ailesi", "kampanya_turu", "record_id"):
        try:
            client.create_payload_index(
                settings.qdrant_collection, f"{METADATA_KEY}.{alan}", field_schema="keyword"
            )
        except Exception:  # noqa: BLE001 — zaten varsa geç
            pass


@lru_cache(maxsize=1)
def get_vectorstore() -> QdrantVectorStore:
    return QdrantVectorStore(
        client=get_qdrant_client(),
        collection_name=settings.qdrant_collection,
        embedding=get_embeddings(),
        content_payload_key=CONTENT_KEY,
        metadata_payload_key=METADATA_KEY,
    )
