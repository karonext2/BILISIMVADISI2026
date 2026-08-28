"""EVREN LLM API ve Qdrant bağlantı kontrolü.

Anahtarlar .env'den okunur (komut satırına yazılmaz).

    python scripts/check_connectivity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config


def check_llm() -> bool:
    try:
        from clients.evren_client import get_evren_client

        client = get_evren_client()
        models = client.models.list()
        adlar = [m.id for m in models.data][:10]
        print(f"[OK]  EVREN LLM API — {len(adlar)} model. Örnek: {adlar}")
        if config.LLM_MODEL not in [m.id for m in models.data]:
            print(f"[UYARI] .env LLM_MODEL={config.LLM_MODEL} listede görünmüyor.")
        return True
    except Exception as exc:
        print(f"[HATA] EVREN LLM API: {type(exc).__name__}: {exc}")
        return False


def check_embedding() -> bool:
    try:
        from clients.evren_client import get_evren_client

        client = get_evren_client()
        resp = client.embeddings.create(model=config.EMBEDDING_MODEL, input=["deneme"])
        dim = len(resp.data[0].embedding)
        durum = "OK" if dim == config.EMBEDDING_DIM else "UYARI"
        print(f"[{durum}] EVREN embedding — boyut={dim} (beklenen {config.EMBEDDING_DIM})")
        return True
    except Exception as exc:
        print(f"[HATA] EVREN embedding: {type(exc).__name__}: {exc}")
        return False


def check_qdrant() -> bool:
    try:
        from rag.qdrant_client import get_qdrant_client

        client = get_qdrant_client()
        var = client.collection_exists(config.QDRANT_COLLECTION)
        print(
            f"[OK]  EVREN Qdrant — bağlantı kuruldu. "
            f"'{config.QDRANT_COLLECTION}' koleksiyonu: {'var' if var else 'yok'}"
        )
        return True
    except Exception as exc:
        print(f"[HATA] EVREN Qdrant: {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    print("=== KARONEXT bağlantı kontrolü ===")
    sonuclar = [check_llm(), check_embedding(), check_qdrant()]
    ok = sum(1 for s in sonuclar if s)
    print(f"\n{ok}/3 bileşen erişilebilir.")
    return 0 if ok == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
