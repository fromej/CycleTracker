from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_register(client: AsyncClient, faker):
    user_data = {
        "email": faker.email(),
        "password": faker.password(length=10),
        "first_name": faker.first_name(),
        "last_name": faker.last_name()
    }
    response = await client.post("api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        assert response.json()["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_login(client: AsyncClient, faker):
    user_data = {
        "email": faker.email(),
        "password": faker.password(length=10),
        "first_name": faker.first_name(),
        "last_name": faker.last_name()
    }
    response = await client.post("api/v1/auth/register", json=user_data)
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        assert response.json()["email"] == user_data["email"]

    login_data = dict(username=user_data["email"], password=user_data["password"])

    response = await client.post("api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    response = await client.post("api/v1/auth/refresh")
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.post("api/v1/auth/logout")
    assert response.status_code == 303
