from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

import app.core.logger
from app.core.logger import logger
from app.api import auth_router, bookings_router, rooms_router

app = FastAPI(
    title="Booking Service API",
    description="REST API for managing bookings, rooms and users",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(rooms_router)


@app.get("/")
async def root():
    return {
        "message": "Booking Service API",
        "docs": "/docs",
        "repository": "https://github.com/mauu1619/booking_service_API",
        "endpoints": {
            "auth": "/auth",
            "rooms": "/rooms",
            "bookings": "/bookings"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal error"}
    )