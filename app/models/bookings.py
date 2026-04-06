from typing import TYPE_CHECKING
from typing_extensions import Self
from datetime import date, datetime
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Numeric, Column
from pydantic import model_validator


if TYPE_CHECKING:
    from .rooms import Rooms
    from .users import Users


class BookingBase(SQLModel):
    date_from: date = Field(index=True)
    date_to: date = Field(index=True)


class BookingCreate(BookingBase):
    room_id: int

    @model_validator(mode='after')
    def check_dates(self) -> Self:
        if self.date_from < date.today():
            raise ValueError("date_from cannot be in the past")

        if self.date_to <= self.date_from:
            raise ValueError("date_to must be later than date_from")
        
        return self


class BookingShow(BookingBase):
    id: int
    user_id: int
    room_id: int
    total_cost: Decimal


class BookingUpdate(SQLModel):
    date_from: date | None = None
    date_to: date | None = None
    total_cost: Decimal | None = None


class Bookings(BookingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(foreign_key='users.id', ondelete='CASCADE', index=True)
    room_id: int | None = Field(foreign_key='rooms.id', ondelete='CASCADE', index=True)
    total_cost: Decimal = Field(sa_column=Column(Numeric(10, 2)))

    user: "Users" = Relationship(back_populates='bookings')
    room: "Rooms" = Relationship(back_populates='bookings')