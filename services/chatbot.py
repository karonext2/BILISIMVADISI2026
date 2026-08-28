from __future__ import annotations

import json

import config
from clients.evren_client import get_evren_client
from nlp.schemas import CHAT_SEMASI

def answer_with_context(query: str, records: list[dict]) -> dict:
    client = get_evren_client()

    context_blocks = []
    valid_ids = []
    for idx, record in enumerate(records, 1):
        rid = str(record.get("record_id", ""))
        valid_ids.append(rid)
        context_blocks.append(
            f"""[{idx}]
record_id: {rid}
banka: {record.get('banka', '')}
urun: {record.get('urun_adi') or record.get('baslik', '')}
kampanya_turu: {record.get('kampanya_turu', '')}
kar_payi_orani: {record.get('kar_payi_orani', '')}
vade_ay: {record.get('vade_ay', '')}
finansman_tutari_tl: {record.get('finansman_tutari_tl', '')}
odul_miktari_tl: {record.get('odul_miktari_tl', '')}
masraf_bilgisi: {record.get('masraf_bilgisi', '')}
hedef_kitle: {record.get('hedef_kitle', '')}
kosullar: {record.get('kampanya_kosullari', '')}
url: {record.get('url', '')}
"""
        )

    system = """
Sen KARONEXT katılım bankacılığı chatbotusun.
Yalnızca verilen Qdrant kayıtlarına dayanarak cevap ver.
Kayıtlarda bulunmayan güncel oran, ücret veya koşul uydurma.
Sayısal karşılaştırma gerekiyorsa uygulama kodunun ürettiği sonuç verilmedikçe
kendi başına aritmetik yapma.
Kullandığın record_id değerlerini çıktıda bildir.
""".strip()

    user = f"""
SORU:
{query}

GETİRİLEN KAYITLAR:
{chr(10).join(context_blocks)}
""".strip()

    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "karonext_chat",
                "schema": CHAT_SEMASI,
                "strict": True,
            },
        },
        temperature=0.0,
        max_tokens=1000,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Chatbot boş yanıt döndürdü.")

    result = json.loads(content)

    # Modelin context dışı id uydurmasını engelle.
    valid = set(valid_ids)
    result["kullanilan_kayit_idleri"] = [
        rid for rid in result.get("kullanilan_kayit_idleri", [])
        if rid in valid
    ]
    return result
