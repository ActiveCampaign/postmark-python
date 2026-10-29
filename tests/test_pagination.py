"""Tests for postmark.utils.pagination.paginate."""

import pytest

from postmark.models.page import Page
from postmark.utils.pagination import paginate


def _list_fn(total, calls):
    """A fake list endpoint over `total` integer records, recording its calls."""

    async def list_fn(count, offset, **filters):
        calls.append({"count": count, "offset": offset, **filters})
        items = list(range(offset, min(offset + count, total)))
        return Page(items=items, total=total)

    return list_fn


class TestPaginate:
    @pytest.mark.asyncio
    async def test_yields_everything_across_pages(self):
        calls = []

        got = [x async for x in paginate(_list_fn(5, calls), 100, 2)]

        assert got == [0, 1, 2, 3, 4]
        assert [c["offset"] for c in calls] == [0, 2, 4]

    @pytest.mark.asyncio
    async def test_stops_at_max_records(self):
        calls = []

        got = [x async for x in paginate(_list_fn(100, calls), 3, 2)]

        assert got == [0, 1, 2]
        # the last request only asks for what is still needed
        assert calls[-1]["count"] == 1

    @pytest.mark.asyncio
    async def test_batch_size_is_capped_at_500(self):
        calls = []

        _ = [x async for x in paginate(_list_fn(10, calls), 10, 9999)]

        assert calls[0]["count"] == 10  # min(500, remaining)
        big = []
        _ = [x async for x in paginate(_list_fn(2000, big), 1000, 9999)]
        assert big[0]["count"] == 500

    @pytest.mark.asyncio
    async def test_empty_page_stops_the_loop(self):
        calls = []

        got = [x async for x in paginate(_list_fn(0, calls), 100, 10)]

        assert got == []
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_page_that_comes_back_empty_early_stops_the_loop(self):
        """The reported total can overstate; an empty page must end the stream."""
        responses = [Page(items=[1, 2], total=10), Page(items=[], total=10)]

        async def list_fn(count, offset, **filters):
            return responses.pop(0)

        got = [x async for x in paginate(list_fn, 10, 2)]

        assert got == [1, 2]

    @pytest.mark.asyncio
    async def test_stops_once_offset_reaches_the_reported_total(self):
        calls = []

        got = [x async for x in paginate(_list_fn(4, calls), 100, 4)]

        assert got == [0, 1, 2, 3]
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_filters_are_forwarded(self):
        calls = []

        _ = [x async for x in paginate(_list_fn(1, calls), 10, 5, tag="promo")]

        assert calls[0]["tag"] == "promo"

    @pytest.mark.asyncio
    async def test_max_records_over_10000_is_rejected(self):
        with pytest.raises(ValueError, match="cannot exceed 10000"):
            _ = [x async for x in paginate(_list_fn(1, []), 10_001, 100)]
