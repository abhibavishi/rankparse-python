import pytest
import respx
import httpx
from rankparse import AsyncRankParseClient
from rankparse.errors import AuthError, InsufficientCreditsError, NotFoundError, RateLimitError, APIError

API_KEY = "rp_test1234567890"
BASE_URL = "https://api.rankparse.com/v1"


@pytest.fixture
def async_client():
    return AsyncRankParseClient(api_key=API_KEY, base_url=BASE_URL)


class TestAuth:
    @pytest.mark.asyncio
    @respx.mock
    async def test_sends_api_key_header(self, async_client):
        route = respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                200, json={"data": {"score": 50}, "credits_used": 1, "credits_remaining": 999}
            )
        )
        await async_client.domain_authority("example.com")
        assert route.called
        assert route.calls[0].request.headers["x-api-key"] == API_KEY


class TestErrorMapping:
    @pytest.mark.asyncio
    @respx.mock
    async def test_401_raises_auth_error(self, async_client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                401, json={"error": "Unauthorized", "code": "invalid_key", "message": "Invalid API key"}
            )
        )
        with pytest.raises(AuthError):
            await async_client.domain_authority("example.com")

    @pytest.mark.asyncio
    @respx.mock
    async def test_402(self, async_client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(402, json={"error": "E", "code": "c", "message": "m"})
        )
        with pytest.raises(InsufficientCreditsError):
            await async_client.domain_authority("example.com")

    @pytest.mark.asyncio
    @respx.mock
    async def test_404(self, async_client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(404, json={"error": "E", "code": "c", "message": "m"})
        )
        with pytest.raises(NotFoundError):
            await async_client.domain_authority("example.com")

    @pytest.mark.asyncio
    @respx.mock
    async def test_429(self, async_client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(429, json={"error": "E", "code": "c", "message": "m"})
        )
        with pytest.raises(RateLimitError):
            await async_client.domain_authority("example.com")

    @pytest.mark.asyncio
    @respx.mock
    async def test_500(self, async_client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(500, json={"error": "E", "code": "c", "message": "m"})
        )
        with pytest.raises(APIError):
            await async_client.domain_authority("example.com")


class TestParamSerialization:
    @pytest.mark.asyncio
    @respx.mock
    async def test_domain_overlap_comma_joined(self, async_client):
        route = respx.get(f"{BASE_URL}/domain-overlap").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 5, "credits_remaining": 995}
            )
        )
        await async_client.domain_overlap(["a.com", "b.com"])
        assert "domains=" in str(route.calls[0].request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_none_params_omitted(self, async_client):
        route = respx.get(f"{BASE_URL}/backlinks").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 2, "credits_remaining": 998}
            )
        )
        await async_client.backlinks("example.com")
        assert "from_domain" not in str(route.calls[0].request.url)
        assert "link_type" not in str(route.calls[0].request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_backlinks_params(self, async_client):
        route = respx.get(f"{BASE_URL}/backlinks").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 2, "credits_remaining": 998}
            )
        )
        await async_client.backlinks("github.com", limit=25, offset=50)
        url_str = str(route.calls[0].request.url)
        assert "limit=25" in url_str
        assert "offset=50" in url_str


class TestMethods:
    @pytest.mark.asyncio
    @respx.mock
    async def test_batch_sends_post(self, async_client):
        route = respx.post(f"{BASE_URL}/batch").mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        await async_client.batch([{"endpoint": "domain-authority", "domain": "example.com"}])
        assert route.calls[0].request.method == "POST"

    @pytest.mark.asyncio
    @respx.mock
    async def test_revoke_key_sends_delete(self, async_client):
        route = respx.delete(f"{BASE_URL}/keys/abc123").mock(
            return_value=httpx.Response(204)
        )
        await async_client.revoke_key("abc123")
        assert route.calls[0].request.method == "DELETE"

    @pytest.mark.asyncio
    @respx.mock
    async def test_keys_unwraps_envelope(self, async_client):
        respx.get(f"{BASE_URL}/keys").mock(
            return_value=httpx.Response(
                200, json={"keys": [{"id": "k1", "name": "Default"}]}
            )
        )
        result = await async_client.keys()
        assert isinstance(result, list)
        assert result[0]["id"] == "k1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_context_manager(self):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                200, json={"data": {"score": 42}, "credits_used": 1, "credits_remaining": 99}
            )
        )
        async with AsyncRankParseClient(api_key=API_KEY, base_url=BASE_URL) as c:
            result = await c.domain_authority("example.com")
        assert result["data"]["score"] == 42
