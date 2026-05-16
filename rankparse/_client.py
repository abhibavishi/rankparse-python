import httpx
from .errors import RankParseError, AuthError, InsufficientCreditsError, NotFoundError, RateLimitError, APIError

DEFAULT_BASE_URL = "https://api.rankparse.com/v1"


class BaseClient:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _build_params(self, **kwargs) -> dict:
        """Strip None values; convert lists to comma-separated strings."""
        result = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, list):
                result[key] = ",".join(str(v) for v in value)
            else:
                result[key] = value
        return result

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Map HTTP status codes to typed exceptions."""
        if response.is_success:
            return
        try:
            body = response.json()
            message = body.get("message", response.text)
            code = body.get("code", "unknown_error")
        except Exception:
            message = response.text
            code = "unknown_error"

        status = response.status_code
        if status == 401:
            raise AuthError(message, code)
        elif status == 402:
            raise InsufficientCreditsError(message, code)
        elif status == 404:
            raise NotFoundError(message, code)
        elif status == 429:
            raise RateLimitError(message, code)
        else:
            raise APIError(message, code, status)

    def _make_headers(self) -> dict:
        return {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
