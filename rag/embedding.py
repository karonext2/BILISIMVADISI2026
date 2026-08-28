from __future__ import annotations

import numpy as np

import config
from clients.evren_client import get_evren_client


MAX_CHARS = 6000
OVERLAP_CHARS = 300


def _split_text(text: str) -> list[str]:
    """
    Uzun metinleri bge-m3-embed'in context sınırını aşmayacak
    parçalara böler.
    """

    text = str(text or "").strip()

    if not text:
        return ["Boş içerik"]

    if len(text) <= MAX_CHARS:
        return [text]

    chunks: list[str] = []

    start = 0
    step = MAX_CHARS - OVERLAP_CHARS

    while start < len(text):
        end = start + MAX_CHARS

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def _normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Vektörü cosine similarity için normalize eder.
    """

    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Bir veya birden fazla metni bge-m3-embed ile embedding'e çevirir.

    Çok uzun metinler parçalara bölünür.
    Chunk embeddingleri ağırlıklı ortalama ile tek vektöre çevrilir.
    """

    if not texts:
        return []

    client = get_evren_client()

    final_vectors: list[list[float]] = []

    for text in texts:

        chunks = _split_text(text)

        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=chunks,
        )

        # API'den gelen sıralamayı garanti altına al
        response_items = sorted(
            response.data,
            key=lambda item: item.index,
        )

        chunk_vectors = [
            np.asarray(item.embedding, dtype=np.float32)
            for item in response_items
        ]

        if not chunk_vectors:
            raise RuntimeError(
                "Embedding modeli boş vektör döndürdü."
            )

        # --------------------------------------------------
        # TEK CHUNK
        # --------------------------------------------------
        if len(chunk_vectors) == 1:
            vector = chunk_vectors[0]

        # --------------------------------------------------
        # BİRDEN FAZLA CHUNK
        # --------------------------------------------------
        else:
            weights = np.asarray(
                [len(chunk) for chunk in chunks],
                dtype=np.float32,
            )

            vector = np.average(
                np.stack(chunk_vectors),
                axis=0,
                weights=weights,
            )

        vector = _normalize_vector(vector)

        if len(vector) != config.EMBEDDING_DIM:
            raise RuntimeError(
                "Embedding boyutu hatalı. "
                f"Beklenen={config.EMBEDDING_DIM}, "
                f"Gelen={len(vector)}"
            )

        final_vectors.append(vector.tolist())

    # BU RETURN ÇOK ÖNEMLİ
    return final_vectors


def embed_text(text: str) -> list[float]:
    """
    Tek bir metni embedding'e çevirir.
    Retriever bu fonksiyonu kullanır.
    """

    vectors = embed_texts([text])

    if not vectors:
        raise RuntimeError(
            "Tek metin embedding işlemi boş sonuç döndürdü."
        )

    return vectors[0]