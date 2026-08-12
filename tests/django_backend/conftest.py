"""Shared fixtures for the Django backend test suite."""

from datetime import datetime

import django
import pytest
from django.conf import settings

if not settings.configured:
    settings.configure(
        USE_TZ=True,
        DEFAULT_CHARSET="utf-8",
        EMAIL_BACKEND="postmark.django.EmailBackend",
        POSTMARK_SERVER_TOKEN="test-token",
    )
    django.setup()

import postmark.django.backend as backend_module  # noqa: E402
from postmark import SendResponse  # noqa: E402


def _default_response(index: int, to: str) -> SendResponse:
    return SendResponse(
        To=to,
        SubmittedAt=datetime(2024, 1, 1),
        MessageID=f"id-{index}",
        ErrorCode=0,
        Message="OK",
    )


class FakeOutbound:
    """Stands in for postmark.sync.ServerClient(...).outbound."""

    def __init__(self):
        self.calls: list[list] = []
        self.responses_queue: list[list[SendResponse]] = []

    def send_batch(self, messages):
        self.calls.append(messages)
        if self.responses_queue:
            return self.responses_queue.pop(0)
        return [_default_response(i, m.to) for i, m in enumerate(messages)]


class FakeSyncClient:
    """Stands in for postmark.sync.ServerClient."""

    def __init__(self):
        self.closed = False
        self.outbound = FakeOutbound()

    def close(self):
        self.closed = True


class RecordingFactory:
    """Replaces backend_module.SyncServerClient; records constructor args."""

    def __init__(self, instance: FakeSyncClient):
        self.instance = instance
        self.calls: list[tuple] = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.instance


@pytest.fixture
def fake_sync_client():
    return FakeSyncClient()


@pytest.fixture
def sync_client_factory(monkeypatch, fake_sync_client):
    factory = RecordingFactory(fake_sync_client)
    monkeypatch.setattr(backend_module, "SyncServerClient", factory)
    return factory
