import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_period(user_client: AsyncClient, faker):
    user_client, _ = user_client
    period_data = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-05",
        "flow_intensity": "Medium",
        "notes": faker.text(max_nb_chars=100),
        "symptoms": [{"name": faker.word()}]
    }
    response = await user_client.post("api/v1/periods", json=period_data)
    assert response.status_code == 201
    if response.status_code == 201:
        json = response.json()
        assert "id" in json
        for key, value in period_data.items():
            if key != "symptoms":
                assert json[key] == value
            else:
                assert json[key][0]["name"] == value[0]["name"]


@pytest.mark.asyncio
async def test_list_periods(user_client: AsyncClient, a_period):
    user_client, user = user_client
    [await a_period(user) for _ in range(5)]
    response = await user_client.get("api/v1/periods")
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)
    assert response.json()["total"] == 5


@pytest.mark.asyncio
async def test_get_period_intensity_counts(user_client: AsyncClient):
    user_client, user = user_client
    response = await user_client.get("api/v1/periods/intensity-counts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_recent_period(user_client: AsyncClient, a_period):
    user_client, user = user_client
    await a_period(user)
    response = await user_client.get("api/v1/periods/recent")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_period(user_client: AsyncClient, a_period):
    user_client, user = user_client
    test_period = await a_period(user)
    response = await user_client.get(f"api/v1/periods/{test_period.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(test_period.id)


@pytest.mark.asyncio
async def test_update_period(user_client: AsyncClient, a_period, faker):
    user_client, user = user_client
    update_data = {"notes": faker.text(max_nb_chars=100)}
    period = await a_period(user)
    response = await user_client.patch(f"api/v1/periods/{period.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["notes"] == update_data["notes"]


@pytest.mark.asyncio
async def test_delete_period(user_client: AsyncClient, a_period):
    user_client, user = user_client
    period = await a_period(user)
    response = await user_client.delete(f"api/v1/periods/{period.id}")
    assert response.status_code == 204
