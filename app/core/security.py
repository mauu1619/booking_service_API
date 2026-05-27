from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from app.core.config import settings


class AccessToken(BaseModel):
    access_token: str
    token_type: str


password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hash_password: str) -> bool:
    return password_hash.verify(plain_password, hash_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_token(data: dict[str, Any], type: str) -> str:
    to_encode = data.copy()
    if type == "access":
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    elif type == "refresh":
        expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    else:
        expire = datetime.now(UTC) + timedelta(minutes=1)

    to_encode.update({"exp": expire, "type": type})
    return jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), settings.algorithm
    )


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token, settings.secret_key.get_secret_value(), [settings.algorithm]
        )
        return payload
    except InvalidTokenError:
        return None
