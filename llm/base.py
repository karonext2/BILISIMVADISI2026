"""LLM / embedding sağlayıcı soyutlaması.

Şu an: EVREN (OpenAI uyumlu, uzak). İleride lokal modele geçiş için `LLM_BACKEND`
ve `EMBEDDING_BACKEND` anahtarları `core/settings.py` içinde hazır — yalnızca
buradaki fabrikaya `local` kolu eklemek yeterli olacak.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from core.settings import settings


@lru_cache(maxsize=4)
def get_chat_model(temperature: float = 0.0, max_tokens: int = 1200) -> ChatOpenAI:
    if settings.llm_backend != "evren":
        raise NotImplementedError(
            f"LLM_BACKEND={settings.llm_backend} henüz uygulanmadı (yalnızca 'evren')."
        )
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=settings.evren_base_url,
        api_key=settings.evren_api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=settings.evren_timeout,
        max_retries=2,
        # EVREN llm-fast "thinking" token'ları completion bütçesini yiyor -> kapat
        extra_body={"enable_thinking": False},
    )


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    if settings.embedding_backend != "evren":
        raise NotImplementedError(
            f"EMBEDDING_BACKEND={settings.embedding_backend} henüz uygulanmadı."
        )
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        base_url=settings.evren_base_url,
        api_key=settings.evren_api_key,
        # EVREN modeli OpenAI tokenizer'ına uymadığı için ctx uzunluk kontrolü kapalı
        check_embedding_ctx_length=False,
        chunk_size=48,
        timeout=settings.evren_timeout,
    )
