import asyncio
from collections.abc import AsyncGenerator

import pytest 
from sqlmodel import SQLModel
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db.session import get_session
from app import models
from app.main import app
from app.core.security import create_token, get_password_hash

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
       await conn.run_sync(SQLModel.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def get_override_session():
        yield db_session

    app.dependency_overrides[get_session] = get_override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    from app.models import Users, UserRole

    user = Users(
        username="test_user",
        email="test@example.com",
        hashed_password=get_password_hash("user123"),
        role=UserRole.DEFAULT
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def another_user(db_session: AsyncSession):
    from app.models import Users, UserRole

    user = Users(
        username="another_user",
        email="another@example.com",
        hashed_password=get_password_hash("123123123"),
        role=UserRole.DEFAULT
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    from app.models import Users, UserRole

    admin = Users(
        username="admin_user",
        email="admin@axample.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user):
    return create_token({"sub": str(test_user.id)}, type='access')


@pytest.fixture
def admin_token(admin_user):
    return create_token({"sub": str(admin_user.id)}, type='access')


@pytest.fixture
def another_token(another_user):
    return create_token({"sub": str(another_user.id)}, type='access')


@pytest.fixture
async def test_room(db_session: AsyncSession):
    from decimal import Decimal as D

    from app.models import Rooms

    room = Rooms(
        title="test_room_1",
        description="test description",
        price=D("101.1"),
        quantity=2
    )

    db_session.add(room)
    await db_session.commit()
    await db_session.refresh(room)
    return room


@pytest.fixture
async def test_rooms(db_session: AsyncSession, test_room):
    from decimal import Decimal as D
    
    from app.models import Rooms

    room = Rooms(
        title="test_room_2",
        price=D("102.2"),
        quantity=3
    )

    db_session.add(room)
    await db_session.commit()
    await db_session.refresh(room)
    return room


@pytest.fixture
async def test_booking(db_session: AsyncSession, test_user, test_room):
    from datetime import date, timedelta
    from decimal import Decimal as D

    from app.models import Bookings

    booking = Bookings(
        date_from=date(2026, 6, 20),
        date_to=date(2026, 6, 27),
        room_id=test_room.id,
        user_id=test_user.id,
        total_cost=test_room.price * D(timedelta(days=7).days)
    )

    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)
    return booking


@pytest.fixture
async def test_bookings(db_session: AsyncSession, test_user, test_room):
    from datetime import date, timedelta
    from decimal import Decimal as D

    from app.models import Bookings

    booking_1 = Bookings(
        date_from=date(2026, 6, 21),
        date_to=date(2026, 6, 28),
        room_id=test_room.id,
        user_id=test_user.id,
        total_cost=test_room.price * D(timedelta(days=7).days)
    )
    booking_2 = Bookings(
        date_from=date(2026, 6, 22),
        date_to=date(2026, 6, 26),
        room_id=test_room.id,
        user_id=test_user.id,
        total_cost=test_room.price * D(timedelta(days=4).days)
    )

    db_session.add_all([booking_1, booking_2])
    await db_session.commit()
    await db_session.refresh(booking_2)
    return booking_2