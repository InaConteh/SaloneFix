"""Offset pagination for list endpoints.

Bodies stay plain arrays (the frontend and tests depend on that); the total
number of matching rows is returned in the ``X-Total-Count`` header.
"""
from dataclasses import dataclass
from fastapi import Query, Response
from sqlalchemy.orm import Query as SAQuery

MAX_LIMIT = 100


@dataclass
class PageParams:
    limit: int
    offset: int


def page_params(
    limit: int = Query(50, ge=1, le=MAX_LIMIT, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Rows to skip"),
) -> PageParams:
    return PageParams(limit=limit, offset=offset)


def paginate(query: SAQuery, page: PageParams, response: Response) -> list:
    total = query.order_by(None).count()
    response.headers["X-Total-Count"] = str(total)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count, X-Request-ID"
    return query.offset(page.offset).limit(page.limit).all()
