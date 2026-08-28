"""Retriever entegrasyon testi — EVREN Qdrant'ta dolu koleksiyon gerektirir
(önce: python scripts/03_index.py --recreate). Erişilemezse atlanır."""

import pytest

from core.settings import settings
from rag.retriever import retrieve

try:
    from rag.qdrant_client import get_qdrant_client

    _sayim = get_qdrant_client().count(settings.qdrant_collection).count
except Exception:  # noqa: BLE001
    _sayim = 0

pytestmark = pytest.mark.skipif(_sayim < 100, reason="Qdrant koleksiyonu boş/erişilemez")


def test_bos_sorgu():
    assert retrieve("") == []


def test_temel_getirme():
    r = retrieve("konut finansmanı kâr payı oranı", top_k=5)
    assert 1 <= len(r) <= 5
    assert all("_skor" in x and "record_id" in x for x in r)
    skorlar = [x["_skor"] for x in r]
    assert skorlar == sorted(skorlar, reverse=True)


def test_record_id_tekil():
    r = retrieve("taşıt finansmanı", top_k=8)
    idler = [x["record_id"] for x in r]
    assert len(idler) == len(set(idler))


def test_banka_filtresi_sunucu_tarafi():
    r = retrieve("finansman", top_k=6, bankalar=["Kuveyt Türk"])
    assert all(x["banka"] == "Kuveyt Türk" for x in r)


def test_urun_ailesi_filtresi():
    r = retrieve("getiri oranı", top_k=5, urun_ailesi="mevduat")
    assert all(x["urun_ailesi"] == "mevduat" for x in r)
