"""Tests for post_gen_project hook behavior."""

import ast
import json
import logging
import subprocess
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
from cookiecutter.environment import StrictEnvironment
from pytest import mark

from hooks import post_gen_project


@pytest.fixture
def agent_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create the `data/` directory that the agent setup copies from."""
    skill_path = tmp_path / "data" / ".agents" / "skills" / "write-code"
    skill_path.mkdir(parents=True)
    (skill_path / "SKILL.md").write_text("skill\n", encoding="utf-8")

    for agent, settings in ((".claude", "settings.json"), (".codex", "hooks.json")):
        (tmp_path / "data" / agent).mkdir()
        (tmp_path / "data" / agent / settings).write_text("{}\n", encoding="utf-8")
    (tmp_path / "data" / "AGENTS.md").write_text("# Guide\n", encoding="utf-8")

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


def test_setup_agent_files_serves_claude_and_codex(agent_data: Path) -> None:
    """Write skills to `.agents/skills/` and make `.claude/skills/` a symlink to it.

    Codex reads `.agents/skills/` and Claude Code `.claude/skills/`, neither the other's; both
    read AGENTS.md, so no CLAUDE.md, which would stop Claude Code reading AGENTS.md.
    """
    post_gen_project.setup_agent_files()

    link = agent_data / ".claude" / "skills"
    assert link.is_symlink()
    assert link.resolve() == (agent_data / ".agents" / "skills").resolve()
    assert (link / "write-code" / "SKILL.md").read_text(encoding="utf-8") == "skill\n"
    assert (agent_data / ".claude" / "settings.json").exists()
    assert (agent_data / ".codex" / "hooks.json").exists()
    assert (agent_data / "AGENTS.md").read_text(encoding="utf-8") == "# Guide\n"
    assert not (agent_data / "CLAUDE.md").exists()


def test_claude_skills_link_survives_project_move(
    agent_data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Claude's skills link reaches the shared files after the project moves."""
    post_gen_project.setup_agent_files()

    monkeypatch.chdir(agent_data.parent)
    moved = agent_data.rename(agent_data.with_name(f"{agent_data.name}-moved"))
    link = moved / ".claude" / "skills"
    assert link.resolve() == (moved / ".agents" / "skills").resolve()
    assert (link / "write-code" / "SKILL.md").read_text(encoding="utf-8") == "skill\n"


def test_claude_and_codex_run_the_same_edit_hooks() -> None:
    """Format after an edit the same way whichever agent made it.

    Both agents read the same `hooks` shape, and both match file edits with `Edit|Write`.
    """
    data = TEMPLATE_ROOT / "data"
    claude = json.loads((data / ".claude" / "settings.json").read_text(encoding="utf-8"))
    codex = json.loads((data / ".codex" / "hooks.json").read_text(encoding="utf-8"))

    assert claude["hooks"] == codex["hooks"]


