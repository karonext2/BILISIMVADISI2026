"""Yapılandırılmış loglama + sır maskeleme."""

from __future__ import annotations

import logging
import re
import sys

from core.settings import settings

_SIRLAR = [s for s in (settings.evren_api_key, settings.evren_qdrant_key) if s]
_MASKE_RE = re.compile("|".join(re.escape(s) for s in _SIRLAR)) if _SIRLAR else None


class SecretMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if _MASKE_RE and isinstance(record.msg, str):
            record.msg = _MASKE_RE.sub("***", record.msg)
        return True


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s | %(message)s")
    )
    handler.addFilter(SecretMaskingFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


logger = logging.getLogger("karonext")
