from typing import AsyncGenerator, Awaitable, Callable, TypeVar

from postmark.models.page import Page

T = TypeVar("T")

_MAX_OFFSET = 10_000
_MAX_BATCH = 500


async def paginate(
    list_fn: Callable[..., Awaitable[Page[T]]],
    max_records: int,
    batch_size: int,
    **filters,
) -> AsyncGenerator[T, None]:
    """Async generator that paginates through a list endpoint.

    Args:
        list_fn: Async callable matching ``list(count=..., offset=..., **filters)``.
        max_records: Hard cap on total yielded records (max 10,000).
        batch_size: Records to fetch per API call (max 500).
        **filters: Extra keyword arguments forwarded to ``list_fn``.
    """
    if max_records > _MAX_OFFSET:
        raise ValueError(f"max_records cannot exceed {_MAX_OFFSET}")

    batch_size = min(batch_size, _MAX_BATCH)
    offset = 0
    yielded = 0

    while yielded < max_records:
        remaining = max_records - yielded
        current_limit = min(batch_size, remaining)

        if offset + current_limit > _MAX_OFFSET:
            current_limit = _MAX_OFFSET - offset
            if current_limit <= 0:
                break

        page = await list_fn(count=current_limit, offset=offset, **filters)
        if not page.items:
            break

        for item in page.items:
            yield item
            yielded += 1
            if yielded >= max_records:
                return

        offset += len(page.items)
        if offset >= page.total:
            break