@pytest.mark.parametrize(
    ("protocol", "expected"),
    [
        ("git", "git@github.com:user/repo.git"),
        ("https", "https://github.com/user/repo.git"),
    ],
)
def test_git_add_remote_formats_url(
    protocol: post_gen_project.GitProtocol,
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


def test_read_write_rejects_a_missing_placeholder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Raise when the placeholder is absent, rather than leaving the file untouched."""
    (tmp_path / "pyproject.toml").write_text("version = '0.0.1'\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="renamed"):
        post_gen_project.read_write("pyproject.toml", "{renamed}", "1")


def test_update_dependencies_fills_both_placeholders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Write both the runtime and the test dependencies into pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pixi.dependencies]\n{pixi_dependencies}\n[dev]\n{pixi_test_dependencies}\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(post_gen_project, "call", lambda *_, **__: None)

    post_gen_project.update_dependencies("numpy", "pytest-xdist@>=3.6")

    contents = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'numpy = "*"\n' in contents
    assert 'pytest-xdist = ">=3.6"\n' in contents


def test_update_dependencies_collapses_empty_specs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Drop the placeholder line entirely when no dependencies were requested."""
    (tmp_path / "pyproject.toml").write_text(
        "[tool.pixi.dependencies]\n{pixi_dependencies}\n[dev]\n{pixi_test_dependencies}\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(post_gen_project, "call", lambda *_, **__: None)

    post_gen_project.update_dependencies("", " ")

    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == (
        "[tool.pixi.dependencies]\n[dev]\n"
    )


def test_verify_generated_project_warns_rather_than_raising(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Report failing hooks without raising, which would delete the generated project."""
    monkeypatch.setattr(post_gen_project, "call", lambda *_, **__: SimpleNamespace(returncode=1))

    with caplog.at_level(logging.WARNING):
        post_gen_project.verify_generated_project()

    assert "fails its own hooks" in caplog.text


def test_notes_link_the_given_repository(caplog: pytest.LogCaptureFixture) -> None:
    """Point the token links at the repository that was passed in."""
    with caplog.at_level(logging.INFO):
        post_gen_project.notes("octocat", "spam")

    assert "https://app.codecov.io/gh/octocat/spam/settings" in caplog.text
    assert "https://github.com/octocat/spam/settings/secrets/actions" in caplog.text


def test_notes_skipped_without_a_github_username(caplog: pytest.LogCaptureFixture) -> None:
    """Print nothing when there is no GitHub username."""
    with caplog.at_level(logging.INFO):
        post_gen_project.notes("", "spam")

    assert not caplog.text


def test_git_initial_commit_skips_the_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Commit with --no-verify, since the hooks already ran over the whole tree."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))

    post_gen_project.git_initial_commit()

    assert calls == ["git add .", "git commit --no-verify -m Setup"]


def test_every_license_choice_ships_a_file_set_license_can_format() -> None:
    """Match the license choices against the files `set_license` copies from."""
    choices = json.loads(Path("cookiecutter.json").read_text(encoding="utf-8"))["license"]
    licenses = Path("{{cookiecutter.package_name}}/data/licenses")

    for choice in choices:
        if choice == "None":
            continue

        path = licenses / choice
        assert path.exists(), f"{choice} has no file in {licenses}"
        assert "{author_name}" in path.read_text(encoding="utf-8")


def test_set_license_rejects_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject a license with no file, rather than guessing at the case."""
    (tmp_path / "data" / "licenses").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="not available"):
        post_gen_project.set_license("BSD-3-clause")


TEMPLATE_ROOT = Path("{{cookiecutter.package_name}}")


def render_template(context: dict[str, str]) -> dict[Path, str]:
    """Render every template file cookiecutter would render for a context.

    Args:
        context: cookiecutter context to render with

    Returns:
        Mapping of path relative to the template root to rendered contents
    """
    environment = StrictEnvironment(context={"cookiecutter": context}, keep_trailing_newline=True)
    copied_verbatim = json.loads(Path("cookiecutter.json").read_text(encoding="utf-8"))[
        "_copy_without_render"
    ]

    rendered = {}
    for path in sorted(TEMPLATE_ROOT.rglob("*")):
        relative = path.relative_to(TEMPLATE_ROOT)
        if path.is_dir() or any(relative.is_relative_to(glob) for glob in copied_verbatim):
            continue

        source = path.read_text(encoding="utf-8")
        rendered[relative] = environment.from_string(source).render(cookiecutter=context)

    return rendered


@mark.parametrize("license_name", ["MIT", "Apache-2.0", "BSD-3-Clause", "None"])
@mark.parametrize("author_name", ["Jane Doe", ""])
def test_template_renders_to_well_formed_files(license_name: str, author_name: str) -> None:
    """Render every option combination, then parse the TOML, JSON, and Python it produces.

    This is the only check that a comment or a conditional edit did not take a Jinja tag with
    it, since the root `prek.toml` has to exclude the template's `pyproject.toml` from
    `check-toml`.
    """
    context = {
        "project_name": "Spam Deluxe",
        "package_name": "spam_deluxe",
        "author_name": author_name,
        "github_username": "octocat",
        "project_url": "https://github.com/octocat/spam_deluxe",
        "python_version": "3.14",
        "line_length": "100",
        "license": license_name,
    }

    for relative, contents in render_template(context).items():
        assert "{{" not in contents, f"unrendered Jinja left in {relative}"
        assert "{%" not in contents, f"unrendered Jinja left in {relative}"

        match relative.suffix:
            case ".toml":
                # The post-gen hook fills these in; until it does the file is not valid TOML
                filled = (
                    contents.replace("{python_version}", context["python_version"])
                    .replace("{pixi_dependencies}\n", "")
                    .replace("{pixi_test_dependencies}\n", "")
                )
                tomllib.loads(filled)
            case ".json":
                json.loads(contents)
            case ".py":
                ast.parse(contents)
            case _:
                pass
