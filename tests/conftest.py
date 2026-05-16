import pytest
import httpx
from rankparse import RankParseClient, AsyncRankParseClient

API_KEY = "rp_test1234567890"
BASE_URL = "https://api.rankparse.com/v1"


@pytest.fixture
def client():
    return RankParseClient(api_key=API_KEY, base_url=BASE_URL)


@pytest.fixture
def async_client():
    return AsyncRankParseClient(api_key=API_KEY, base_url=BASE_URL)


def make_success_response(data: dict) -> dict:
    return {"data": data, "credits_used": 1, "credits_remaining": 999, "domain": "example.com"}


def make_error_response(status: int, code: str, message: str) -> httpx.Response:
    return httpx.Response(status, json={"error": "Error", "code": code, "message": message})
