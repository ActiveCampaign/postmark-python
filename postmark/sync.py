"""
postmark.sync — synchronous wrapper around the async Postmark clients.

Runs all API calls on a background event loop thread, blocking until each
call completes. Works in plain scripts, Flask apps, and Jupyter notebooks
(where asyncio.run() would fail with RuntimeError).

Example::

    import postmark.sync

    with postmark.sync.ServerClient(token) as client:
        response = client.outbound.send({
            "sender": "you@example.com",
            "to": "recipient@example.com",
            "subject": "Hello",
            "text_body": "Hello from postmark.sync!",
        })
        print(response.message_id)
"""

import asyncio
import inspect
import os
import threading

from postmark.clients.account_client import AccountClient as _AsyncAccountClient
from postmark.clients.server_client import ServerClient as _AsyncServerClient


class _EventLoopThread:
    """Persistent background thread running a dedicated event loop."""

    def __init__(self):
        self._lock = threading.Lock()
        self._loop = None
        self._thread = None
        self._pid = None

    def _ensure_started(self):
        current_pid = os.getpid()
        with self._lock:
            if (
                self._pid == current_pid
                and self._loop is not None
                and not self._loop.is_closed()
                and self._thread is not None
                and self._thread.is_alive()
            ):
                return

            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._thread.start()
            self._pid = current_pid

    def run(self, coro):
        """Submit a coroutine and block the calling thread until it returns or raises."""
        self._ensure_started()
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()


_loop = _EventLoopThread()


class _SyncProxy:
    """
    Wraps an async manager, exposing coroutine methods as regular blocking calls.

    AsyncGenerator methods are collected into a list on the background thread
    (all pages fetched upfront) and returned synchronously.
    Non-async attributes are passed through unchanged.
    """

    def __init__(self, async_manager):
        self._async = async_manager

    def __getattr__(self, name):
        attr = getattr(self._async, name)
        if inspect.isasyncgenfunction(attr):

            def sync_collect(*args, **kwargs):
                async def _collect():
                    return [item async for item in attr(*args, **kwargs)]

                return _loop.run(_collect())

            return sync_collect
        if inspect.iscoroutinefunction(attr):

            def sync_method(*args, **kwargs):
                return _loop.run(attr(*args, **kwargs))

            return sync_method
        return attr


class SyncServerClient:
    """
    Synchronous wrapper around ServerClient.

    All async manager methods are available as regular blocking calls.
    Use as a context manager (recommended) or call .close() explicitly.

    Example::

        with postmark.sync.ServerClient(os.environ["POSTMARK_SERVER_TOKEN"]) as client:
            response = client.outbound.send({
                "sender": "you@example.com",
                "to": "recipient@example.com",
                "subject": "Hello",
                "text_body": "Hello from postmark.sync!",
            })
            print(response.message_id)
    """

    _SERVER_MANAGERS = [
        "outbound",
        "inbound",
        "inbound_rules",
        "bounces",
        "templates",
        "server",
        "stream",
        "stats",
        "webhooks",
        "suppressions",
    ]

    def __init__(
        self,
        server_token: str,
        retries: int = 3,
        timeout: float = 5.0,
        base_url: str | None = None,
    ):
        self._async = _AsyncServerClient(
            server_token, retries=retries, timeout=timeout, base_url=base_url
        )
        for name in self._SERVER_MANAGERS:
            setattr(self, name, _SyncProxy(getattr(self._async, name)))

    def close(self):
        """Close the underlying HTTP connection pool."""
        _loop.run(self._async.close())

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


ServerClient = SyncServerClient


class SyncAccountClient:
    """
    Synchronous wrapper around AccountClient.

    All async manager methods are available as regular blocking calls.
    Use as a context manager (recommended) or call .close() explicitly.

    Example::

        with postmark.sync.AccountClient(os.environ["POSTMARK_ACCOUNT_TOKEN"]) as client:
            domains = client.domain.list()
            for domain in domains.domains:
                print(domain.name)
    """

    _ACCOUNT_MANAGERS = [
        "server",
        "domain",
        "signature",
        "data_removals",
        "templates",
    ]

    def __init__(
        self,
        account_token: str,
        retries: int = 3,
        timeout: float = 30.0,
        base_url: str | None = None,
    ):
        self._async = _AsyncAccountClient(
            account_token, retries=retries, timeout=timeout, base_url=base_url
        )
        for name in self._ACCOUNT_MANAGERS:
            setattr(self, name, _SyncProxy(getattr(self._async, name)))

    def close(self):
        """Close the underlying HTTP connection pool."""
        _loop.run(self._async.close())

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


AccountClient = SyncAccountClient
