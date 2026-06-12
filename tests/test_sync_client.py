"""Tests for postmark.sync — synchronous wrapper around the async clients."""

import os
import select
import signal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import postmark.sync
from postmark.sync import (
    SyncAccountClient,
    SyncServerClient,
    _EventLoopThread,
    _SyncProxy,
)


class TestEventLoopThread:
    def test_run_coroutine_returns_value(self):
        loop = _EventLoopThread()

        async def add(a, b):
            return a + b

        assert loop.run(add(2, 3)) == 5

    def test_run_coroutine_propagates_exception(self):
        loop = _EventLoopThread()

        async def boom():
            raise ValueError("oops")

        with pytest.raises(ValueError, match="oops"):
            loop.run(boom())

    def test_multiple_calls_on_same_loop(self):
        loop = _EventLoopThread()

        async def identity(x):
            return x

        results = [loop.run(identity(i)) for i in range(5)]
        assert results == list(range(5))


class TestSyncProxy:
    def test_wraps_coroutine_as_sync(self):
        class AsyncThing:
            async def compute(self, x):
                return x * 2

        proxy = _SyncProxy(AsyncThing())
        assert proxy.compute(5) == 10

    def test_wraps_coroutine_with_kwargs(self):
        class AsyncThing:
            async def greet(self, name="world"):
                return f"hello {name}"

        proxy = _SyncProxy(AsyncThing())
        assert proxy.greet(name="postmark") == "hello postmark"

    def test_passthrough_plain_method(self):
        class AsyncThing:
            def plain(self):
                return "sync"

        proxy = _SyncProxy(AsyncThing())
        assert proxy.plain() == "sync"

    def test_passthrough_plain_attribute(self):
        class AsyncThing:
            value = 42

        proxy = _SyncProxy(AsyncThing())
        assert proxy.value == 42

    def test_async_generator_returns_list(self):
        class AsyncThing:
            async def stream(self):
                yield 1
                yield 2
                yield 3

        proxy = _SyncProxy(AsyncThing())
        result = proxy.stream()
        assert result == [1, 2, 3]

    def test_async_generator_respects_kwargs(self):
        class AsyncThing:
            async def stream(self, limit=10):
                for i in range(limit):
                    yield i

        proxy = _SyncProxy(AsyncThing())
        result = proxy.stream(limit=2)
        assert result == [0, 1]

    def test_missing_attribute_raises_attribute_error(self):
        class AsyncThing:
            pass

        proxy = _SyncProxy(AsyncThing())
        with pytest.raises(AttributeError):
            _ = proxy.nonexistent

    def test_coroutine_exception_propagates(self):
        class AsyncThing:
            async def fail(self):
                raise RuntimeError("network error")

        proxy = _SyncProxy(AsyncThing())
        with pytest.raises(RuntimeError, match="network error"):
            proxy.fail()


@pytest.fixture
def patched_httpx():
    """Prevent real httpx.AsyncClient creation during client instantiation."""
    with patch("httpx.AsyncClient") as mock_httpx:
        mock_httpx.return_value = MagicMock()
        yield mock_httpx


class TestSyncServerClient:
    def test_instantiates_with_valid_token(self, patched_httpx):
        client = SyncServerClient("test-token")
        assert client._async.server_token == "test-token"

    def test_accepts_all_constructor_kwargs(self, patched_httpx):
        client = SyncServerClient(
            "tok", retries=1, timeout=10.0, base_url="http://mock"
        )
        assert client._async.retries == 1
        assert client._async.timeout == 10.0

    def test_has_all_manager_proxies(self, patched_httpx):
        client = SyncServerClient("test-token")
        for name in SyncServerClient._SERVER_MANAGERS:
            proxy = getattr(client, name)
            assert isinstance(proxy, _SyncProxy), f"expected _SyncProxy for '{name}'"

    def test_context_manager_calls_close(self, patched_httpx):
        with patch.object(SyncServerClient, "close") as mock_close:
            with SyncServerClient("test-token"):
                pass
            mock_close.assert_called_once()

    def test_context_manager_calls_close_on_exception(self, patched_httpx):
        with patch.object(SyncServerClient, "close") as mock_close:
            with pytest.raises(ValueError):
                with SyncServerClient("test-token"):
                    raise ValueError("boom")
            mock_close.assert_called_once()

    def test_send_proxies_to_async_send(self, patched_httpx):
        expected = MagicMock()
        async_send = AsyncMock(return_value=expected)

        client = SyncServerClient("test-token")
        client.outbound._async.send = async_send

        result = client.outbound.send(
            {"sender": "a@b.com", "to": "c@d.com", "subject": "hi", "text_body": "hi"}
        )

        assert result is expected
        async_send.assert_called_once()

    def test_send_batch_proxies_to_async(self, patched_httpx):
        expected = [MagicMock(), MagicMock()]
        async_send_batch = AsyncMock(return_value=expected)

        client = SyncServerClient("test-token")
        client.outbound._async.send_batch = async_send_batch

        result = client.outbound.send_batch([])
        assert result is expected

    def test_stream_returns_list(self, patched_httpx):
        async def fake_stream():
            yield "a"
            yield "b"

        client = SyncServerClient("test-token")
        client.outbound._async.stream = fake_stream
        result = client.outbound.stream()
        assert result == ["a", "b"]

    def test_invalid_empty_token_raises(self, patched_httpx):
        from postmark.exceptions import PostmarkException

        with pytest.raises(PostmarkException):
            SyncServerClient("")

    def test_negative_retries_raises(self, patched_httpx):
        from postmark.exceptions import PostmarkException

        with pytest.raises(PostmarkException):
            SyncServerClient("tok", retries=-1)

    def test_zero_timeout_raises(self, patched_httpx):
        from postmark.exceptions import PostmarkException

        with pytest.raises(PostmarkException):
            SyncServerClient("tok", timeout=0)


