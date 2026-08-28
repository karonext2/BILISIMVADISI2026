"""SQLite tek erişim noktası — dashboard, karşılaştırma ve RAG buradan okur.

Şartname KURAL 9: dashboard ve chatbot AYNI güvenilir veri katmanını kullanır.
"""

from __future__ import annotations

import statistics
from functools import lru_cache
from typing import Any

from data_layer.db import DB_PATH, get_connection, row_to_dict

# Dashboard'da gösterilmeyen ürün aileleri.
# 'yatirim': fon/altın/döviz/hisse bilgilendirme sayfaları — sabit oran/vade/tutar
# yayımlanmadığından kayıtların ~%95'i boş. Kullanıcı isteğiyle listelenmiyor.
GIZLI_AILELER = ("yatirim",)
_GIZLI_WHERE = f"urun_ailesi NOT IN ({','.join('?' * len(GIZLI_AILELER))})"

SIRALAMALAR = {
    "kar_payi_artan": "kar_payi_orani_min IS NULL, kar_payi_orani_min ASC",
    "kar_payi_azalan": "kar_payi_orani_min IS NULL, kar_payi_orani_min DESC",
    "vade_azalan": "vade_max_ay IS NULL, vade_max_ay DESC",
    "vade_artan": "vade_max_ay IS NULL, vade_max_ay ASC",
    "banka": "banka ASC, urun_adi ASC",
    "yeni": "rowid DESC",
}


def veritabani_var_mi() -> bool:
    return DB_PATH.exists()


# ---------------------------------------------------------------------------
# LİSTELEME / FİLTRE
# ---------------------------------------------------------------------------

def _filtre_where(f: dict[str, Any]) -> tuple[str, list]:
    # Gizli aileler her zaman dışlanır (dashboard genelinde)
    kosullar: list[str] = [_GIZLI_WHERE]
    parametreler: list = list(GIZLI_AILELER)

    if f.get("banka"):
        bankalar = f["banka"] if isinstance(f["banka"], list) else [f["banka"]]
        kosullar.append(f"banka IN ({','.join('?' * len(bankalar))})")
        parametreler.extend(bankalar)

    if f.get("kampanya_turu"):
        turler = f["kampanya_turu"] if isinstance(f["kampanya_turu"], list) else [f["kampanya_turu"]]
        kosullar.append(f"kampanya_turu IN ({','.join('?' * len(turler))})")
        parametreler.extend(turler)

    if f.get("urun_ailesi"):
        aileler = f["urun_ailesi"] if isinstance(f["urun_ailesi"], list) else [f["urun_ailesi"]]
        kosullar.append(f"urun_ailesi IN ({','.join('?' * len(aileler))})")
        parametreler.extend(aileler)

    if f.get("aktif_mi") is not None:
        kosullar.append("aktif_mi = ?")
        parametreler.append(1 if f["aktif_mi"] else 0)

    if f.get("has_kar_payi"):
        kosullar.append("kar_payi_orani_min IS NOT NULL")

    if f.get("has_finansal_veri"):
        kosullar.append(
            "(kar_payi_orani_raw IS NOT NULL OR vade_raw IS NOT NULL "
            "OR finansman_tutari_raw IS NOT NULL OR odul_miktari_raw IS NOT NULL "
            "OR alisveris_puani_raw IS NOT NULL OR indirim_orani_raw IS NOT NULL "
            "OR tahsis_ucreti_raw IS NOT NULL OR kampanya_bitis_iso IS NOT NULL "
            "OR kuratorlu = 1)"
        )

    if f.get("vade_min") is not None:
        kosullar.append("vade_max_ay >= ?")
        parametreler.append(f["vade_min"])

    if f.get("vade_max") is not None:
        kosullar.append("vade_min_ay <= ?")
        parametreler.append(f["vade_max"])

    if f.get("kar_payi_min") is not None:
        kosullar.append("kar_payi_orani_min >= ?")
        parametreler.append(f["kar_payi_min"])

    if f.get("kar_payi_max") is not None:
        kosullar.append("kar_payi_orani_min <= ?")
        parametreler.append(f["kar_payi_max"])

    if f.get("q"):
        kosullar.append("(baslik LIKE ? OR urun_adi LIKE ? OR metin LIKE ?)")
        kalip = f"%{f['q']}%"
        parametreler.extend([kalip, kalip, kalip])

    where = (" WHERE " + " AND ".join(kosullar)) if kosullar else ""
    return where, parametreler


