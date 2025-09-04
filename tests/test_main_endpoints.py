import pytest
import httpx


@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_root_redirects_to_web():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", follow_redirects=False) as client:
        r = await client.get("/")
        assert 300 <= r.status_code < 400