class TestSyncAccountClient:
    def test_instantiates_with_valid_token(self, patched_httpx):
        client = SyncAccountClient("test-token")
        assert client._async.account_token == "test-token"

    def test_accepts_all_constructor_kwargs(self, patched_httpx):
        client = SyncAccountClient(
            "tok", retries=0, timeout=60.0, base_url="http://mock"
        )
        assert client._async.retries == 0
        assert client._async.timeout == 60.0

    def test_has_all_manager_proxies(self, patched_httpx):
        client = SyncAccountClient("test-token")
        for name in SyncAccountClient._ACCOUNT_MANAGERS:
            proxy = getattr(client, name)
            assert isinstance(proxy, _SyncProxy), f"expected _SyncProxy for '{name}'"

    def test_context_manager_calls_close(self, patched_httpx):
        with patch.object(SyncAccountClient, "close") as mock_close:
            with SyncAccountClient("test-token"):
                pass
            mock_close.assert_called_once()

    def test_domain_list_proxies_to_async(self, patched_httpx):
        expected = MagicMock()
        async_list = AsyncMock(return_value=expected)

        client = SyncAccountClient("test-token")
        client.domain._async.list = async_list

        result = client.domain.list()
        assert result is expected
        async_list.assert_called_once()

    def test_invalid_empty_token_raises(self, patched_httpx):
        from postmark.exceptions import PostmarkException

        with pytest.raises(PostmarkException):
            SyncAccountClient("")

    def test_negative_retries_raises(self, patched_httpx):
        from postmark.exceptions import PostmarkException

        with pytest.raises(PostmarkException):
            SyncAccountClient("tok", retries=-1)


class TestModuleLevelLoop:
    def test_module_loop_is_shared(self):
        assert postmark.sync._loop is postmark.sync._loop

    def test_module_loop_can_run_coroutines(self):
        async def echo(x):
            return x

        result = postmark.sync._loop.run(echo("hello"))
        assert result == "hello"

    @pytest.mark.skipif(not hasattr(os, "fork"), reason="requires os.fork")
    def test_module_loop_recovers_after_fork(self):
        async def echo(value):
            return value

        assert postmark.sync._loop.run(echo("parent")) == "parent"

        read_fd, write_fd = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(read_fd)
            try:
                result = postmark.sync._loop.run(echo("child"))
                stored_pid = postmark.sync._loop._pid
                payload = f"{result},{stored_pid},{os.getpid()}"
                os.write(write_fd, payload.encode())
            except Exception as exc:
                os.write(write_fd, f"ERROR:{exc}".encode())
            finally:
                os.close(write_fd)
            os._exit(0)

        os.close(write_fd)
        try:
            ready, _, _ = select.select([read_fd], [], [], 2)
            if not ready:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
                pytest.fail("module event loop hung after fork")

            payload = os.read(read_fd, 1024).decode()
            _, status = os.waitpid(pid, 0)
        finally:
            os.close(read_fd)

        assert status == 0
        result, stored_pid_str, child_pid_str = payload.split(",")
        assert result == "child"
        assert int(stored_pid_str) == int(child_pid_str)
        assert int(child_pid_str) == pid
