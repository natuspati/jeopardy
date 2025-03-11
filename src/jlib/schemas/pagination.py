from typing import Generic, Sequence

from jlib.schemas.base import BaseSchema
from jlib.types.schemas import T


class PaginatedResponseMeta(type):
    def __new__(mcs, name: str, bases, namespace: dict, **kwargs):
        if "items" not in namespace:
            namespace["items"] = []
        return super().__new__(mcs, name, bases, namespace)


class PaginationSchema(BaseSchema):
    offset: int = 0
    limit: int | None = None


class PaginatedResponseSchema(BaseSchema, Generic[T]):
    total: int
    offset: int
    limit: int
    items: Sequence[T]

    @classmethod
    def paginate(
        cls: "PaginatedResponseSchema[T]",
        items: Sequence[T],
        pagination: PaginationSchema,
    ) -> "PaginatedResponseSchema[T]":
        return cls(
            total=len(items),
            offset=pagination.offset,
            limit=pagination.limit,
            items=items[pagination.offset : pagination.offset + pagination.limit],
        )