def list_campaigns(
    filtreler: dict[str, Any] | None = None,
    sort: str = "banka",
    page: int = 1,
    size: int = 20,
) -> dict:
    filtreler = filtreler or {}
    where, parametreler = _filtre_where(filtreler)
    order = SIRALAMALAR.get(sort, SIRALAMALAR["banka"])
    page = max(1, page)
    size = max(1, min(size, 100))
    offset = (page - 1) * size

    conn = get_connection()
    try:
        toplam = conn.execute(f"SELECT COUNT(*) FROM records{where}", parametreler).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM records{where} ORDER BY {order} LIMIT ? OFFSET ?",
            [*parametreler, size, offset],
        ).fetchall()
    finally:
        conn.close()

    return {
        "page": page,
        "size": size,
        "toplam": toplam,
        "toplam_sayfa": (toplam + size - 1) // size if toplam else 0,
        "items": [row_to_dict(r) for r in rows],
    }


def get_campaign(record_id: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM records WHERE record_id = ?", [record_id]).fetchone()
    finally:
        conn.close()
    return row_to_dict(row) if row else None


def records_for_ids(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT * FROM records WHERE record_id IN ({','.join('?' * len(ids))})", ids
        ).fetchall()
    finally:
        conn.close()
    sirali = {r["record_id"]: row_to_dict(r) for r in rows}
    return [sirali[i] for i in ids if i in sirali]


def all_records(
    filtreler: dict[str, Any] | None = None, tum_aileler: bool = False
) -> list[dict]:
    """tum_aileler=True: gizli aileler dahil (RAG indeksleme için)."""
    if tum_aileler:
        conn = get_connection()
        try:
            rows = conn.execute("SELECT * FROM records").fetchall()
        finally:
            conn.close()
        return [row_to_dict(r) for r in rows]
    where, parametreler = _filtre_where(filtreler or {})
    conn = get_connection()
    try:
        rows = conn.execute(f"SELECT * FROM records{where}", parametreler).fetchall()
    finally:
        conn.close()
    return [row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# BANKALAR / FİLTRE DEĞERLERİ
# ---------------------------------------------------------------------------

def banks() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            f"""
            SELECT banka,
                   MAX(banka_id) AS banka_id,
                   COUNT(*) AS kayit_sayisi,
                   SUM(CASE WHEN kampanya_turu != 'Kampanya Değil' THEN 1 ELSE 0 END) AS kampanya_sayisi
            FROM records WHERE {_GIZLI_WHERE} GROUP BY banka ORDER BY kayit_sayisi DESC
            """,
            list(GIZLI_AILELER),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def filter_values() -> dict:
    g = list(GIZLI_AILELER)
    conn = get_connection()
    try:
        bankalar = [r[0] for r in conn.execute(
            f"SELECT DISTINCT banka FROM records WHERE {_GIZLI_WHERE} ORDER BY banka", g)]
        turler = [r[0] for r in conn.execute(
            f"SELECT DISTINCT kampanya_turu FROM records WHERE {_GIZLI_WHERE} ORDER BY kampanya_turu", g)]
        aileler = [r[0] for r in conn.execute(
            f"SELECT DISTINCT urun_ailesi FROM records WHERE {_GIZLI_WHERE} ORDER BY urun_ailesi", g)]
        vade = conn.execute(
            f"SELECT MIN(vade_min_ay), MAX(vade_max_ay) FROM records "
            f"WHERE {_GIZLI_WHERE} AND vade_max_ay IS NOT NULL", g
        ).fetchone()
        kp = conn.execute(
            "SELECT MIN(kar_payi_orani_min), MAX(kar_payi_orani_max) FROM records "
            "WHERE urun_ailesi='finansman' AND kar_payi_orani_min IS NOT NULL "
            "AND kar_payi_orani_max <= 15"
        ).fetchone()
    finally:
        conn.close()
    return {
        "bankalar": bankalar,
        "kampanya_turleri": turler,
        "urun_aileleri": aileler,
        "vade_araligi_ay": {"min": vade[0], "max": vade[1]},
        "finansman_kar_payi_araligi": {"min": kp[0], "max": kp[1]},
    }


# ---------------------------------------------------------------------------
# İSTATİSTİK (özet kartlar)
# ---------------------------------------------------------------------------

def stats() -> dict:
    g = list(GIZLI_AILELER)
    w = f"WHERE {_GIZLI_WHERE}"
    conn = get_connection()
    try:
        toplam = conn.execute(f"SELECT COUNT(*) FROM records {w}", g).fetchone()[0]
        banka_sayisi = conn.execute(f"SELECT COUNT(DISTINCT banka) FROM records {w}", g).fetchone()[0]
        finansal_veri_olan = conn.execute(
            f"SELECT COUNT(*) FROM records {w} AND (kar_payi_orani_raw IS NOT NULL "
            "OR vade_raw IS NOT NULL OR finansman_tutari_raw IS NOT NULL "
            "OR odul_miktari_raw IS NOT NULL OR alisveris_puani_raw IS NOT NULL "
            "OR indirim_orani_raw IS NOT NULL OR tahsis_ucreti_raw IS NOT NULL "
            "OR kampanya_bitis_iso IS NOT NULL OR kuratorlu = 1)", g
        ).fetchone()[0]
        kuratorlu = conn.execute(f"SELECT COUNT(*) FROM records {w} AND kuratorlu=1", g).fetchone()[0]
        aktif_kampanya = conn.execute(
            f"SELECT COUNT(*) FROM records {w} AND aktif_mi=1 AND kampanya_turu != 'Kampanya Değil'", g
        ).fetchone()[0]
        toplam_kampanya = conn.execute(
            f"SELECT COUNT(*) FROM records {w} AND kampanya_turu != 'Kampanya Değil'", g
        ).fetchone()[0]

        turu = [
            {"tur": r[0], "adet": r[1]}
            for r in conn.execute(
                f"SELECT kampanya_turu, COUNT(*) FROM records {w} GROUP BY 1 ORDER BY 2 DESC", g
            )
        ]
        banka_dag = [
            {"banka": r[0], "adet": r[1]}
            for r in conn.execute(f"SELECT banka, COUNT(*) FROM records {w} GROUP BY 1 ORDER BY 2 DESC", g)
        ]
        aile_dag = [
            {"aile": r[0], "adet": r[1]}
            for r in conn.execute(f"SELECT urun_ailesi, COUNT(*) FROM records {w} GROUP BY 1 ORDER BY 2 DESC", g)
        ]

        fin_oranlar = [
            r[0]
            for r in conn.execute(
                "SELECT kar_payi_orani_min FROM records "
                "WHERE urun_ailesi='finansman' AND kar_payi_orani_min IS NOT NULL "
                "AND kar_payi_orani_max <= 15"
            )
        ]
        vadeler = [
            r[0]
            for r in conn.execute(
                f"SELECT vade_max_ay FROM records {w} AND vade_max_ay IS NOT NULL", g
            )
        ]
        veri_tarihi = conn.execute("SELECT MAX(veri_tarihi) FROM records").fetchone()[0]
    finally:
        conn.close()

    return {
        "toplam_kayit": toplam,
        "toplam_banka": banka_sayisi,
        "toplam_kampanya": toplam_kampanya,
        "aktif_kampanya": aktif_kampanya,
        "finansal_veri_olan_kayit": finansal_veri_olan,
        "kuratorlu_kayit": kuratorlu,
        "kampanya_turu_dagilimi": turu,
        "banka_dagilimi": banka_dag,
        "urun_ailesi_dagilimi": aile_dag,
        "finansman_kar_payi": _ozet(fin_oranlar),
        "vade_dagilimi_ay": _ozet(vadeler),
        "guncelleme_tarihi": veri_tarihi,
    }


def _ozet(degerler: list[float]) -> dict:
    if not degerler:
        return {"min": None, "medyan": None, "max": None, "veri_olan_kayit": 0}
    return {
        "min": round(min(degerler), 2),
        "medyan": round(statistics.median(degerler), 2),
        "max": round(max(degerler), 2),
        "veri_olan_kayit": len(degerler),
    }


@lru_cache(maxsize=1)
def veri_tarihi() -> str:
    conn = get_connection()
    try:
        return conn.execute("SELECT MAX(veri_tarihi) FROM records").fetchone()[0] or ""
    finally:
        conn.close()
