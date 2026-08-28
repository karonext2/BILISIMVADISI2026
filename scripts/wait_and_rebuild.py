"""EVREN servisi geri gelince otomatik olarak:
  1) kalan (basarisiz) kayitlari yeniden dener (--resume)
  2) 02_build_db.py
  3) chunk_dataset.py
  4) 03_index.py --recreate
calistirir. Servis kapaliysa periyodik kontrol ederek bekler (max WAIT_CAP_SEC).

    python scripts/wait_and_rebuild.py
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config

BASE_DIR = Path(__file__).resolve().parent.parent
PY = str(BASE_DIR / ".venv" / "Scripts" / "python.exe")

POLL_SEC = 20
WAIT_CAP_SEC = 2 * 60 * 60  # 2 saat


def llm_ready() -> bool:
    try:
        from clients.evren_client import get_evren_client
        client = get_evren_client()
        r = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
        )
        return bool(r.choices)
    except Exception as exc:
        print(f"[bekleniyor] LLM hazir degil: {exc}", flush=True)
        return False


def embedding_ready() -> bool:
    try:
        from clients.evren_client import get_evren_client
        client = get_evren_client()
        r = client.embeddings.create(model=config.EMBEDDING_MODEL, input=["ping"])
        return len(r.data[0].embedding) == config.EMBEDDING_DIM
    except Exception as exc:
        print(f"[bekleniyor] Embedding hazir degil: {exc}", flush=True)
        return False


def run(cmd: list[str], label: str) -> bool:
    print(f"\n=== {label} ===", flush=True)
    proc = subprocess.run(cmd, cwd=str(BASE_DIR))
    ok = proc.returncode == 0
    print(f"=== {label} {'OK' if ok else 'HATA exit=' + str(proc.returncode)} ===", flush=True)
    return ok


def main() -> int:
    start = time.time()
    print("EVREN servisinin geri gelmesi bekleniyor...", flush=True)
    while True:
        if llm_ready() and embedding_ready():
            print("EVREN servisi hazir (LLM + embedding). Pipeline baslıyor.", flush=True)
            break
        if time.time() - start > WAIT_CAP_SEC:
            print(f"[IPTAL] {WAIT_CAP_SEC}s bekleme suresi doldu, servis hala hazir degil.", flush=True)
            return 1
        time.sleep(POLL_SEC)

    if not run([PY, "scripts/process_dataset_parallel.py", "--workers", "16", "--resume"], "LLM cikarim (kalanlari tamamla)"):
        print("[UYARI] Cikarimda hatalar olabilir, devam ediliyor (errors.jsonl kontrol edilmeli).", flush=True)

    if not run([PY, "scripts/02_build_db.py"], "SQLite build"):
        print("[IPTAL] DB build basarisiz, chunk/index calistirilmiyor.", flush=True)
        return 1

    if not run([PY, "scripts/chunk_dataset.py"], "Chunk uretimi"):
        print("[IPTAL] Chunk uretimi basarisiz, index calistirilmiyor.", flush=True)
        return 1

    if not run([PY, "scripts/03_index.py", "--recreate"], "Qdrant reindex"):
        print("[IPTAL] Qdrant reindex basarisiz.", flush=True)
        return 1

    print("\nPIPELINE_TAMAMLANDI", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
