from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from app.core.security import decode_token
from app.db.session import get_session
from app.models import Users, UserRole
from app.db.crud import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", refreshUrl="auth/refresh")


async def get_default_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)]
) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await get_user(db, int(user_id))
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise credentials_exception

    return user


async def get_admin_user(
    current_user: Annotated[Users, Depends(get_default_user)]
) -> Users:
    if current_user.role != UserRole.ADMIN:
        logger.warning("Admin access attempt", user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    logger.warning("Admin actions", user_id=current_user.id)
    return current_user