from fastapi import APIRouter

from api.v1 import calculate, campaigns, chat, compare, meta

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(meta.router, tags=["genel"])
api_router.include_router(campaigns.router, tags=["kampanyalar"])
api_router.include_router(calculate.router, tags=["hesaplama"])
api_router.include_router(compare.router, tags=["karşılaştırma"])
api_router.include_router(chat.router, tags=["asistan"])
