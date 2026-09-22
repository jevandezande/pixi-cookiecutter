"""Hooks for setting up project once generated."""

import logging
import shutil
import subprocess
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, assert_never
from urllib.parse import urlparse

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("post_gen_project")


type GitProtocol = Literal["git", "https"]
GITHUB_PRIVACY_OPTIONS = ("private", "internal", "public")
DEFAULT_BRANCH = "master"
AGENT_DIR = Path(".claude")


class CodingAgent(StrEnum):
    """Coding agents supported, as lowercased `cookiecutter.json` choices."""

    NONE = "none"
    CLAUDE = "claude"
    CODEX = "codex"


def call(cmd: str, check: bool = True, **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
    """Call shell commands.

    Args:
        cmd: command to call
        check: whether to raise an exception if the command fails
        kwargs: keyword arguments to pass to subprocess.call

    Warning:
        strings with spaces are not yet supported
    """
    logger.debug(f"Calling: {cmd}")
    return subprocess.run(cmd.split(), check=check, **kwargs)


def read_write(file_name: str, old: str, new: str) -> None:
    """Replace all occurrences of a substring in a file.

    Args:
        file_name: file to modify
        old: substring to replace
        new: replacement substring

    Raises:
        ValueError: `old` is not in the file, so a renamed placeholder cannot pass silently
    """
    path = Path(file_name)
    contents = path.read_text(encoding="utf-8")
    if old not in contents:
        raise ValueError(f"{old!r} not found in {file_name}")

    path.write_text(contents.replace(old, new), encoding="utf-8")


def set_python_version(python_version: str) -> None:
    """Set the python version in pyproject.toml.

    The workflow does not need it; CI resolves python from pixi.lock.

    Args:
        python_version: `major.minor` version of python (validated in the pre-gen hook)
    """
    logger.info(f"Setting {python_version=}")

    read_write("pyproject.toml", "{python_version}", python_version)


def set_license(license_name: str) -> None:
    """Write the selected license to LICENSE (if any).

    Args:
        license_name: SPDX identifier of the license (or "None" for no license)

    Raises:
        ValueError: if license is not available
    """
    if license_name == "None":
        logger.debug("No license set")
        return

    licenses = {path.name for path in Path("data/licenses").iterdir()}
    if license_name not in licenses:
        raise ValueError(f"{license_name=} not available; select from:\n{licenses}")

    contents = Path(f"data/licenses/{license_name}").read_text(encoding="utf-8")
    contents = contents.replace("{year}", f"{datetime.now().year}")
    contents = contents.replace("{author_name}", "{{cookiecutter.author_name}}")

    stripped = "\n".join(line.rstrip() for line in contents.split("\n"))
    Path("LICENSE").write_text(stripped, encoding="utf-8")

    logger.debug(f"Set {license_name=}")


def git_init(default_branch: str = DEFAULT_BRANCH) -> None:
    """Initialize a git repository.

    The branch is set explicitly so it matches the branch referenced by the generated
    workflow, README badges, and upstream configuration.

    Args:
        default_branch: name of the initial branch
    """
    call(f"git init -b {default_branch}")


def process_dependency(dependency: str) -> str:
    """Process a dependency.

    Args:
        dependency: dependency to process

    Returns:
        processed dependency in the format 'package = "version"'

    Examples:
        >>> process_dependency("pytest")
        'pytest = "*"'
        >>> process_dependency("matplotlib@>=3.7.2")
        'matplotlib = ">=3.7.2"'
        >>> process_dependency("more-itertools@10.*")
        'more-itertools = "10.*"'
        >>> process_dependency("")
        Traceback (most recent call last):
        ...
        ValueError: Blank dependency
        >>> process_dependency("hello@1.2.3@v40")
        Traceback (most recent call last):
        ...
        ValueError: Unable to process dependency='hello@1.2.3@v40'
    """
    if not dependency:
        raise ValueError("Blank dependency")

    match dependency.split("@"):
        case [package]:
            return f'{package} = "*"'
        case [package, version]:
            return f'{package} = "{version}"'
        case _:
            raise ValueError(f"Unable to process {dependency=}")


def process_dependencies(deps: str) -> str:
    r"""Process a space separated list of dependencies.

    Args:
        deps: dependencies to process

    Returns:
        processed dependencies in the format 'package = "version"'

    Examples:
        >>> process_dependencies(' ')
        ''
        >>> process_dependencies("pytest matplotlib@~3.7 black@!=1.2.3")
        'pytest = "*"\nmatplotlib = "~3.7"\nblack = "!=1.2.3"\n'
    """
    if not deps.strip():
        return ""

    return "\n".join(map(process_dependency, deps.split())) + "\n"


def update_dependencies(
    # Extra space and .strip() avoids accidentally creating '""""'
    deps: str = """{{cookiecutter.pixi_dependencies}} """.strip(),
    test_deps: str = """{{cookiecutter.pixi_test_dependencies}} """.strip(),
) -> None:
    """Add and update the dependencies in pyproject.toml and pixi.lock.

    Args:
        deps: space separated runtime dependencies
        test_deps: space separated test dependencies
    """
    read_write("pyproject.toml", "{pixi_dependencies}\n", process_dependencies(deps))
    read_write("pyproject.toml", "{pixi_test_dependencies}\n", process_dependencies(test_deps))

    call("pixi update")


def check_program(program: str, install_str: str, **run_kwargs: Any) -> None:
    """Check that a program is installed.

    Args:
        program: name of the program to check
        install_str: string to print if the program is not installed
        run_kwargs: keyword arguments to pass to subprocess.call

    Examples:
        >>> check_program("python", "https://www.python.org")  # doctest: +SKIP
        >>> check_program("this_program_does_not_exist", "nothing")  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        OSError: this_program_does_not_exist is not installed; install with `nothing`
    """
    try:
        call(program, stdout=subprocess.DEVNULL, **run_kwargs)
    except FileNotFoundError as e:
        raise OSError(f"{program} is not installed; install with `{install_str}`") from e
    except subprocess.CalledProcessError as e:
        raise OSError(f"Issue with {program} encountered") from e


def check_prerequisites(github_setup: str = "{{cookiecutter.github_setup}}") -> None:
    """Check that the tools generation needs are installed, before anything is built.

    Args:
        github_setup: privacy of the GitHub repository to create, or "None" to skip the CLI check
    """
    check_program("pixi --version", "https://pixi.sh/latest/#installation")
    check_program("direnv --version", "pixi global install direnv")

    if github_setup != "None":
        check_program("gh --version", "https://cli.github.com/")


def allow_direnv() -> None:
    """Allow direnv."""
    call("direnv allow .")


def git_hooks() -> None:
    """Install pre-commit and pre-push hooks (via prek)."""
    call("pixi run -e dev prek install")


def setup_coding_agent_files(agent: str) -> None:
    """Set up the selected agent's files; AGENTS.md ships even when none was chosen.

    Every agent reads the conventions from the same `AGENTS.md`, so none of them get a second
    copy to keep in step.

    Args:
        agent: coding agent name ("claude", "codex", or "none")

    Raises:
        ValueError: if coding agent is not supported
    """
    coding_agent = CodingAgent(agent.lower())
    shutil.copy(Path("data/AGENTS_README.md"), Path("AGENTS.md"))

    if coding_agent is CodingAgent.NONE:
        return

    logger.info(f"Setting up files for {coding_agent.value}")
    shutil.copytree("data/skills", AGENT_DIR / "skills")

    match coding_agent:
        case CodingAgent.CLAUDE:
            # Settings are only understood by Claude Code
            shutil.copy(Path("data/claude/settings.json"), AGENT_DIR / "settings.json")
            cmd = "claude -p 'Read AGENTS.md and update it'"
        case CodingAgent.CODEX:
            cmd = "codex exec 'Read AGENTS.md and update it'"
        case _:
            assert_never(coding_agent)

    logger.info(f"Run `{cmd}` to finish agent setup.")


def remove_data_dir() -> None:
    """Remove the data directory."""
    shutil.rmtree("data")


def verify_generated_project() -> None:
    """Run the generated project's own hooks over the tree, warning on failure.

    A raise would have cookiecutter delete an otherwise finished project, so failures are
    reported instead. The hooks are mutating, so any formatting they fix lands in the initial
    commit.
    """
    call("git add .")
    if call("pixi run -e dev prek run -a --stage pre-push", check=False).returncode:
        logger.warning("Generated project fails its own hooks; see above")


def git_initial_commit() -> None:
    """Make the initial commit, skipping the hooks `verify_generated_project` just ran."""
    call("git add .")
    call("git commit --no-verify -m Setup")


def setup_remote(remote: str = "origin") -> None:
    """Add remote (and optionally setup GitHub).

    Args:
        remote: name for the remote
    """
    if "{{cookiecutter.github_setup}}" != "None":  # noqa: PLR0133
        github_setup("{{cookiecutter.github_setup}}", remote)
        return

    url = "{{cookiecutter.project_url}}"
    if not valid_remote_url(url):
        logger.warning(f"Skipping remote setup; {url=} is incomplete.")
        return

    git_add_remote(remote, url)


def valid_remote_url(url: str) -> bool:
    """Check that a remote url has a hostname and no empty path segments.

    Args:
        url: url of the remote

    Returns:
        whether the url is complete enough to use as a remote

    Examples:
        >>> valid_remote_url("https://github.com/octocat/repo")
        True
        >>> valid_remote_url("https://github.com//repo")
        False
        >>> valid_remote_url("https://github.com")
        False
        >>> valid_remote_url("")
        False
    """
    parsed = urlparse(url)
    segments = parsed.path.split("/")[1:]
    return bool(parsed.hostname and segments and all(segments))


def git_add_remote(remote: str, url: str, protocol: GitProtocol = "git") -> None:
    """Add a remote to the git repository.

    Args:
        remote: name for the remote
        url: url of remote
        protocol: protocol of the remote ("git" or "https")
    """
    if protocol == "git":
        _, _, hostname, path = url.split("/", 3)
        url = f"{protocol}@{hostname}:{path}"

    call(f"git remote add {remote} {url}")


def github_setup(
    privacy: str,
    remote: str = "origin",
    default_branch: str = DEFAULT_BRANCH,
    owner: str = "{{cookiecutter.github_username}}",
    name: str = "{{cookiecutter.package_name}}",
) -> None:
    """Make a repository on GitHub (requires GitHub CLI).

    The repository is qualified with its owner, so it lands under `github_username` rather than
    whoever the GitHub CLI happens to be authenticated as.

    Args:
        privacy: privacy of the repository ("private", "internal", "public")
        remote: name of the remote to add
        default_branch: name of the default branch for upstream
        owner: user or organization to create the repository under
        name: name of the repository

    Raises:
        ValueError: if privacy option is not valid
    """
    if privacy not in GITHUB_PRIVACY_OPTIONS:
        raise ValueError(f"{privacy=} not in {GITHUB_PRIVACY_OPTIONS}")

    create = f"gh repo create {owner}/{name} --{privacy} --remote {remote} --source . --push"

    try:
        call(create)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating GitHub repository: {e}\nRetry with: {create}")
        return

    try:
        call(f"git config branch.{default_branch}.remote {remote}")
        call(f"git config branch.{default_branch}.merge refs/heads/{default_branch}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting upstream to {default_branch}: {e}")


def notes() -> None:
    """Print notes for the user (if hosted on GitHub)."""
    if not "{{cookiecutter.github_username}}":
        return

    logger.info(
        """
If using GitHub, generate a CODECOV_TOKEN at:
https://app.codecov.io/gh/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/settings

and add it to the GitHub repository secrets at:
https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/settings/secrets/actions
"""
    )


SUCCESS = "\x1b[1;32m"
TERMINATOR = "\x1b[0m"


def main() -> None:
    """Run the post generation hooks."""
    check_prerequisites()
    set_python_version("{{cookiecutter.python_version}}")
    set_license("{{cookiecutter.license}}")
    git_init()
    update_dependencies()
    allow_direnv()
    git_hooks()
    setup_coding_agent_files("{{cookiecutter.coding_agent}}")
    remove_data_dir()
    verify_generated_project()
    git_initial_commit()
    setup_remote("origin")

    notes()

    logger.info(f"{SUCCESS}Project successfully initialized{TERMINATOR}")


if __name__ == "__main__":
    main()
