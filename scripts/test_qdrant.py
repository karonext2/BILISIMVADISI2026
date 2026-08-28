from __future__ import annotations

import config
from rag.qdrant_client import get_qdrant_client

def main():
    client = get_qdrant_client()
    collections = client.get_collections()
    print("Qdrant bağlantısı başarılı.")
    print("Koleksiyonlar:")
    for col in collections.collections:
        print("-", col.name)

if __name__ == "__main__":
    main()
