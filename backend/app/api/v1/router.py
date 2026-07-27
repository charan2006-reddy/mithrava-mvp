"""Main v1 API router aggregating all sub-routers."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.crops import router as crops_router
from app.api.v1.disease import router as disease_router
from app.api.v1.farmers import router as farmers_router
from app.api.v1.finance import router as finance_router
from app.api.v1.forum import router as forum_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.market import router as market_router
from app.api.v1.mitra import router as mitra_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.support import router as support_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.weather import router as weather_router

api_router = APIRouter()

# Register all sub-routers
api_router.include_router(auth_router)
api_router.include_router(farmers_router)
api_router.include_router(crops_router)
api_router.include_router(disease_router)
api_router.include_router(weather_router)
api_router.include_router(market_router)
api_router.include_router(finance_router)
api_router.include_router(vendors_router)
api_router.include_router(forum_router)
api_router.include_router(support_router)
api_router.include_router(notifications_router)
api_router.include_router(mitra_router)
api_router.include_router(knowledge_router)
api_router.include_router(admin_router)
