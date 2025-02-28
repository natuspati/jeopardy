from jlib.schemas.base import BaseSchema


class PaginationSchema(BaseSchema):
    offset: int = 0
    limit: int | None = None
