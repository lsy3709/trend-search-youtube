from services.base_service import BaseSocialMediaService


class Dummy(BaseSocialMediaService):
    async def get_trending_videos(self, max_results: int = 25, **kwargs):
        return []

    async def search_videos(self, query: str, max_results: int = 25, **kwargs):
        return []

    async def get_trending_hashtags(self, max_results: int = 20):
        return []


def test_text_utils_and_numbers():
    d = Dummy("dummy")
    assert d.truncate_text("abc", 5) == "abc"
    assert d.truncate_text("abcdef", 5) == "ab..."
    assert d.safe_int("10") == 10
    assert d.safe_int(None) is None
    assert d.safe_float("1.5") == 1.5
    assert d.safe_float(None) is None
    assert d.extract_hashtags("#Hi #hello world") == ["#hi", "#hello"]


