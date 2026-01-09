"""Tests for post_gen_project hook behavior."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from hooks import post_gen_project


def test_set_python_version_updates_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace {python_version} in target files."""
    workflow_path = tmp_path / ".github" / "workflows"
    workflow_path.mkdir(parents=True)

    (workflow_path / "test.yml").write_text("python: {python_version}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        'requires-python = ">= {python_version}"\n',
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(version_info=SimpleNamespace(major=3, minor=13))
    monkeypatch.setattr(post_gen_project, "sys", args)

    post_gen_project.set_python_version()

    workflow_contents = (workflow_path / "test.yml").read_text(encoding="utf-8")
    pyproject_contents = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    assert workflow_contents == "python: 3.13\n"
    assert pyproject_contents == 'requires-python = ">= 3.13"\n'
    assert "{python_version}" not in workflow_contents
    assert "{python_version}" not in pyproject_contents


def test_set_python_version_warns_on_old_minor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Warn when Python minor version is below supported minimum."""
    workflow_path = tmp_path / ".github" / "workflows"
    workflow_path.mkdir(parents=True)
    (workflow_path / "test.yml").write_text("python: {python_version}\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        'requires-python = ">= {python_version}"\n',
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(version_info=SimpleNamespace(major=3, minor=11))
    monkeypatch.setattr(post_gen_project, "sys", args)

    post_gen_project.set_python_version()
    captured = capsys.readouterr()
    assert "should be upgraded" in captured.err


def test_set_license_copies_and_formats(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Copy license file and fill placeholders."""
    licenses_path = tmp_path / "data" / "licenses"
    licenses_path.mkdir(parents=True)
    (licenses_path / "MIT").write_text(
        "Copyright {year} {author_name}",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(now=lambda: SimpleNamespace(year=2026))
    monkeypatch.setattr(post_gen_project, "datetime", args)

    post_gen_project.set_license("MIT")

    license_contents = (tmp_path / "LICENSE").read_text(encoding="utf-8")
    assert "2026" in license_contents
    assert "{{cookiecutter.author_name}}" in license_contents


@pytest.mark.parametrize(
    ("protocol", "expected"),
    [
        ("git", "git@github.com:user/repo.git"),
        ("https", "https://github.com/user/repo.git"),
    ],
)
def test_git_add_remote_formats_url(
    protocol: post_gen_project.PROTOCOL,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Format remote URL based on protocol."""
    calls: list[str] = []

    def fake_call(cmd: str, **_: object) -> None:
        calls.append(cmd)

    monkeypatch.setattr(post_gen_project, "call", fake_call)
    post_gen_project.git_add_remote("origin", "https://github.com/user/repo.git", protocol=protocol)
    assert calls == [f"git remote add origin {expected}"]
