import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from loguru import logger

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Users, UserRole
from app.db.crud import get_user_by_email

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_admin(): 
    async with async_session() as session:
        admin = await get_user_by_email(session, settings.superuser_email)
        if admin is None:
            new_admin = Users(
                username="admin",
                email=settings.superuser_email,
                hashed_password=get_password_hash(settings.superuser_password),
                role=UserRole.ADMIN
            )

            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)

            logger.info("Admin initialized", user_id=new_admin.id)
        else:
            logger.debug("Admin already exists")


if __name__ == "__main__":
    asyncio.run(create_admin())