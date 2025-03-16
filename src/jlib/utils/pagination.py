from jlib.schemas.pagination import PaginationSchema
from settings import settings


def get_default_pagination() -> PaginationSchema:
    return PaginationSchema(offset=0, limit=settings.page_size)


def check_pagination(pagination: PaginationSchema) -> None:
    if pagination.limit is None or pagination.limit > settings.max_query_limit:
        pagination.limit = settings.max_query_limit
