# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Django email backend (`postmark.django.EmailBackend`), gated behind the new `django` extra (`pip install postmark-python[django]`). Supports Django 4.2 LTS, 5.2 LTS, 6.0, and 6.1 — including Django 6.0's ["modern email API" change](https://docs.djangoproject.com/en/6.0/releases/6.0/#adoption-of-python-s-modern-email-api). The Postmark payload is built from `EmailMessage`'s high-level attributes rather than `EmailMessage.message()`, so this backend is unaffected by that change.
  - `postmark.django.PostmarkEmailMessage` / `PostmarkEmailMultiAlternatives` / `PostmarkEmailMixin` for setting `tag`, `metadata`, and `message_stream`.
  - `postmark.django.pre_send` / `post_send` / `on_exception` signals.
  - New settings: `POSTMARK_SERVER_TOKEN`, `POSTMARK_TEST_MODE`, `POSTMARK_TRACK_OPENS`, `POSTMARK_MESSAGE_STREAM`.
  - See the [Django Backend wiki page](https://github.com/ActiveCampaign/postmark-python/wiki/Django-Backend) and `examples/django/`.

---

## [0.3.7] - 2026-08-05

### Fixed

- `InactiveRecipientException` no longer truncates inactive email addresses at the first `.` in the domain (e.g. `john@example.com` was truncated to `john@example`). Handles single and multiple inactive recipients correctly. (Thanks, [@bharara](https://github.com/bharara).)

### Changed

- Updated `pytest` to `9.1.1`, addressing PYSEC-2026-1845 (local privilege escalation via a temp-directory race condition).
- Updated `respx` test dependency constraint and lockfile.
- Updated dev tooling: `mypy`, `ruff`, and `pre-commit`; reformatted README code examples for the `ruff` 0.16 formatter.
- CI: updated `actions/setup-python` to `v7` and `github/codeql-action` to `4.37.4`.
- CI: free disk space before CodeQL scans to prevent runner out-of-disk failures.

---

## [0.3.6] - 2026-07-10

### Added

- Security hardening for the repository and release pipeline:
  - **Dependabot** (`.github/dependabot.yml`): weekly automated PRs for Python dependency and GitHub Actions updates; minor and patch updates grouped to reduce noise.
  - **CodeQL** (`.github/workflows/codeql.yml`): SAST scanning on every push, PR, and weekly schedule; results surface in the GitHub Security tab.
  - **Dependency vulnerability scanning** (`.github/workflows/security.yml`): `pip-audit` checks all locked dependencies against OSV/PyPI advisory databases on push, PR, and weekly.
  - **Publish gate** (`publish.yml`): `pip-audit` now runs before every PyPI release; a known-vulnerable dependency blocks the publish job.
  - **Secret detection** (`.pre-commit-config.yaml`): `detect-secrets` pre-commit hook blocks commits containing hard-coded credentials.
  - **`SECURITY.md`**: published security policy with private vulnerability reporting instructions and scope definition.
- Updated `idna` (transitive dependency via `httpx`) from 3.11 to 3.18 to address PYSEC-2026-215, a DoS vulnerability in `idna.encode()` for arbitrarily large inputs.

---

## [0.3.5] - 2026-07-07

### Changed

- Modernized type hints to Python 3.10+ syntax throughout: `Optional[X]` to `X | None`, `Union[X, Y]` to `X | Y`, `List[X]` to `list[X]`, `Dict[K, V]` to `dict[K, V]`. `AsyncGenerator`, `Callable`, and `Awaitable` moved from `typing` to `collections.abc`. No functional changes.
- Added `target-version = "py310"` and the `UP` ruleset to ruff config, enforcing the modernized syntax going forward.

---

## [0.3.4] - 2026-06-29

### Changed

- Migrated `pyproject.toml` package metadata from the legacy `[tool.poetry]` table to the PEP 621 `[project]` table. No functional changes — dependency version constraints are semantically equivalent, `[tool.poetry]` is retained only for the Poetry-specific `packages` directive, and the build-system pin is now explicit (`poetry-core>=2.4.0,<3.0.0`).

---

## [0.3.3] - 2026-06-24

### Added

- `postmark/py.typed` marker (PEP 561): type checkers (mypy, pyright, Pylance) in downstream projects now pick up the package's inline annotations. The annotations were already present; the missing marker caused conformant checkers to ignore them.

### Changed

- Trove classifiers synced with CI: added `Programming Language :: Python :: 3.13`, `Programming Language :: Python :: 3.14`, and `Typing :: Typed`.

---

## [0.3.2] - 2026-06-15
### Changed
- Updated dev tooling: mypy 2.x, ruff 0.15.x, Poetry 2.4.1, and pre-commit hooks

---

## [0.3.1] - 2026-06-12

### Fixed

- `postmark.sync`: Gunicorn and Odoo devs, rejoice! ...the module-level event loop thread is now fork-safe. Previously, importing `postmark.sync` before a process fork caused child processes to inherit a stale event loop with no running thread, causing all sync API calls to hang indefinitely. The loop and thread are now created lazily on first use and recreated automatically when a PID change is detected. (Good eye, [@yibudak](https://github.com/yibudak).)

---

## [0.3.0] - 2026-06-08

### Added

- `SyncServerClient` and `SyncAccountClient` — synchronous wrappers around the async clients, backed by a single daemon thread with a persistent asyncio event loop. Enables SDK use in scripts, Flask apps, and Jupyter notebooks without `async`/`await`. HTTP connection pooling is retained across calls for performance.
- Examples reorganized into `examples/async/` and `examples/sync/` directories with parallel coverage, plus two new sync-only examples (`send_sync_simple.py`, `send_sync_batch.py`).
- 31 new tests for sync client behavior (`tests/test_sync_client.py`).

---

## [0.2.5] - 2026-06-04

### Changed

- Upgraded `httpx` dependency to `0.28.1`.
- CI: expanded test matrix to include Python 3.13 and 3.14.
- CI: updated GitHub Actions to `actions/checkout@v6`, `actions/setup-python@v6`, `actions/cache@v5`, and Poetry `2.3.4`.

---

## [0.2.4] - 2026-04-15

### Fixed

- README: logo image now uses an absolute raw GitHub URL so it renders correctly on the PyPI project page.

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
