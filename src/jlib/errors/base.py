from fastapi import status


class BaseError(Exception):
    detail: str = "Error occurred"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.detail)

    def __str__(self):
        return self.detail


class BaseServiceError(BaseError):
    detail: str = "Internal service error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    ws_status_code = status.WS_1011_INTERNAL_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        ws_status_code: int | None = None,
    ):
        super().__init__(detail or self.detail)
        self.status_code = status_code or self.status_code
        self.ws_status_code = ws_status_code or self.ws_status_code

    def __str__(self):
        return f"{self.detail} (status_code={self.status_code})"
