from decimal import Decimal as D

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_rooms(client: AsyncClient, test_room):
    response = await client.get("/rooms")

    assert response.status_code == 200
    data = response.json()
    assert data['total'] == len(data['items'])
    room = data['items'][0]
    assert room['title'] == "test_room_1"
    assert room['description'] == 'test description'
    assert D(room['price']) == D("101.1")
    assert room['quantity'] == 2


@pytest.mark.asyncio
async def test_list_rooms_with_filter(client: AsyncClient, test_rooms):
    response =  await client.get("/rooms?offset=1")

    assert response.status_code == 200
    data = response.json()
    assert data['total'] != len(data['items'])
    assert len(data['items']) == 1
    assert data['items'][0]['title'] == 'test_room_2'


    response = await client.get("/rooms?limit=1")

    assert response.status_code == 200
    data = response.json()
    assert data['total'] != len(data['items'])
    assert len(data['items']) == 1
    assert data['items'][0]['title'] == 'test_room_1'


@pytest.mark.asyncio
async def test_detail_room(client: AsyncClient, test_room):
    response = await client.get(f"/rooms/{test_room.id}")

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'test_room_1'


@pytest.mark.asyncio
async def test_detail_nonexistent_room(client: AsyncClient):
    response = await client.get("/rooms/1")

    assert response.status_code == 404
    assert "doesn't exist" in response.json()['detail']


@pytest.mark.asyncio
async def test_create_room(client: AsyncClient, admin_token):
    response = await client.post(
        "/rooms", 
        json={
            'title': 'new_room',
            'description': 'new room',
            'price': "100.01",
            'quantity': 1
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data['title'] == 'new_room'
    assert data['description'] == 'new room'
    assert D(data['price']) == D("100.01")
    assert data['quantity'] == 1


@pytest.mark.asyncio
async def test_create_room_with_invalid_datas(client: AsyncClient, admin_token):
    response = await client.post(
        "/rooms",
        json={
            "title": "invalid_room",
            "price": "free",
            "quantity": "infinity"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_room_with_the_same_title(client: AsyncClient, test_room, admin_token): 
    response = await client.post(
        "/rooms",
        json={
            "title": "test_room_1",
            "price": "1238",
            "quantity": 12
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_room_as_default_user(client: AsyncClient, user_token):
    response = await client.post(
        "/rooms",
        json={
            "title": "new_room",
            "price": "100.12",
            "quantity": 1
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_room(client: AsyncClient, test_room, admin_token):
    response = await client.patch(
        f"/rooms/{test_room.id}",
        json={
            'title': "another_title"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'another_title'
    assert data['description'] == 'test description'


@pytest.mark.asyncio
async def test_update_room_as_default_user(client: AsyncClient, test_room, user_token):
    response = await client.patch(
        f"/rooms/{test_room.id}",
        json={
            "title": "another_title"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_room(client: AsyncClient, test_room, admin_token):
    response = await client.delete(
        f"/rooms/{test_room.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_room_as_default_user(client: AsyncClient, test_room, user_token):
    response = await client.delete(
        f"/rooms/{test_room.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 403