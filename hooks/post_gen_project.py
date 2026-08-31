"""Hooks for setting up project once generated."""

import logging
import shutil
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("post_gen_project")


PROTOCOL = Literal["git", "https"]
GITHUB_PRIVACY_OPTIONS = ["private", "internal", "public"]
DEFAULT_BRANCH = "master"
DEFAULT_AGENT_DIR = ".agent"
CLAUDE_AGENT_DIR = ".claude"


class CodingAgent(str, Enum):
    """Coding agents supported."""

    CLAUDE = "claude"
    CODEX = "codex"

    @property
    def directory(self) -> Path:
        """Directory the agent reads its skills (and settings) from.

        Examples:
            >>> str(CodingAgent.CLAUDE.directory)
            '.claude'
            >>> str(CodingAgent.CODEX.directory)
            '.agent'
        """
        return Path(CLAUDE_AGENT_DIR if self is CodingAgent.CLAUDE else DEFAULT_AGENT_DIR)


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


def set_python_version(python_version: str) -> None:
    """Set the python version in pyproject.toml.

    The workflow does not need it; CI resolves python from pixi.lock.

    Args:
        python_version: `major.minor` version of python (validated in the pre-gen hook)
    """
    logger.info(f"Setting {python_version=}")

    pyproject = Path("pyproject.toml")
    contents = pyproject.read_text(encoding="utf-8")
    pyproject.write_text(contents.replace("{python_version}", python_version), encoding="utf-8")


def set_license(license: str | None = "MIT") -> None:
    """Write the selected license to LICENSE (if any).

    Args:
        license: name of the license (or None for no license)

    Raises:
        ValueError: if license is not available
    """
    if not license or license == "None":
        logger.debug("No license set")
        return

    licenses = {lic.name for lic in Path("data/licenses").iterdir()}
    if license not in licenses:
        try:
            # Check and correct cases
            license = next(lic for lic in licenses if lic.lower() == license.lower())
            logger.warning(f"Corrected license to {license=}")
        except StopIteration as e:
            raise ValueError(f"{license=} not available; select from:\n{licenses}") from e

    contents = Path(f"data/licenses/{license}").read_text(encoding="utf-8")
    contents = contents.replace("{year}", f"{datetime.now().year}")
    contents = contents.replace("{author_name}", "{{cookiecutter.author_name}}")

    stripped = "\n".join(line.rstrip() for line in contents.split("\n"))
    Path("LICENSE").write_text(stripped, encoding="utf-8")

    logger.debug(f"Set {license=}")


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


def update_dependencies() -> None:
    """Add and update the dependencies in pyproject.toml and pixi.lock."""
    # Extra space and .strip() avoids accidentally creating '""""'
    dependencies = process_dependencies("""{{cookiecutter.pixi_dependencies}} """.strip())
    dev_dependencies = process_dependencies("""{{cookiecutter.pixi_test_dependencies}} """.strip())

    pyproject = Path("pyproject.toml")
    contents = (
        pyproject.read_text(encoding="utf-8")
        .replace("{pixi_dependencies}\n", dependencies)
        .replace("{pixi_test_dependencies}\n", dev_dependencies)
    )
    pyproject.write_text(contents, encoding="utf-8")

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


def allow_direnv() -> None:
    """Allow direnv."""
    check_program("direnv", "pixi global install direnv")
    call("direnv allow .")


def git_hooks() -> None:
    """Install pre-commit and pre-push hooks (via prek)."""
    call("pixi run -e dev prek install")


def setup_coding_agent_files(agent: str) -> None:
    """Set up coding agent files.

    Args:
        agent: coding agent name ("claude", "codex", or "none")

    Raises:
        ValueError: if coding agent is not supported
    """
    if agent.lower() == "none":
        return

    coding_agent = CodingAgent(agent.lower())
    logger.info(f"Setting up files for {coding_agent}.")

    source = Path("data/AGENTS_README.md")

    # Created up front so agent-specific files have somewhere to land
    agent_dir = coding_agent.directory
    agent_dir.mkdir(parents=True, exist_ok=True)

    match coding_agent:
        case CodingAgent.CLAUDE:
            destination = Path("CLAUDE.md")
            cmd = "claude /init"
            # Settings are only understood by Claude Code
            shutil.copy("data/claude/settings.json", agent_dir / "settings.json")
        case CodingAgent.CODEX:
            destination = Path("AGENTS.md")
            cmd = "codex exec 'Read AGENTS.md and update it'"
        case _:
            raise ValueError(f"Unsupported coding agent: {coding_agent}")

    shutil.copytree("data/skills", agent_dir / "skills")
    logger.info(f"Copied skills to {agent_dir / 'skills'}")

    shutil.copy(source, destination)
    logger.info(f"Copied {source} to {destination}")
    logger.info(f"Run `{cmd}` to finish agent setup.")


def remove_data_dir() -> None:
    """Remove the data directory."""
    shutil.rmtree("data")


def git_initial_commit() -> None:
    """Make the initial commit."""
    call("git add .")
    call("git commit -m Setup")


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


def git_add_remote(remote: str, url: str, protocol: PROTOCOL = "git") -> None:
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
    privacy: str, remote: str = "origin", default_branch: str = DEFAULT_BRANCH
) -> None:
    """Make a repository on GitHub (requires GitHub CLI).

    Args:
        privacy: privacy of the repository ("private", "internal", "public")
        remote: name of the remote to add
        default_branch: name of the default branch for upstream
    Raises:
        ValueError: if privacy option is not valid
    """
    if privacy not in GITHUB_PRIVACY_OPTIONS:
        raise ValueError(f"{privacy=} not in {GITHUB_PRIVACY_OPTIONS}")

    check_program("gh", "https://cli.github.com/")

    try:
        call(
            f"gh repo create {{cookiecutter.package_name}} --{privacy} --remote {remote} --source ."
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating GitHub repository, likely already exists: {e}")

    try:
        call(f"git config branch.{default_branch}.remote {remote}")
        call(f"git config branch.{default_branch}.merge refs/heads/{default_branch}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting upstream to {default_branch}: {e}")


def notes() -> None:
    """Print notes for the user (if hosted on GitHub)."""
    if not "{{cookiecutter.github_username}}":
        return

    print(
        """
If using GitHub, generate a CODECOV_TOKEN at:
https://app.codecov.io/gh/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/settings
and add it to the GitHub repository secrets as CODECOV_TOKEN at:
https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.package_name}}/settings/secrets/actions
"""
    )


SUCCESS = "\x1b[1;32m"
TERMINATOR = "\x1b[0m"


def main() -> None:
    """Run the post generation hooks."""
    set_python_version("{{cookiecutter.python_version}}")
    set_license("{{cookiecutter.license}}")
    git_init()
    update_dependencies()
    allow_direnv()
    git_hooks()
    setup_coding_agent_files("{{cookiecutter.coding_agent}}")
    remove_data_dir()
    git_initial_commit()
    setup_remote("origin")

    notes()

    print(f"{SUCCESS}Project successfully initialized{TERMINATOR}")


if __name__ == "__main__":
    main()
