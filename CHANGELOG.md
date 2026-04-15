# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.2.3] - 2026-04-14

### Fixed

- `__version__` resolves from the **`postmark-python`** distribution metadata so `X-Postmark-Client-Version` matches after `pip install postmark-python` (falls back to `0.0.0` when not installed as a package).

### Changed

- **`poetry.lock`** is tracked in version control again (removed from `.gitignore`) for reproducible installs and CI cache keys.
- README: removed the misleading note about a future PyPI distribution under the name `postmark`.

---

## [0.2.2] - 2026-04-14

### Fixed

- Timeout error message now uses the client’s configured timeout with clearer numeric formatting (`:g`), for both `ServerClient` and `AccountClient`.
- Postmark API `ErrorCode` values from JSON are coerced to `int` when sent as numeric strings; invalid values and booleans map to `None` so exception mapping stays reliable.
- README quick start no longer imports `python-dotenv` (a dev-only dependency); optional `.env` loading is described in a comment instead.

---

## [0.2.1] - 2026-04-14

### Changed

- PyPI distribution renamed from `postmark` to **`postmark-python`** to avoid clashing with the unrelated [`postmark`](https://pypi.org/project/postmark/) package on PyPI. The import name remains `postmark`.
- Trove classifier updated from **Alpha** to **Beta** (`Development Status :: 4 - Beta`).

### Added

- Project URLs for PyPI metadata: repository, homepage ([official libraries](https://postmarkapp.com/developer/integration/official-libraries)), documentation (wiki), and Issues link.

---

## [0.2.0] - 2026-03-06

### Added
- Client identification on every request: `User-Agent` as `Python/{major}.{minor}.{micro}`, `X-Postmark-Client` as `postmark-python`, `X-Postmark-Client-Version` as the installed SDK version, and a fresh `X-Postmark-Correlation-Id` (UUID) per HTTP request.
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
