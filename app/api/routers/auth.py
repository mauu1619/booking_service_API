from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Path, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_admin_user, get_default_user
from app.core.config import settings
from app.core.logger import logger
from app.core.security import (
    AccessToken,
    create_token,
    decode_token,
    verify_password,
)
from app.db.crud import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    make_user_inactive,
)
from app.db.redis import get_redis_session
from app.db.session import get_session
from app.models import UserCreate, UserRole, Users, UserShow

router = APIRouter(prefix="/auth", tags=["auth"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis_session)]
expire_days_seconds = settings.refresh_token_expire_days * 24 * 60 * 60


@router.post("/register", response_model=UserShow, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: SessionDep):
    logger.info("Request", method="POST", path="/auth/register")

    if await get_user_by_username(db, user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    if await get_user_by_email(db, user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    if user.role != UserRole.DEFAULT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to create admin"
        )

    return await create_user(db, user)


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    response: Response,
    redis: RedisDep,
) -> AccessToken:
    logger.info(
        "Request", method="POST", path="/auth/login", username=form_data.username
    )
    user = await get_user_by_username(db, form_data.username)

    if user is None:
        logger.warning("Failed login attempt", username=form_data.username)
        verify_password(form_data.password, settings.dummy_hash)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning("Failed login attempt", username=form_data.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token({"sub": str(user.id)}, type="access")
    refresh_token = create_token({"sub": str(user.id)}, type="refresh")

    await redis.set(
        f"user:{user.id}:refresh", value=refresh_token, ex=expire_days_seconds
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=expire_days_seconds,
        path="/auth",
        httponly=True,
        samesite="lax",
        # secure=True
    )

    logger.info("User login", user_id=user.id)
    return AccessToken(access_token=access_token, token_type="bearer")


@router.post("/refresh")
async def refresh(
    response: Response,
    redis: RedisDep,
    refresh_token: Annotated[str, Cookie()] = "No token",
) -> AccessToken:
    logger.info("Request", method="POST", path="/auth/refresh")

    if refresh_token == "No token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(refresh_token)
    if payload is None or payload["type"] != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    db_token = await redis.get(f"user:{user_id}:refresh")
    if not db_token or db_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token({"sub": user_id}, type="access")
    refresh_token = create_token({"sub": user_id}, type="refresh")

    await redis.set(
        f"user:{user_id}:refresh", value=refresh_token, ex=expire_days_seconds
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        path="/auth",
        max_age=expire_days_seconds,
        httponly=True,
        samesite="lax",
        # secure=True
    )

    logger.info("User refresh tokens", user_id=user_id)
    return AccessToken(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(
    response: Response,
    redis: RedisDep,
    refresh_token: Annotated[str, Cookie()] = "No token",
):
    logger.info("Request", method="POST", path="/auth/logout")
    if refresh_token == "No token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(refresh_token)
    if payload is None or payload["type"] != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    await redis.delete(f"user:{user_id}:refresh")

    response.delete_cookie("refresh_token", path="/auth")

    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserShow)
async def get_me(user: Annotated[Users, Depends(get_default_user)]):
    logger.info("Request", method="GET", path="/auth/me", user_id=user.id)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def inactive(
    user_id: Annotated[int, Path(ge=1)],
    db: SessionDep,
    _: Annotated[Users, Depends(get_admin_user)],
):
    logger.info("Request", method="DELETE", path=f"/auth/{user_id}")
    inactive = await make_user_inactive(db, user_id)
    if not inactive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Such user doesn't exist"
        )
