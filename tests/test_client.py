import pytest
import respx
import httpx
from rankparse import RankParseClient
from rankparse.errors import AuthError, InsufficientCreditsError, NotFoundError, RateLimitError, APIError

API_KEY = "rp_test1234567890"
BASE_URL = "https://api.rankparse.com/v1"


@pytest.fixture
def client():
    return RankParseClient(api_key=API_KEY, base_url=BASE_URL)


class TestAuth:
    @respx.mock
    def test_sends_api_key_header(self, client):
        route = respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(200, json={"data": {"score": 50}, "credits_used": 1, "credits_remaining": 999})
        )
        client.domain_authority("example.com")
        assert route.called
        assert route.calls[0].request.headers["x-api-key"] == API_KEY


class TestErrorMapping:
    @respx.mock
    def test_401_raises_auth_error(self, client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                401, json={"error": "Unauthorized", "code": "invalid_key", "message": "Invalid API key"}
            )
        )
        with pytest.raises(AuthError) as exc:
            client.domain_authority("example.com")
        assert exc.value.status == 401

    @respx.mock
    def test_402_raises_insufficient_credits(self, client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                402,
                json={"error": "Payment Required", "code": "insufficient_credits", "message": "No credits"},
            )
        )
        with pytest.raises(InsufficientCreditsError):
            client.domain_authority("example.com")

    @respx.mock
    def test_404_raises_not_found(self, client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                404, json={"error": "Not Found", "code": "not_found", "message": "Not found"}
            )
        )
        with pytest.raises(NotFoundError):
            client.domain_authority("example.com")

    @respx.mock
    def test_429_raises_rate_limit(self, client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                429,
                json={"error": "Too Many Requests", "code": "rate_limited", "message": "Rate limited"},
            )
        )
        with pytest.raises(RateLimitError):
            client.domain_authority("example.com")

    @respx.mock
    def test_500_raises_api_error(self, client):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                500, json={"error": "Server Error", "code": "internal_error", "message": "Internal error"}
            )
        )
        with pytest.raises(APIError) as exc:
            client.domain_authority("example.com")
        assert exc.value.status == 500


class TestParamSerialization:
    @respx.mock
    def test_backlinks_params(self, client):
        route = respx.get(f"{BASE_URL}/backlinks").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 2, "credits_remaining": 998}
            )
        )
        client.backlinks("github.com", limit=50, offset=100)
        request = route.calls[0].request
        assert "limit=50" in str(request.url)
        assert "offset=100" in str(request.url)
        assert "domain=github.com" in str(request.url)

    @respx.mock
    def test_domain_overlap_comma_joined(self, client):
        route = respx.get(f"{BASE_URL}/domain-overlap").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 5, "credits_remaining": 995}
            )
        )
        client.domain_overlap(["a.com", "b.com", "c.com"])
        request = route.calls[0].request
        url_str = str(request.url)
        assert "domains=a.com%2Cb.com%2Cc.com" in url_str or "domains=a.com,b.com,c.com" in url_str

    @respx.mock
    def test_link_intersect_two_params(self, client):
        route = respx.get(f"{BASE_URL}/link-intersect").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 5, "credits_remaining": 995}
            )
        )
        client.link_intersect("x.com", "y.com")
        request = route.calls[0].request
        assert "domain_a=x.com" in str(request.url)
        assert "domain_b=y.com" in str(request.url)

    @respx.mock
    def test_none_params_omitted(self, client):
        route = respx.get(f"{BASE_URL}/backlinks").mock(
            return_value=httpx.Response(
                200, json={"data": [], "credits_used": 2, "credits_remaining": 998}
            )
        )
        client.backlinks("example.com")  # from_domain=None, link_type=None
        request = route.calls[0].request
        assert "from_domain" not in str(request.url)
        assert "link_type" not in str(request.url)


class TestMethods:
    @respx.mock
    def test_batch_sends_post(self, client):
        route = respx.post(f"{BASE_URL}/batch").mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        client.batch([{"endpoint": "domain-authority", "domain": "example.com"}])
        assert route.calls[0].request.method == "POST"

    @respx.mock
    def test_revoke_key_sends_delete(self, client):
        route = respx.delete(f"{BASE_URL}/keys/abc123").mock(
            return_value=httpx.Response(204)
        )
        client.revoke_key("abc123")
        assert route.calls[0].request.method == "DELETE"

    @respx.mock
    def test_keys_unwraps_envelope(self, client):
        respx.get(f"{BASE_URL}/keys").mock(
            return_value=httpx.Response(
                200, json={"keys": [{"id": "k1", "name": "Default"}]}
            )
        )
        result = client.keys()
        assert isinstance(result, list)
        assert result[0]["id"] == "k1"

    @respx.mock
    def test_context_manager(self):
        respx.get(f"{BASE_URL}/domain-authority").mock(
            return_value=httpx.Response(
                200, json={"data": {"score": 42}, "credits_used": 1, "credits_remaining": 99}
            )
        )
        with RankParseClient(api_key=API_KEY, base_url=BASE_URL) as c:
            result = c.domain_authority("example.com")
        assert result["data"]["score"] == 42
