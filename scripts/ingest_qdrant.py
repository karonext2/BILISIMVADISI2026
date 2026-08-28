"""[ESKİ] Bu script artık `scripts/03_index.py`'e yönlendirir.

Eski kayıt-başına-tek-vektör yaklaşımı (rag/ingest.py + rag/embedding.py ortalama
mantığı) yerini chunk-başına indekslemeye bıraktı.

    python scripts/03_index.py --recreate
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    print("Not: ingest_qdrant.py kullanımdan kalktı -> scripts/03_index.py çalıştırılıyor\n")
    sys.argv[0] = str(Path(__file__).resolve().parent / "03_index.py")
    runpy.run_path(sys.argv[0], run_name="__main__")
