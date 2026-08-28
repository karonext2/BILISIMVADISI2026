"""SQLite bağlantısı ve şema — `data/final/karonext.sqlite`."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "final" / "karonext.sqlite"

# Record modelindeki liste alanları (SQLite'ta JSON metni olarak tutulur)
LISTE_ALANLARI = ("hedef_kitle", "kampanya_kosullari", "avantajlar")
# Record modelindeki bool alanları (SQLite'ta 0/1)
BOOL_ALANLARI = ("aktif_mi", "kuratorlu")

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    record_id                 TEXT PRIMARY KEY,
    banka                     TEXT NOT NULL,
    banka_id                  TEXT,
    urun_adi                  TEXT,
    baslik                    TEXT,
    kampanya_turu             TEXT,
    urun_ailesi               TEXT,
    urun_kategorisi           TEXT,
    kuratorlu                 INTEGER,
    kar_payi_orani_min        REAL,
    kar_payi_orani_max        REAL,
    kar_payi_turu             TEXT,
    kar_payi_orani_raw        TEXT,
    finansman_orani           REAL,
    finansman_tutari_min      REAL,
    finansman_tutari_max      REAL,
    finansman_tutari_raw      TEXT,
    vade_min_ay               INTEGER,
    vade_max_ay               INTEGER,
    vade_raw                  TEXT,
    taksit_sayisi             INTEGER,
    tahsis_ucreti_tl          REAL,
    tahsis_ucreti_orani       REAL,
    tahsis_ucreti_raw         TEXT,
    masraf_bilgisi            TEXT,
    odul_miktari_tl           REAL,
    odul_miktari_raw          TEXT,
    alisveris_puani           REAL,
    alisveris_puani_raw       TEXT,
    indirim_orani             REAL,
    indirim_orani_raw         TEXT,
    kampanya_baslangic_tarihi TEXT,
    kampanya_bitis_tarihi     TEXT,
    kampanya_bitis_iso        TEXT,
    aktif_mi                  INTEGER,
    hedef_kitle               TEXT,
    kampanya_kosullari        TEXT,
    avantajlar                TEXT,
    url                       TEXT,
    kaynak                    TEXT,
    metin                     TEXT,
    veri_tarihi               TEXT
);
CREATE INDEX IF NOT EXISTS idx_records_banka       ON records(banka);
CREATE INDEX IF NOT EXISTS idx_records_urun_ailesi ON records(urun_ailesi);
CREATE INDEX IF NOT EXISTS idx_records_turu        ON records(kampanya_turu);
CREATE INDEX IF NOT EXISTS idx_records_aktif       ON records(aktif_mi);
"""


def get_connection(path: Path | str | None = None) -> sqlite3.Connection:
    p = Path(path) if path else DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    """SQLite satırını kanonik dict'e çevirir (JSON listeleri ve bool'lar geri açılır)."""
    d = dict(row)
    for alan in LISTE_ALANLARI:
        if alan in d:
            try:
                d[alan] = json.loads(d[alan]) if d[alan] else []
            except (json.JSONDecodeError, TypeError):
                d[alan] = []
    for alan in BOOL_ALANLARI:
        if alan in d and d[alan] is not None:
            d[alan] = bool(d[alan])
    return d


def record_to_row(record: dict) -> dict:
    """Kanonik dict'i SQLite'a yazılabilir biçime çevirir."""
    d = dict(record)
    for alan in LISTE_ALANLARI:
        d[alan] = json.dumps(d.get(alan) or [], ensure_ascii=False)
    for alan in BOOL_ALANLARI:
        d[alan] = 1 if d.get(alan) else 0
    return d
