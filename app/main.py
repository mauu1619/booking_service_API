from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth_router, bookings_router, rooms_router
from app.core.logger import logger

app = FastAPI(
    title="Booking Service API",
    description="REST API for managing bookings, rooms and users",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(rooms_router)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "message": "Booking Service API",
        "docs": "/docs",
        "repository": "https://github.com/mauu1619/booking_service_API",
        "endpoints": {"auth": "/auth", "rooms": "/rooms", "bookings": "/bookings"},
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, HTTPException):
        handler = request.app.exception_handlers.get(HTTPException)
        if handler:
            return cast(Response, await handler(request, exc))

    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal error"},
    )
