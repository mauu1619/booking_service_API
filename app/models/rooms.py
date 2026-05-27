from collections.abc import Sequence
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .bookings import Bookings


class RoomBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = None
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    quantity: int


class RoomsShow(RoomBase):
    id: int


class RoomCreate(RoomBase):
    pass


class Rooms(RoomBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    bookings: list["Bookings"] = Relationship(
        back_populates="room", passive_deletes="all"
    )


class RoomUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    quantity: int | None = None


class PaginatedRooms(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    items: Sequence[RoomsShow]
    total: int
    limit: int
    offset: int
