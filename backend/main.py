import logging
import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.core.exceptions import SaloneFixException
from app.core.logging import setup_logging, bind_request_id, reset_request_id
from app.api.v1.router import api_router
from app.db.init_db import init_db

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger("salonefix.request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database schema and seed data
    init_db()
    yield
    # Shutdown logic if any


app = FastAPI(
    title="SaloneFix API",
    description="Freetown Public-Service Incident Management Platform - Human-First Foundation Launch",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID and Timing Middleware
@app.middleware("http")
async def request_id_and_timing_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    token = bind_request_id(request_id)
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "request_failed",
            extra={"data": {"method": request.method, "path": request.url.path}},
        )
        raise
    finally:
        reset_request_id(token)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    logger.info(
        "request",
        extra={
            "data": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(process_time * 1000, 2),
            }
        },
    )
    return response


# Standard Exception Handlers
@app.exception_handler(SaloneFixException)
async def salonefix_exception_handler(request: Request, exc: SaloneFixException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.detail.get("error_code", "INTERNAL_ERROR"),
            "message": exc.detail.get("message", "An error occurred"),
            "details": exc.detail.get("details", {}),
            "request_id": getattr(request.state, "request_id", None),
        },
        headers={"X-Request-ID": getattr(request.state, "request_id", "")},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request payload validation failed.",
            "details": {"errors": exc.errors()},
            "request_id": getattr(request.state, "request_id", None),
        },
        headers={"X-Request-ID": getattr(request.state, "request_id", "")},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Stable INTERNAL_ERROR envelope; details stay in the structured log, not the response.
    logging.getLogger("salonefix.error").exception("unhandled_exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please retry or contact support with the request ID.",
            "details": {},
            "request_id": getattr(request.state, "request_id", None),
        },
        headers={"X-Request-ID": getattr(request.state, "request_id", "")},
    )


# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "phase": "Human-First Foundation Launch",
        "ai_enabled": settings.AI_ENABLED,
        "whatsapp_enabled": settings.WHATSAPP_ENABLED,
    }


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
