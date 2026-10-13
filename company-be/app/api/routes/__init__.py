from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.payments import router as payments_router
from app.api.routes.refunds import router as refunds_router
from app.api.routes.tickets import router as tickets_router

__all__ = [
    "customers_router",
    "health_router",
    "orders_router",
    "payments_router",
    "refunds_router",
    "tickets_router",
]
