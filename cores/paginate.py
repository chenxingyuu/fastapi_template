from typing import Generic, List, Type, TypeVar

from fastapi import Query
from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel
from tortoise.queryset import QuerySet

T = TypeVar("T")


class PageModel(BaseModel, Generic[T]):
    list: List[T]
    total: int
    page: int
    limit: int


class PaginationParams(BaseModel):
    page: int = Query(1, alias="page", ge=1)
    limit: int = Query(10, alias="limit", ge=1)


async def paginate(query: QuerySet[T], pagination: PaginationParams, schema: Type[PydanticModel]) -> PageModel[T]:
    total = await query.count()
    items = await schema.from_queryset(query.offset((pagination.page - 1) * pagination.limit).limit(pagination.limit))
    return PageModel(list=items, total=total, page=pagination.page, limit=pagination.limit)
