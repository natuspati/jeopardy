from jlib.schemas.pagination import PaginationSchema
from settings import settings


def get_default_pagination() -> PaginationSchema:
    return PaginationSchema(offset=0, limit=settings.page_size)
