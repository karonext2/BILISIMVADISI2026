from __future__ import annotations

from pydantic import BaseModel, Field

class ExtractRequest(BaseModel):
    banka: str | None = None
    baslik: str | None = None
    metin: str = Field(..., min_length=2)
    url: str | None = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=5, ge=1, le=30)
    bankalar: list[str] | None = None

class CompareRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=10, ge=2, le=50)
    bankalar: list[str] | None = None

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)
    bankalar: list[str] | None = None
