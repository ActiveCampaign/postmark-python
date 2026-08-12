# Contributing

Thanks for considering a contribution to `postmark-python`.

## Getting started

```bash
git clone https://github.com/ActiveCampaign/postmark-python.git
cd postmark-python
poetry install
poetry run pre-commit install
```

## Making a change

1. Fork the repository and create a feature branch off `main`.
2. Make your change, keeping it scoped to a single concern.
3. Add or update tests under `tests/` — the suite follows a one-file-per-feature layout (e.g. `test_templates.py`, `test_bounces.py`) that mirrors `postmark/models/`.
4. Run the full check suite locally before opening a PR:

   ```bash
   poetry run pytest
   poetry run ruff check
   poetry run ruff format --check
   poetry run mypy postmark/
   poetry run pre-commit run --all-files
   ```

   CI enforces a minimum test coverage of 85% (`--cov-fail-under=85`), so new code needs tests to match.
5. Update `CHANGELOG.md` under an `Unreleased` heading (Keep a Changelog format).
6. Open a pull request describing the change and why it's needed.

## Reporting bugs and requesting features

Please open a [GitHub issue](https://github.com/ActiveCampaign/postmark-python/issues) using the appropriate template. For security vulnerabilities, follow the process in [SECURITY.md](SECURITY.md) instead of filing a public issue.

## Code style

- Formatting and linting are enforced by `ruff` (see `[tool.ruff]` in `pyproject.toml`).
- Type hints are required; `mypy postmark/` must pass cleanly.
- Request/response schemas use Pydantic v2 models under `postmark/models/<feature>/schemas.py`.
