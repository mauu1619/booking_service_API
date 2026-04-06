from decimal import Decimal as D

from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.models import (
    Rooms, 
    Users, 
    UserCreate, 
    RoomCreate,
    RoomUpdate,
    Bookings,
    BookingCreate,
    UserRole
)
from app.core.security import get_password_hash


async def create_user(db: AsyncSession, user: UserCreate) -> Users:
    hash_pass = get_password_hash(user.password)
    db_user = Users(
        username=user.username,
        email=user.email,
        hashed_password=hash_pass
    )

    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: int) -> Users | None:
    result = await db.execute(select(Users).where(Users.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Users | None:
    result = await db.execute(select(Users).where(Users.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: EmailStr) -> Users | None:
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()


async def get_rooms(
    db: AsyncSession,
    skip: int,
    limit: int,
) -> tuple[list[Rooms], int]:
    result = await db.execute(select(Rooms).offset(skip).limit(limit))
    total_result = await db.execute(select(func.count()).select_from(Rooms))
    return list(result.scalars().all()), total_result.scalar_one()


async def get_room(db: AsyncSession, room_id: int) -> Rooms | None:
    room = await db.get(Rooms, room_id)
    return room


async def get_room_by_title(db: AsyncSession, title: str) -> Rooms | None:
    room = await db.execute(select(Rooms).where(Rooms.title == title))
    return room.scalar_one_or_none()


async def make_user_inactive(db: AsyncSession, user_id: int) -> bool:
    user = await get_user(db, user_id)
    if user is None:
        return False
    
    user.is_active = False

    await db.flush()
    return True


async def create_room(db: AsyncSession, room: RoomCreate) -> Rooms:
    db_room = Rooms(**room.model_dump())

    db.add(db_room)
    await db.flush()
    await db.refresh(db_room)
    return db_room


async def update_room(db: AsyncSession, room_id: int, room_update: RoomUpdate) -> Rooms | None:
    db_room = await get_room(db, room_id)
    if db_room is None:
        return None
    
    updated_data = room_update.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_room, key, value)

    await db.flush()
    await db.refresh(db_room)
    return db_room


async def delete_room(db: AsyncSession, room_id: int) -> bool:
    db_room = await get_room(db, room_id)
    if db_room is None:
        return False
    
    await db.delete(db_room)
    await db.flush()
    return True


async def get_bookings(db: AsyncSession, user_id: int | None) -> list[Bookings]:
    result = await db.execute(select(Bookings).where(Bookings.user_id == user_id))
    return list(result.scalars().all())


async def get_rooms_for_update(db: AsyncSession, room_id: int) -> Rooms | None:
    result = await db.execute(
        select(Rooms)
        .where(Rooms.id == room_id)
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def create_booking(
    db: AsyncSession,
    user_id: int | None,
    booking_data: BookingCreate
) -> Bookings:
    room = await get_rooms_for_update(db, booking_data.room_id)
    if room is None:
        raise ValueError("Room doesn't exist")
    
    statement = (
        select(func.count())
        .select_from(Bookings)
        .where(Bookings.room_id == room.id)
        .where(Bookings.date_from < booking_data.date_to)
        .where(booking_data.date_from < Bookings.date_to)
    )

    result = await db.execute(statement)
    occupied_count = result.scalar() or 0

    if room.quantity - occupied_count <= 0:
        raise ValueError("No rooms available")
    
    db_booking = Bookings(
        date_from=booking_data.date_from,
        date_to=booking_data.date_to,
        user_id=user_id, 
        room_id=room.id,
        total_cost=room.price * D((
            booking_data.date_to - booking_data.date_from
        ).days)
    )

    db.add(db_booking)
    await db.flush()
    await db.refresh(db_booking)
    return db_booking


async def get_booking(db: AsyncSession, booking_id: int, **kwargs) -> Bookings | None:
    booking = await db.get(Bookings, booking_id, **kwargs)
    return booking


async def delete_booking(
    db: AsyncSession, 
    booking_id: int,
    user_id: int | None,
    role: UserRole
):
    db_booking = await get_booking(db, booking_id, with_for_update=True)
    if db_booking is None:
        raise ValueError("Booking doesn't exist")

    if db_booking.user_id != user_id and role != UserRole.ADMIN:
        raise PermissionError("Not enough required permissions")
    
    await db.delete(db_booking)
    await db.flush()