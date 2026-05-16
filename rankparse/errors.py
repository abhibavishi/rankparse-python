class RankParseError(Exception):
    def __init__(self, message: str, code: str, status: int) -> None:
        super().__init__(message)
        self.code = code
        self.status = status


class AuthError(RankParseError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message, code, 401)


class InsufficientCreditsError(RankParseError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message, code, 402)


class NotFoundError(RankParseError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message, code, 404)


class RateLimitError(RankParseError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message, code, 429)


class APIError(RankParseError):
    pass
