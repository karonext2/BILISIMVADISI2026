from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import config
from clients.evren_client import get_evren_client
from nlp.schemas import FINANSAL_CIKARIM_SEMASI

_PROMPT_DIR = Path(__file__).resolve().parent / "prompts"


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    return (_PROMPT_DIR / "extraction_system.md").read_text(encoding="utf-8").strip()


@lru_cache(maxsize=1)
def _user_template() -> str:
    return (_PROMPT_DIR / "extraction_user.md").read_text(encoding="utf-8").strip()


def _build_user_prompt(metin: str, banka: str | None, baslik: str | None) -> str:
    return (
        _user_template()
        .replace("{{BANKA}}", (banka or "Belirtilmemiş").strip())
        .replace("{{BASLIK}}", (baslik or "Belirtilmemiş").strip())
        .replace("{{METIN}}", metin.strip())
    )


def _call_llm(client, user_prompt: str, max_tokens: int = 6000):
    return client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "katilim_bankaciligi_finansal_cikarim",
                "schema": FINANSAL_CIKARIM_SEMASI,
                "strict": True,
            },
        },
        temperature=0.0,
        max_tokens=max_tokens,
        extra_body={"enable_thinking": False},
    )


_RETRY_HINT = (
    "\n\nÖNCEKİ ÇIKTI GEÇERLİ JSON DEĞİLDİ. Bu kez daha kısa yaz: "
    "kampanya_kosullari en fazla 6, avantajlar en fazla 4, hedef_kitle en fazla 4 "
    "kısa madde. Her madde tek kısa cümle. Sayısal değerleri ve aralıkları değiştirme. "
    "Yalnızca geçerli JSON üret, şema dışına çıkma."
)


def extract_financial_info(
    text: str,
    banka: str | None = None,
    baslik: str | None = None,
) -> dict:
    """Katılım bankacılığı metninden strict şemaya uygun finansal bilgi çıkarır."""

    if not text or not str(text).strip():
        raise ValueError("Metin boş olamaz.")

    client = get_evren_client()
    user_prompt = _build_user_prompt(str(text), banka, baslik)

    # 1. deneme
    response = _call_llm(client, user_prompt)
    choice = response.choices[0]
    content = choice.message.content

    if content and content.strip():
        try:
            return json.loads(content)
        except json.JSONDecodeError as first_error:
            pass
    else:
        first_error = RuntimeError(
            f"llm boş yanıt döndürdü (finish_reason={choice.finish_reason})"
        )

    # 2. deneme / fallback — prompt'u KISALT, uzatma
    retry_response = _call_llm(client, user_prompt + _RETRY_HINT)
    retry_choice = retry_response.choices[0]
    retry_content = retry_choice.message.content

    if not retry_content or not retry_content.strip():
        raise RuntimeError(
            "llm-fast iki denemede de kullanılabilir yanıt üretemedi. "
            f"finish_reason={retry_choice.finish_reason}, usage={retry_response.usage}"
        )

    try:
        return json.loads(retry_content)
    except json.JSONDecodeError as retry_error:
        raise RuntimeError(
            "llm-fast iki denemede de geçerli JSON üretemedi. "
            f"İlk hata: {first_error}. İkinci hata: {retry_error}. "
            f"finish_reason={retry_choice.finish_reason}"
        ) from retry_error
