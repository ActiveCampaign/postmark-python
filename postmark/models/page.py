from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """
    A single page of results from a paginated list endpoint.

    Attributes:
        items: The list of results for this page.
        total: The total number of records matching the query (across all pages).
    """

    items: list[T]
    total: int


@dataclass(frozen=True)
class CursorPage(Generic[T]):
    """
    A single page of results from a cursor-paginated list endpoint.

    Unlike :class:`Page`, these endpoints report no total, only an opaque cursor.

    Attributes:
        items: The list of results for this page.
        next_key: Opaque cursor for the next page, or ``None`` on the last page.
            Pass it back unchanged; Postmark rejects altered values.
    """

    items: list[T]
    next_key: str | None = None
