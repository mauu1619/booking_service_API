import asyncio
from datetime import date, timedelta
from decimal import Decimal

from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Bookings, Rooms, UserRole, Users

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def seed_data() -> None:
    if settings.model_config.get("env_file") == ".env":
        # Check ENV from environment

        import os

        env = os.getenv("ENV", "dev").lower()
        if env == "prod":
            logger.error("Seeding is disabled in PRODUCTION environment!")
            return

    async with async_session() as session:
        # 1. Create Users
        password = get_password_hash("password123")
        user1 = Users(
            username="testuser",
            email="user@example.com",
            hashed_password=password,
            role=UserRole.DEFAULT,
        )
        user2 = Users(
            username="testadmin",
            email="admin_test@example.com",
            hashed_password=password,
            role=UserRole.ADMIN,
        )

        session.add_all([user1, user2])
        await session.flush()

        # 2. Create Rooms
        room1 = Rooms(
            title="Lux Apartment",
            description="Beautiful sea view, king size bed, minibar.",
            price=Decimal("15000.00"),
            quantity=5,
        )
        room2 = Rooms(
            title="Standard Room",
            description="Cozy room for two people.",
            price=Decimal("5000.00"),
            quantity=10,
        )
        room3 = Rooms(
            title="Economy Single",
            description="Budget option for solo travelers.",
            price=Decimal("2500.00"),
            quantity=15,
        )

        session.add_all([room1, room2, room3])
        await session.flush()

        # 3. Create some Bookings
        today = date.today()
        booking1 = Bookings(
            room_id=room1.id,
            user_id=user1.id,
            date_from=today + timedelta(days=1),
            date_to=today + timedelta(days=5),
            total_cost=room1.price * 4,
        )
        booking2 = Bookings(
            room_id=room2.id,
            user_id=user1.id,
            date_from=today + timedelta(days=10),
            date_to=today + timedelta(days=12),
            total_cost=room2.price * 2,
        )

        session.add_all([booking1, booking2])

        try:
            await session.commit()
            logger.info("Database successfully seeded with test data!")
        except Exception:
            await session.rollback()
            logger.exception("Failed to seed database")
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
