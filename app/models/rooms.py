from typing import TYPE_CHECKING, Sequence
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Numeric


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


class Rooms(RoomsShow, table=True):
    id: int | None = Field(default=None, primary_key=True)

    bookings: list["Bookings"] = Relationship(back_populates='room', passive_deletes='all')


class RoomUpdate(RoomBase):
    title: str | None = None
    price: Decimal | None = None
    quantity: int | None = None


class PaginatedRooms(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: Sequence[RoomsShow]
    total: int
    limit: int 
    offset: int