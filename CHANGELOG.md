# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.2.0] - 2026-03-06

### Added
- `User-Agent` header sent on every request in the format `Postmark.PY - {version} (Python/{major}.{minor}.{micro})`.
- `X-Request-Id` from Postmark responses is now stored as `request_id` on all `PostmarkAPIException` subclasses and included in the exception `__str__` output when present — enabling direct support escalations.
- `request_id` included in structured log records for both successful requests and API errors.
- Structured `extra={}` fields on all log calls (`method`, `endpoint`, `status_code`, `duration_ms`, `error_code`, `postmark_message`, `request_id`) for compatibility with Datadog, Splunk, and other log aggregators.
- `duration_ms` timing on every request log record (success, error, and timeout).

### Changed
- Upgraded `pytest-asyncio` to `^1.0.0` and set `asyncio_mode = "auto"` to eliminate deprecation warnings on Python 3.12+.

---

## [0.1.0] - 2026-03-05

### Added
- Initial release of the SDK.
- `ServerClient` and `AccountClient` with authentication, configurable retries, timeout, and optional `base_url` override for local mock servers.
- Managers for outbound/inbound messages, bounces, templates, streams, suppressions, webhooks, stats, domains, sender signatures, and data removals.
- Async pagination via `paginate()` utility; `stream()` methods on `OutboundManager` and `BounceManager`.
- Typed request/response models backed by Pydantic v2.
- Pytest test suite.
