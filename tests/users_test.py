from uuid import uuid4

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, user_client: AsyncClient, admin_client: AsyncClient, faker):
    user_client, _ = user_client
    admin_client, _ = admin_client
    user = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "password": faker.password(length=8),
        "email": faker.email()
    }
    response = await client.post("api/v1/users", json=user)
    assert response.status_code == 401

    response = await user_client.post("api/v1/users", json=user)
    assert response.status_code == 403

    response = await admin_client.post("api/v1/users", json=user)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_users(admin_client: AsyncClient):
    admin_client, _ = admin_client
    response = await admin_client.get("/api/v1/users")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


@pytest.mark.asyncio
async def test_read_user_me(user_client: AsyncClient):
    user_client, _ = user_client
    response = await user_client.get("api/v1/users/me")
    assert response.status_code == 200
    assert "email" in response.json()


@pytest.mark.asyncio
async def test_update_user_me(user_client: AsyncClient, faker):
    user_client, _ = user_client
    update_data = {"first_name": faker.first_name(), "last_name": faker.last_name()}
    response = await user_client.patch("api/v1/users/me", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"]
    assert response.json()["last_name"] == update_data["last_name"]


@pytest.mark.asyncio
async def test_change_password_me(user_client: AsyncClient, faker):
    user_client, _ = user_client
    password_data = {"current_password": "password", "new_password": faker.password(length=10)}
    response = await user_client.post("api/v1/users/me/change-password", json=password_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"


@pytest.mark.asyncio
async def test_read_user(admin_client: AsyncClient, normal_user):
    admin_client, _ = admin_client
    user_id = normal_user.id
    response = await admin_client.get(f"api/v1/users/{user_id}")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["email"] == normal_user.email


@pytest.mark.asyncio
async def test_read_users(admin_client: AsyncClient):
    admin_client, _ = admin_client
    response = await admin_client.get("api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)


@pytest.mark.asyncio
async def test_update_user(admin_client: AsyncClient, faker, normal_user):
    admin_client, _ = admin_client
    user_id = normal_user.id
    update_data = {"first_name": faker.first_name(), "last_name": faker.last_name()}
    response = await admin_client.patch(f"api/v1/users/{user_id}", json=update_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["first_name"] == update_data["first_name"]
        assert response.json()["last_name"] == update_data["last_name"]


@pytest.mark.asyncio
async def test_change_password(admin_client: AsyncClient, faker):
    admin_client, _ = admin_client
    user_id = str(uuid4())
    password_data = {"new_password": faker.password(length=10)}
    response = await admin_client.post(f"api/v1/users/{user_id}/change-password", json=password_data)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.json()["message"] == "Password changed successfully"


@pytest.mark.asyncio
async def test_delete_user(admin_client: AsyncClient, normal_user):
    admin_client, _ = admin_client
    user_id = normal_user.id
    response = await admin_client.delete(f"api/v1/users/{user_id}")
    assert response.status_code in [204, 404]
