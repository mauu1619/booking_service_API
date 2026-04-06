import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    response = await client.post(
        "/auth/register", 
        json={
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "new123"
        }        
    )

    assert response.status_code == 201
    data = response.json()
    assert data['username'] == 'new_user'
    assert data['email'] == 'new_user@example.com'
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/register",
        json={
            "username": "test_user",
            "email": "another@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400
    assert "Username already exists" == response.json()['detail']


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/register",
        json={
            "username": "another_user",
            "email": "test@example.com",
            "password": "pass123"
        }
    )

    assert response.status_code == 400
    assert "Email already exists" == response.json()['detail']


@pytest.mark.asyncio
async def test_register_with_invalid_datas(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "username": "invalid_user",
            "email": "not_an_email",
            "password": "pass456"
        }
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": "test_user",
            "password": "user123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    response = await client.post(
        "/auth/login",
        data={
            "username": "test_user",
            "password": "user456"
        }
    )

    assert response.status_code == 401
    assert "Incorrect" in response.json()['detail']


@pytest.mark.asyncio 
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        data={
            "username": "nobody",
            "password": "blablabla"
        }
    )

    assert response.status_code == 401
    assert "Incorrect" in response.json()['detail']


@pytest.mark.asyncio
async def test_update_tokens_with_refresh(client: AsyncClient, test_user):
    await client.post(
        "/auth/login",
        data={
            "username": "test_user",
            "password": "user123"
        }
    )
    old_refresh = client.cookies.get(name="refresh_token", path="/auth")

    await asyncio.sleep(1.1)

    response = await client.post("/auth/refresh")
    assert response.status_code == 200
    assert "refresh_token" in client.cookies
    assert old_refresh != client.cookies.get(name="refresh_token", path="/auth")
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == 'bearer'


@pytest.mark.asyncio
async def test_update_tokens_with_no_refresh(client: AsyncClient):
    response = await client.post("/auth/refresh")

    assert response.status_code == 401
    assert "missing" in response.json()['detail']


@pytest.mark.asyncio
async def test_get_me_by_token(client: AsyncClient, user_token):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['username'] == 'test_user'
    assert data['email'] == 'test@example.com'
    assert 'password' not in data


@pytest.mark.asyncio
async def test_logout_with_refresh_token(client: AsyncClient, test_user):
    await client.post(
        "/auth/login",
        data={
            "username": "test_user",
            "password": "user123"
        }
    )

    response = await client.post("/auth/logout")
    assert response.status_code == 200
    assert "successfully" in response.json()['detail']
    assert "refresh_token" not in client.cookies


@pytest.mark.asyncio
async def test_logout_with_no_refresh(client: AsyncClient):
    response = await client.post("/auth/logout")

    assert response.status_code == 401
    assert "missing" in response.json()['detail']


@pytest.mark.asyncio
async def test_make_user_inactive(client: AsyncClient, test_user, admin_token, db_session):
    response = await client.delete(
        f"/auth/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 204
    await db_session.refresh(test_user)
    assert not test_user.is_active