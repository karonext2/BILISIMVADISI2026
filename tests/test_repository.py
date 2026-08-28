"""SQLite veri katmanı testleri. `data/final/karonext.sqlite` gerektirir
(önce: python scripts/02_build_db.py)."""

import pytest

from data_layer import repository as repo

pytestmark = pytest.mark.skipif(
    not repo.veritabani_var_mi(),
    reason="karonext.sqlite yok — önce scripts/02_build_db.py çalıştırın",
)


def test_stats_dinamik():
    s = repo.stats()
    assert 350 < s["toplam_kayit"] < 469  # yatirim ailesi dashboard'dan gizli
    assert s["toplam_banka"] == 10
    assert s["guncelleme_tarihi"]  # veriden gelir, hardcoded değil
    assert isinstance(s["kampanya_turu_dagilimi"], list)


def test_banks():
    b = repo.banks()
    assert len(b) == 10
    assert 350 < sum(x["kayit_sayisi"] for x in b) < 469


def test_filter_values_makul():
    fv = repo.filter_values()
    assert len(fv["bankalar"]) == 10
    assert "finansman" in fv["urun_aileleri"]
    v = fv["vade_araligi_ay"]
    assert 1 <= v["min"] <= v["max"] <= 480


def test_yatirim_ailesi_dashboarddan_gizli():
    assert "yatirim" not in repo.filter_values()["urun_aileleri"]
    assert repo.list_campaigns({"urun_ailesi": "yatirim"})["toplam"] == 0
    aileler = {d["aile"] for d in repo.stats()["urun_ailesi_dagilimi"]}
    assert "yatirim" not in aileler
    # RAG için tüm aileler erişilebilir kalmalı
    assert any(r["urun_ailesi"] == "yatirim" for r in repo.all_records(tum_aileler=True))


def test_list_campaigns_filtre_ve_sayfalama():
    r = repo.list_campaigns({"urun_ailesi": "finansman"}, sort="kar_payi_artan", page=1, size=5)
    assert r["toplam"] > 0
    assert len(r["items"]) <= 5
    assert all(it["urun_ailesi"] == "finansman" for it in r["items"])


def test_get_campaign_ve_liste_alanlari():
    r = repo.list_campaigns(page=1, size=1)
    rid = r["items"][0]["record_id"]
    kayit = repo.get_campaign(rid)
    assert kayit["record_id"] == rid
    assert isinstance(kayit["avantajlar"], list)
    assert isinstance(kayit["aktif_mi"], bool)


def test_records_for_ids_sira_korunur():
    r = repo.list_campaigns(page=1, size=3)
    ids = [it["record_id"] for it in r["items"]]
    geri = repo.records_for_ids(list(reversed(ids)))
    assert [x["record_id"] for x in geri] == list(reversed(ids))
