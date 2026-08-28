"""
finansal_veriler_yapilandirilmis.json içindeki kayıtları RAG için
chunk'lara böler.

- Her kaydın yapılandırılmış alanları + serbest metni birleştirilir.
- Uzun metin, örtüşmeli (overlap) karakter pencereleriyle segmentlere bölünür.
- Çıktı, dosya başına sabit sayıda KAYNAK KAYIT olacak şekilde
  data/processed/chunks/chunks_XXX.jsonl dosyalarına yazılır.

Kullanım:
    python scripts/chunk_dataset.py
    python scripts/chunk_dataset.py --chunk-size 800 --overlap 150 --per-file 50
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

OUTPUT_DIR = BASE_DIR / "data/processed/chunks"

# Chunk metnine dahil edilecek yapılandırılmış alanlar (etiketli).
META_FIELDS = [
    ("banka", "Banka"),
    ("urun_adi", "Ürün"),
    ("baslik", "Başlık"),
    ("urun_kategorisi", "Ürün kategorisi"),
    ("kampanya_turu", "Kampanya türü"),
    ("kar_payi_orani_raw", "Kâr payı oranı"),
    ("vade_raw", "Vade"),
    ("finansman_tutari_raw", "Finansman / bakiye tutarı"),
    ("tahsis_ucreti_raw", "Tahsis ücreti"),
    ("masraf_bilgisi", "Masraf bilgisi"),
    ("odul_miktari_raw", "Ödül miktarı"),
    ("indirim_orani_raw", "İndirim oranı"),
    ("alisveris_puani_raw", "Alışveriş puanı"),
    ("kampanya_baslangic_tarihi", "Kampanya başlangıç"),
    ("kampanya_bitis_tarihi", "Kampanya bitiş"),
]

# Payload'a taşınacak alanlar.
PAYLOAD_FIELDS = [
    "record_id", "banka", "banka_id", "baslik", "urun_adi", "urun_ailesi",
    "urun_kategorisi", "kampanya_turu", "url", "kaynak", "kuratorlu",
    "kar_payi_orani_min", "kar_payi_orani_max", "kar_payi_turu",
    "vade_max_ay", "finansman_tutari_max", "finansman_orani",
    "taksit_sayisi", "tahsis_ucreti_tl", "odul_miktari_tl", "indirim_orani",
    "alisveris_puani", "kampanya_baslangic_tarihi", "kampanya_bitis_tarihi",
]


def load_records() -> list[dict]:
    """Kanonik kaynaktan (karonext.sqlite) okur — tek doğru kaynak."""
    from data_layer import repository as repo

    if not repo.veritabani_var_mi():
        raise SystemExit("Önce: python scripts/02_build_db.py")
    return repo.all_records(tum_aileler=True)  # RAG tüm aileleri indeksler


def clean(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none", "null", "[]"}:
        return ""
    return text


def build_document(record: dict) -> str:
    """Kaydı tek bir metin bloğuna çevirir."""
    lines: list[str] = []
    for key, label in META_FIELDS:
        val = clean(record.get(key))
        if val:
            lines.append(f"{label}: {val}")

    for list_key, label in (("avantajlar", "Avantajlar"),
                            ("hedef_kitle", "Hedef kitle"),
                            ("kampanya_kosullari", "Kampanya koşulları")):
        raw = record.get(list_key)
        items: list = []
        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, str) and raw.strip().startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    items = parsed
            except json.JSONDecodeError:
                pass
        items = [clean(i) for i in items if clean(i)]
        if items:
            lines.append(f"{label}: " + "; ".join(items))

    metin = clean(record.get("metin"))
    if metin:
        # ardışık boşlukları sadeleştir
        metin = re.sub(r"[ \t]+", " ", metin)
        metin = re.sub(r"\n{3,}", "\n\n", metin)
        lines.append("")
        lines.append("Metin:")
        lines.append(metin)

    return "\n".join(lines).strip()


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Karakter bazlı, örtüşmeli bölme. Mümkünse boşlukta keser."""
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    step = max(1, chunk_size - overlap)
    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            # kelime ortasında kesmemek için son boşluğa geri sar
            window = text[start:end]
            cut = window.rfind(" ")
            if cut > chunk_size * 0.5:
                end = start + cut
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def make_payload(record: dict) -> dict:
    payload = {}
    for key in PAYLOAD_FIELDS:
        val = record.get(key)
        if isinstance(val, float) and val != val:  # NaN
            val = None
        payload[key] = val
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=150)
    parser.add_argument("--per-file", type=int, default=50,
                        help="Çıktı dosyası başına kaynak kayıt sayısı.")
    args = parser.parse_args()

    if args.overlap >= args.chunk_size:
        print("overlap, chunk-size'dan küçük olmalı.", file=sys.stderr)
        return 1

    records = load_records()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # eski çıktıları temizle
    for old in args.out_dir.glob("chunks_*.jsonl"):
        old.unlink()

    total_chunks = 0
    total_records = 0
    empty_records = 0
    file_index = 0
    manifest_files: list[dict] = []

    current_fh = None
    current_path = None
    current_records = 0
    current_chunks = 0

    def open_next():
        nonlocal current_fh, current_path, current_records, current_chunks, file_index
        if current_fh is not None:
            current_fh.close()
            manifest_files.append({
                "file": current_path.name,
                "records": current_records,
                "chunks": current_chunks,
            })
        file_index += 1
        current_path = args.out_dir / f"chunks_{file_index:03d}.jsonl"
        current_fh = current_path.open("w", encoding="utf-8")
        current_records = 0
        current_chunks = 0

    open_next()

    for record in records:
        record_id = clean(record.get("record_id")) or f"idx_{total_records}"
        document = build_document(record)
        pieces = split_text(document, args.chunk_size, args.overlap)

        if not pieces:
            empty_records += 1
            continue

        if current_records >= args.per_file:
            open_next()

        payload = make_payload(record)
        for i, piece in enumerate(pieces):
            row = {
                "chunk_id": f"{record_id}_{i}",
                "record_id": record_id,
                "chunk_index": i,
                "chunk_count": len(pieces),
                "char_len": len(piece),
                "text": piece,
                **payload,
            }
            current_fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            current_chunks += 1
            total_chunks += 1

        current_records += 1
        total_records += 1

    if current_fh is not None:
        current_fh.close()
        manifest_files.append({
            "file": current_path.name,
            "records": current_records,
            "chunks": current_chunks,
        })

    manifest = {
        "source": "data/final/karonext.sqlite",
        "chunk_size": args.chunk_size,
        "overlap": args.overlap,
        "records_per_file": args.per_file,
        "total_source_records": len(records),
        "chunked_records": total_records,
        "empty_records": empty_records,
        "total_chunks": total_chunks,
        "files": manifest_files,
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Kaynak kayıt      : {len(records)}")
    print(f"Chunk'lanan kayıt : {total_records}  (boş: {empty_records})")
    print(f"Toplam chunk      : {total_chunks}")
    print(f"Çıktı dosyası     : {len(manifest_files)} adet -> {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
