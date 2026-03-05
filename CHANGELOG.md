# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-03-05

### Added
- Initial release of the SDK.
- `ServerClient` and `AccountClient` with authentication, configurable retries, timeout, and optional `base_url` override for local mock servers.
- Managers for outbound/inbound messages, bounces, templates, streams, suppressions, webhooks, stats, domains, sender signatures, and data removals.
- Async pagination via `paginate()` utility; `stream()` methods on `OutboundManager` and `BounceManager`.
- Typed request/response models backed by Pydantic v2.
- Pytest test suite.
