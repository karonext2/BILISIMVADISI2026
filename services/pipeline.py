from __future__ import annotations

from nlp.processor import process_record
from rag.retriever import retrieve
from services.chatbot import answer_with_context
from services.comparison import compare_records

def extract_pipeline(payload: dict) -> dict:
    return process_record(payload)

def search_pipeline(
    query: str,
    top_k: int = 5,
    bankalar: list[str] | None = None,
) -> list[dict]:
    return retrieve(query=query, top_k=top_k, bankalar=bankalar)

def chat_pipeline(
    query: str,
    top_k: int = 5,
    bankalar: list[str] | None = None,
) -> dict:
    records = retrieve(query=query, top_k=top_k, bankalar=bankalar)
    result = answer_with_context(query=query, records=records)
    return {
        "retrieved": records,
        "answer": result,
    }

def compare_pipeline(
    query: str,
    top_k: int = 10,
    bankalar: list[str] | None = None,
) -> dict:
    records = retrieve(query=query, top_k=top_k, bankalar=bankalar)
    return {
        "retrieved": records,
        "comparison": compare_records(records),
    }
