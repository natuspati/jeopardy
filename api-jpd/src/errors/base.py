from fastapi import status


class BaseError(Exception):
    detail: str = "Internal service error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers: dict = {}  # noqa: RUF012 - sub-classes can override, not a class variable

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.detail = detail or self.detail
        self.status_code = status_code or self.status_code
        self.headers = headers or self.headers
        super().__init__(self.detail)

    def __str__(self):
        return f"{self.detail} (status_code={self.status_code})"
