from fastapi import APIRouter

from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.payments import router as payments_router
from app.api.routes.refunds import router as refunds_router
from app.api.routes.tickets import router as tickets_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(customers_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(tickets_router)
api_v1_router.include_router(refunds_router)

__all__ = ["api_v1_router", "health_router"]
