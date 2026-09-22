"""Tests for post_gen_project hook behavior."""

import logging
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from hooks import post_gen_project


@pytest.fixture
def agent_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create the `data/` directory that the coding agent setup copies from."""
    skill_path = tmp_path / "data" / "skills" / "write-code"
    skill_path.mkdir(parents=True)
    (skill_path / "SKILL.md").write_text("skill\n", encoding="utf-8")

    claude_path = tmp_path / "data" / "claude"
    claude_path.mkdir(parents=True)
    (claude_path / "settings.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "data" / "AGENTS_README.md").write_text("# Guide\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_set_python_version_updates_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Replace {python_version} in pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text(
        'requires-python = ">= {python_version}"\n',
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    post_gen_project.set_python_version("3.13")

    pyproject_contents = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    assert pyproject_contents == 'requires-python = ">= 3.13"\n'


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


def test_setup_coding_agent_files_claude(agent_data: Path) -> None:
    """Claude gets CLAUDE.md, skills in `.claude/`, and the settings it understands."""
    post_gen_project.setup_coding_agent_files("Claude")

    assert (agent_data / "CLAUDE.md").exists()
    assert (agent_data / ".claude" / "skills" / "write-code" / "SKILL.md").exists()
    assert (agent_data / ".claude" / "settings.json").exists()
    assert not (agent_data / ".agent").exists()


def test_setup_coding_agent_files_codex(agent_data: Path) -> None:
    """Codex gets AGENTS.md and skills in `.agent/`, but no Claude-only files."""
    post_gen_project.setup_coding_agent_files("Codex")

    assert (agent_data / "AGENTS.md").exists()
    assert (agent_data / ".agent" / "skills" / "write-code" / "SKILL.md").exists()
    assert not (agent_data / ".agent" / "settings.json").exists()
    assert not (agent_data / ".claude").exists()
    assert not (agent_data / "CLAUDE.md").exists()


def test_setup_coding_agent_files_none(agent_data: Path) -> None:
    """No agent files are created when no agent is selected."""
    post_gen_project.setup_coding_agent_files("None")

    assert not (agent_data / ".claude").exists()
    assert not (agent_data / ".agent").exists()
    assert not (agent_data / "CLAUDE.md").exists()
    assert not (agent_data / "AGENTS.md").exists()


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


def test_check_prerequisites_requires_gh_only_for_github_setup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Probe the GitHub CLI only when a repository will be created."""
    checked: list[str] = []
    monkeypatch.setattr(
        post_gen_project, "check_program", lambda program, _: checked.append(program)
    )

    post_gen_project.check_prerequisites("None")
    assert not any("gh" in program for program in checked)

    checked.clear()
    post_gen_project.check_prerequisites("private")
    assert "gh --version" in checked


def test_github_setup_qualifies_the_repo_with_the_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create the repository under the given owner rather than the authenticated user."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))

    post_gen_project.github_setup("private", owner="octocat", name="spam")

    assert calls[0] == "gh repo create octocat/spam --private --remote origin --source . --push"


def test_github_setup_stops_after_a_failing_gh(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Skip the upstream configuration when the repository was never created."""
    calls: list[str] = []

    def fake_call(cmd: str, **_: object) -> None:
        calls.append(cmd)
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(post_gen_project, "call", fake_call)

    with caplog.at_level(logging.ERROR):
        post_gen_project.github_setup("public", owner="octocat", name="spam")

    assert len(calls) == 1
    assert "Retry with" in caplog.text


def test_github_setup_rejects_unknown_privacy() -> None:
    """Reject a privacy level the GitHub CLI has no flag for."""
    with pytest.raises(ValueError, match="secret"):
        post_gen_project.github_setup("secret")
