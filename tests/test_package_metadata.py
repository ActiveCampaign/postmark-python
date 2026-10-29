"""Tests for postmark/__init__.py version handling."""

import importlib
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import postmark


def test_version_comes_from_the_installed_metadata():
    assert postmark.__version__ != ""
    assert postmark.__version__ == importlib.metadata.version("postmark-python")


def test_version_falls_back_when_running_without_package_metadata():
    """Running from a bare checkout (no dist-info) must still import."""
    try:
        with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
            importlib.reload(postmark)
            assert postmark.__version__ == "0.0.0"
    finally:
        importlib.reload(postmark)  # restore the real value for later tests

    assert postmark.__version__ != "0.0.0"
