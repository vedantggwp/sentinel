import pytest

from sentinel.config import settings


@pytest.fixture(autouse=True)
def disable_live_tavily_by_default(monkeypatch):
    monkeypatch.setattr(settings, "tavily_api_key", "")
