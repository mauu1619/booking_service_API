from .auth import router as auth_router
from .bookings import router as bookings_router
from .rooms import router as rooms_router

__all__ = ["auth_router", "bookings_router", "rooms_router"]
