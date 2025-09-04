import types
import pytest
import httpx

from datetime import datetime


@pytest.mark.asyncio
async def test_analyze_success(monkeypatch):
    # 준비: app과 서비스 인스턴스 로드
    import main

    async def fake_analyze(req):
        # 한글: 최소 구조의 성공 응답
        return types.SimpleNamespace(
            rows=[
                types.SimpleNamespace(
                    channel_name="채널A",
                    title="제목A",
                    published_at=datetime.now(),
                    view_count=10000,
                    views_per_hour=500.0,
                    subscriber_count=2000,
                    view_to_subscriber_ratio=5.0,
                    duration="10:00",
                    video_url="https://youtube.com/watch?v=1",
                    thumbnail_url="https://i.ytimg.com/vi/1/hqdefault.jpg",
                )
            ],
            total=1,
            filtered=1,
            settings={},
        )

    monkeypatch.setattr(main.youtube_service, "analyze", fake_analyze)

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/youtube/analyze",
            json={
                "mode": "keyword",
                "keywords": ["인공지능"],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["filtered"] == 1 or data.get("rows") is not None


@pytest.mark.asyncio
async def test_analyze_export_success(monkeypatch):
    import main

    async def fake_analyze(req):
        return types.SimpleNamespace(
            rows=[
                types.SimpleNamespace(
                    channel_name="채널A",
                    title="제목A",
                    published_at=datetime.now(),
                    view_count=10000,
                    views_per_hour=500.0,
                    subscriber_count=2000,
                    view_to_subscriber_ratio=5.0,
                    duration="10:00",
                    video_url="https://youtube.com/watch?v=1",
                    thumbnail_url="https://i.ytimg.com/vi/1/hqdefault.jpg",
                )
            ],
            total=1,
            filtered=1,
            settings={},
        )

    monkeypatch.setattr(main.youtube_service, "analyze", fake_analyze)

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/youtube/analyze/export",
            json={"mode": "keyword", "keywords": ["테스트"]},
        )
        assert r.status_code == 200
        assert r.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "attachment;" in r.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_analyze_failure_quota(monkeypatch):
    import main

    async def fail_analyze(req):
        raise Exception("quota exceeded")

    monkeypatch.setattr(main.youtube_service, "analyze", fail_analyze)

    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/youtube/analyze",
            json={"mode": "keyword", "keywords": ["테스트"]},
        )
        assert r.status_code == 500


