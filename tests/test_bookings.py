from datetime import date
from decimal import Decimal as D

import pytest
from httpx import AsyncClient

from app.core.security import create_token, decode_token


@pytest.mark.asyncio
async def test_list_my_bookings(client: AsyncClient, test_bookings):
    user_token = create_token({"sub": str(test_bookings.user_id)}, type='access')
    response = await client.get("/bookings", headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert D(data[0]['total_cost']) == D("707.7")
    assert D(data[1]['total_cost']) == D("404.4")


@pytest.mark.asyncio
async def test_list_empty_bookings(client: AsyncClient, test_bookings, another_token):
    response = await client.get("/bookings", headers={"Authorization": f"Bearer {another_token}"})

    assert response.status_code == 200
    data = response.json()
    assert not data


@pytest.mark.asyncio
async def test_create_booking(client: AsyncClient, user_token, test_room):
    response = await client.post(
        "/bookings",
        json={
            "date_from": '2026-08-16',
            "date_to": '2026-08-19',
            "room_id": test_room.id
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert (date.fromisoformat(data['date_to']) 
            - date.fromisoformat(data['date_from'])).days == 3
    assert D(data['total_cost']) == D("303.3")
    assert data['room_id'] == test_room.id
    
    payload = decode_token(user_token)
    assert payload is not None
    user_id = payload.get("sub")
    assert str(data['user_id']) == user_id


@pytest.mark.asyncio
async def test_create_booking_with_dates_in_the_past(client: AsyncClient, user_token, test_room):
    response = await client.post(
        "/bookings",
        json={
            "date_from": "2026-02-21",
            "date_to": "2026-02-26",
            "room_id": test_room.id
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_booking_with_dateto_earlier_than_datefrom(client: AsyncClient, user_token, test_room):
    response = await client.post(
        "/bookings",
        json={
            "date_from": "2026-05-15",
            "date_to": "2026-05-12",
            "room_id": test_room.id
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_not_enough_rooms_for_cross_dates(client: AsyncClient, test_bookings):
    user_token = create_token({"sub": str(test_bookings.user_id)}, type='access')
    response = await client.post(
        "/bookings",
        json={
            "date_from": '2026-06-24',
            "date_to": '2026-06-25',
            "room_id": test_bookings.room_id
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 400
    assert "No rooms available" in response.json()['detail']


@pytest.mark.asyncio
async def test_cancel_booking_as_admin(client: AsyncClient, test_booking, admin_token):
    response = await client.delete(
        f"/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_cancel_booking_as_owner(client: AsyncClient, test_booking):
    user_token = create_token({"sub": str(test_booking.user_id)}, type='access')
    response = await client.delete(
        f"/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_cancel_booking_as_another_user(client: AsyncClient, test_booking, another_token):
    response = await client.delete(
        f"/bookings/{test_booking.id}",
        headers={"Authorization": f"Bearer {another_token}"}
    )

    assert response.status_code == 403