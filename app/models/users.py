from typing import TYPE_CHECKING
from enum import Enum

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship


if TYPE_CHECKING:
    from .bookings import Bookings


class UserRole(str, Enum):
    DEFAULT = 'default'
    ADMIN = 'admin'


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, min_length=4, max_length=30)
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    role: UserRole = UserRole.DEFAULT


class Users(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    bookings: list["Bookings"] = Relationship(back_populates='user', passive_deletes='all')


class UserCreate(UserBase):
    password: str


class UserShow(UserBase):
    pass