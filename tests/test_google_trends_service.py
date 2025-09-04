import types
import pytest

from services.google_trends_service import GoogleTrendsService


@pytest.mark.asyncio
async def test_google_trends_dummy_on_error(monkeypatch):
    svc = GoogleTrendsService()

    class DummyPytrends:
        def trending_searches(self, pn=None, cat=None):
            raise RuntimeError("network error")

    monkeypatch.setattr(svc, "pytrends", DummyPytrends())
    res = await svc.get_realtime_trending_searches(region="KR")
    assert isinstance(res, list)
    assert len(res) > 0  # 더미가 반환됨


@pytest.mark.asyncio
async def test_google_trends_success_minimal(monkeypatch):
    svc = GoogleTrendsService()

    class OKPytrends:
        def trending_searches(self, pn=None, cat=None):
            # pandas DataFrame과 유사하게 [ [키워드1, 키워드2] ] 접근만 사용하므로 최소 동작 구현
            return [["키워드1", "키워드2"]]

    monkeypatch.setattr(svc, "pytrends", OKPytrends())
    res = await svc.get_realtime_trending_searches(region="KR")
    assert isinstance(res, list)
    assert res[0]["keyword"] == "키워드1"


