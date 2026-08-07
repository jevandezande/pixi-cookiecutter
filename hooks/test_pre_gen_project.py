"""Tests for pre_gen_project hook behavior."""

import logging

import pytest

from hooks import pre_gen_project

MINIMUM_MINOR = pre_gen_project.MINIMUM_PYTHON_MINOR_VERSION


def test_check_python_version_warns_on_old_minor(caplog: pytest.LogCaptureFixture) -> None:
    """Warn (but do not fail) when the python minor version is below the supported minimum."""
    with caplog.at_level(logging.WARNING):
        pre_gen_project.check_python_version(f"3.{MINIMUM_MINOR - 1}")

    assert "should be upgraded" in caplog.text


def test_check_python_version_accepts_minimum(caplog: pytest.LogCaptureFixture) -> None:
    """Do not warn for a supported python version."""
    with caplog.at_level(logging.WARNING):
        pre_gen_project.check_python_version(f"3.{MINIMUM_MINOR}")

    assert caplog.text == ""
