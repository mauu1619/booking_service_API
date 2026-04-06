from typing import Annotated

from fastapi import Depends, Path, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.api.deps import get_default_user
from app.models import (
    Users,
    BookingShow,
    BookingCreate,
)
from app.db.crud import (
    get_bookings,
    create_booking,
    delete_booking,
)
from app.tasks import send_booking_email
from app.core.logger import logger

router = APIRouter(prefix="/bookings", tags=['bookings'])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
UserDep = Annotated[Users, Depends(get_default_user)]


@router.get("", response_model=list[BookingShow])
async def my_bookings(
    user: UserDep,
    db: SessionDep
):
    logger.info("Request", method="GET", path="/bookings", user_id=user.id)

    bookings = await get_bookings(db, user.id) 
    return bookings


@router.post("", response_model=BookingShow, status_code=status.HTTP_201_CREATED)
async def add_booking(
    booking_in: BookingCreate,
    user: UserDep,
    db: SessionDep,
):
    logger.info("Request", method="POST", path="/bookings", user_id=user.id)
    try:
        new_booking = await create_booking(db, user.id, booking_in)
    except ValueError as e:
        error_msg = str(e)
        logger.error("Booking failed", error=error_msg, user_id=user.id)
        if "doesn't exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    else:
        logger.info(
            "Booking created",
            user_id=user.id,
            room_id=new_booking.room_id,
            date_from=new_booking.date_from,
            date_to=new_booking.date_to
        )

        await send_booking_email.kiq(
            name=user.username, 
            email=user.email,
            date_from=new_booking.date_from, 
            date_to=new_booking.date_to,
            total_cost=str(new_booking.total_cost)
        )

        return new_booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: Annotated[int, Path(ge=1)],
    db: SessionDep,
    user: UserDep
):
    logger.info("Request", method="DELETE", path=f"/bookings/{booking_id}", user_id=user.id)
    try:
        await delete_booking(db, booking_id, user.id, user.role)
    except ValueError as e:
        logger.exception("Booking canceling failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        logger.exception("Booking canceling failed")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    else:
        logger.info("Booking canceled", booking_id=booking_id, user_id=user.id)