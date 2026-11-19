"""Tests for post_gen_project hook behavior."""

import ast
import json
import logging
import re
import subprocess
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest
from cookiecutter.environment import StrictEnvironment
from pytest import mark, raises

from hooks import post_gen_project

TEMPLATE_ROOT = Path("{{cookiecutter.package_name}}")


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


@mark.parametrize(
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
    """Rewrite HTTPS URL into `git@` form, or leave it alone for `https`."""
    calls: list[str] = []

    def fake_call(cmd: str, **_: object) -> None:
        calls.append(cmd)

    monkeypatch.setattr(post_gen_project, "call", fake_call)
    post_gen_project.git_add_remote("origin", "https://github.com/user/repo.git", protocol=protocol)
    assert calls == [f"git remote add origin {expected}"]


@mark.parametrize(
    ("github_setup", "expected"), [("None", False), ("private", True), ("public", True)]
)
def test_check_prerequisites_requires_gh_only_for_github_setup(
    github_setup: str, expected: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Check GitHub CLI up front, rather than after the project is built."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))

    post_gen_project.check_prerequisites(github_setup)

    assert ("gh --version" in calls) is expected


def test_check_program_reports_the_install_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """Turn a missing prerequisite into an error that says how to install it."""

    def missing(*_: object, **__: object) -> None:
        raise FileNotFoundError

    monkeypatch.setattr(post_gen_project, "call", missing)

    with raises(OSError, match=re.escape("install with `https://cli.github.com/`")):
        post_gen_project.check_program("gh --version", "https://cli.github.com/")


def test_check_program_reports_the_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tell a broken install apart from a missing one, and say what it exited with."""

    def broken(cmd: str, **_: object) -> None:
        raise subprocess.CalledProcessError(127, cmd)

    monkeypatch.setattr(post_gen_project, "call", broken)

    with raises(RuntimeError, match="`gh --version` exited with 127"):
        post_gen_project.check_program("gh --version", "https://cli.github.com/")


@mark.parametrize(
    ("privacy", "url", "expected"),
    [
        ("private", "https://github.com/octocat/spam", "github_setup private"),
        (
            "None",
            "https://github.com/octocat/spam",
            "git remote add origin git@github.com:octocat/spam",
        ),
        ("None", "https://github.com//spam", None),
    ],
)
def test_setup_remote_creates_or_adds_or_skips(
    privacy: str, url: str, expected: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Create repository when a privacy was chosen, else add URL as remote if it is complete."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))
    monkeypatch.setattr(
        post_gen_project, "github_setup", lambda privacy, _: calls.append(f"github_setup {privacy}")
    )

    post_gen_project.setup_remote("origin", privacy, url)

    assert calls == ([expected] if expected else [])


def test_github_setup_qualifies_the_repo_with_the_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create `owner/name`, so repo matches URLs the project embeds."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))

    post_gen_project.github_setup("internal", owner="acme", name="spam")

    assert calls[0] == "gh repo create acme/spam --internal --remote origin --source . --push"


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


def test_github_setup_rejects_unknown_privacy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raise before touching gh, so a typo cannot create a repo with the wrong visibility."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))

    with raises(ValueError, match="privacy='pubic'"):
        post_gen_project.github_setup("pubic")

    assert calls == []


def test_read_write_rejects_a_missing_placeholder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Raise when the placeholder is absent, rather than leaving the file untouched."""
    (tmp_path / "pyproject.toml").write_text("version = '0.0.1'\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with raises(ValueError, match="renamed"):
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
    """Report failing hooks without aborting; cookiecutter deletes project on a raise.

    Pre-push stage runs, since test suites are pre-push hooks that `prek run` alone skips.
    """
    calls: list[str] = []

    def fake_call(cmd: str, **_: object) -> SimpleNamespace:
        calls.append(cmd)
        return SimpleNamespace(returncode=int("prek" in cmd))

    monkeypatch.setattr(post_gen_project, "call", fake_call)

    with caplog.at_level(logging.WARNING):
        post_gen_project.verify_generated_project()

    # Staged first: `prek run -a` sees only what git knows about
    assert calls == ["git add .", "pixi run -e dev prek run -a --stage pre-push"]
    assert "fails its own hooks" in caplog.text


def test_verify_generated_project_is_quiet_when_the_hooks_pass(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Say nothing when generated project already satisfies its own hooks."""
    monkeypatch.setattr(post_gen_project, "call", lambda *_, **__: SimpleNamespace(returncode=0))

    post_gen_project.verify_generated_project()

    assert not caplog.text


def test_git_initial_commit_skips_the_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Commit with --no-verify: hooks already ran, where failing them is not fatal."""
    calls: list[str] = []
    monkeypatch.setattr(post_gen_project, "call", lambda cmd, **_: calls.append(cmd))

    post_gen_project.git_initial_commit()

    assert calls == ["git add .", "git commit --no-verify -m Setup"]


def test_every_license_choice_ships_a_file_set_license_can_format() -> None:
    """Ship a file per license choice, each carrying the placeholders `set_license` fills."""
    choices = json.loads(Path("cookiecutter.json").read_text(encoding="utf-8"))["license"]
    licenses = TEMPLATE_ROOT / "data" / "licenses"

    expected = {choice for choice in choices if choice != "None"}

    assert expected == {path.name for path in licenses.iterdir()}

    for path in licenses.iterdir():
        contents = path.read_text(encoding="utf-8")
        assert "{year}" in contents, path.name
        assert "{author_name}" in contents, path.name


def test_set_license_rejects_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Raise on a license with no file to copy, listing what is available."""
    licenses_path = tmp_path / "data" / "licenses"
    licenses_path.mkdir(parents=True)
    (licenses_path / "MIT").write_text("MIT text", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    with raises(ValueError, match="WTFPL"):
        post_gen_project.set_license("WTFPL")

    assert not (tmp_path / "LICENSE").exists()


def cookiecutter_context(**overrides: str) -> dict[str, str]:
    """Build context cookiecutter would render with: `cookiecutter.json` defaults, overridden.

    Args:
        overrides: option values to replace defaults with

    Returns:
        `cookiecutter` namespace, with derived names resolved
    """
    raw = json.loads(Path("cookiecutter.json").read_text(encoding="utf-8"))
    context = {
        key: value[0] if isinstance(value, list) else value
        for key, value in raw.items()
        if not key.startswith("_")
    } | overrides
    package_name = context["project_name"].lower().replace(" ", "_").replace("-", "_")
    context["package_name"] = package_name
    context["project_url"] = f"https://github.com/{context['github_username']}/{package_name}"
    return context


def render_template(context: dict[str, str]) -> dict[Path, str]:
    """Render every file cookiecutter renders for a context, hooks included.

    Args:
        context: cookiecutter context to render with

    Returns:
        Mapping of path relative to repo root to rendered contents
    """
    environment = StrictEnvironment(context={"cookiecutter": context}, keep_trailing_newline=True)
    copied_verbatim = json.loads(Path("cookiecutter.json").read_text(encoding="utf-8"))[
        "_copy_without_render"
    ]

    paths = [
        path
        for path in TEMPLATE_ROOT.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and not any(
            path.relative_to(TEMPLATE_ROOT).full_match(glob)
            or path.relative_to(TEMPLATE_ROOT).is_relative_to(glob)
            for glob in copied_verbatim
        )
    ]
    paths += [Path("hooks") / name for name in ("pre_gen_project.py", "post_gen_project.py")]

    return {
        path: environment.from_string(path.read_text(encoding="utf-8")).render(cookiecutter=context)
        for path in sorted(paths)
    }


@mark.parametrize("license_name", ["MIT", "Apache-2.0", "BSD-3-Clause", "None"])
@mark.parametrize("author_name", ["Jane Doe", ""])
def test_template_renders_to_well_formed_files(license_name: str, author_name: str) -> None:
    """Render every file for option combination and parse what has a parser.

    Root `prek.toml` has to exclude Jinja-bearing TOML from `check-toml`; this is the only check
    short of CI that a comment edit did not take a Jinja tag with it.
    """
    context = cookiecutter_context(
        project_name="Spam Deluxe",
        author_name=author_name,
        github_username="octocat",
        license=license_name,
    )

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
