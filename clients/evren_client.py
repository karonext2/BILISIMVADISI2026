from __future__ import annotations

from functools import lru_cache
from openai import OpenAI

import config

@lru_cache(maxsize=1)
def get_evren_client() -> OpenAI:
    config.require_evren()
    return OpenAI(
        base_url=config.EVREN_BASE_URL,
        api_key=config.EVREN_API_KEY,
        timeout=config.EVREN_TIMEOUT,
        max_retries=2,
    )
