from dataclasses import dataclass
from typing import Generic, List, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    """
    A single page of results from a paginated list endpoint.

    Attributes:
        items: The list of results for this page.
        total: The total number of records matching the query (across all pages).
    """

    items: List[T]
    total: int
