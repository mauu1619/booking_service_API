from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    Depends, 
    Query, 
    Path, 
    APIRouter, 
    HTTPException, 
    status
)

from app.db.session import get_session
from app.db.crud import (
    get_rooms, 
    get_room, 
    get_room_by_title, 
    create_room,
    update_room,
    delete_room
)
from app.models import (
    RoomsShow, 
    PaginatedRooms, 
    RoomCreate, 
    Users, 
    RoomUpdate
)
from app.api.deps import get_admin_user
from app.core.logger import logger

router = APIRouter(prefix='/rooms', tags=['rooms'])
SessionDep = Annotated[AsyncSession, Depends(get_session)]
AdminDep = Annotated[Users, Depends(get_admin_user)]


@router.get("", response_model=PaginatedRooms)
async def rooms_list(
    db: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 100,
):
    logger.info("Request", method="GET", path="/rooms")

    rooms, total = await get_rooms(db=db, skip=offset, limit=limit)
    return PaginatedRooms(items=rooms, total=total, limit=limit, offset=offset)


@router.get("/{room_id}", response_model=RoomsShow)
async def room_detail(
    room_id: Annotated[int, Path(ge=1)],
    db: SessionDep
):
    logger.info("Request", method="GET", path=f"/rooms/{room_id}")

    room = await get_room(db, room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room doesn't exist"
        )
    
    return room


@router.post("", response_model=RoomsShow, status_code=status.HTTP_201_CREATED)
async def room_create(
    room_in: RoomCreate,
    db: SessionDep,
    _: AdminDep
):
    logger.info("Request", method="POST", path="/rooms")

    room = await get_room_by_title(db, title=room_in.title)
    if room is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with the same title already exist"
        )
    
    return await create_room(db, room_in)


@router.patch("/{room_id}", response_model=RoomsShow)
async def room_modify(
    room_id: Annotated[int, Path(ge=1)],
    room_update: RoomUpdate,
    db: SessionDep,
    _: AdminDep
):
    logger.info("Request", method="PATCH", path=f"/rooms/{room_id}")

    updated = await update_room(db, room_id, room_update)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room doesn't exist"
        ) 
    
    return updated


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def room_remove(
    room_id: Annotated[int, Path(ge=1)],
    db: SessionDep,
    _: AdminDep
):
    logger.info("Request", method="DELETE", path=f"/rooms/{room_id}")

    deleted = await delete_room(db, room_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room doesn't exist"
        )     