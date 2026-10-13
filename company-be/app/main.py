import os

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_v1_router, health_router

app = FastAPI(
    title="FlowPilot Mock Company Backend",
    description=(
        "Simulated e-commerce company backend REST API for FlowPilot AI integration. "
        "Provides mock endpoints for Customers, Orders, Payments, Support Tickets, and Refund Proposals."
    ),
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS Configuration
raw_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for clean, predictable responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Format request validation errors consistently without exposing internal tracebacks."""
    errors = exc.errors()
    error_messages = []
    for err in errors:
        loc = " -> ".join(str(item) for item in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        error_messages.append(f"{loc}: {msg}" if loc else msg)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "; ".join(error_messages)},
    )


# Register Routers
app.include_router(health_router)
app.include_router(api_v1_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
