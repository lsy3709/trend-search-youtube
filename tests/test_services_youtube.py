import os
import pytest

from services.youtube_service import YouTubeService


@pytest.mark.asyncio
async def test_youtube_search_smoke():
    svc = YouTubeService()
    if not os.getenv("YOUTUBE_API_KEY"):
        pytest.skip("YOUTUBE_API_KEY not set; skipping live API test")
    results = await svc.search_videos("인공지능", max_results=1)
    assert isinstance(results, list)
    assert len(results) <= 1


@pytest.mark.asyncio
async def test_duration_utils():
    svc = YouTubeService()
    # ISO8601 -> readable string 변환 검사
    assert svc.parse_duration("PT1H2M3S") == "1:02:03"
    assert svc.parse_duration("PT2M5S") == "2:05"

