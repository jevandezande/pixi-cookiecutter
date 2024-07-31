"""Hooks for setting up project once generated."""

import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from typing import Any, Literal

logger = logging.Logger("post_gen_project_logger")
logger.setLevel(logging.INFO)


PROTOCOL = Literal["git", "https"]
GITHUB_PRIVACY_OPTIONS = ["private", "internal", "public"]
MINUMUM_PYTHON_MINOR_VERSION = 12


def call(*inputs: str, **kwargs: Any) -> None:
    """
    Call shell commands.

    :param inputs: commands to call
    :param kwargs: keyword arguments to pass to subprocess.check_call

    Warning: strings with spaces are not yet supported.
    """
    for input in inputs:
        logger.debug(f"Calling: {input}")
        subprocess.check_call(input.split(), **kwargs)


def set_python_version() -> None:
    """Set the python version in pyproject.toml and .github/workflows/test.yml."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    logger.info(f"Settting {python_version=}")
    if sys.version_info.minor < MINUMUM_PYTHON_MINOR_VERSION:
        logger.warn(f"{python_version=} should be upgraded to the latest avaiable python version.")

    file_names = [
        ".github/workflows/test.yml",
        "pyproject.toml",
    ]

    for file_name in file_names:
        with open(file_name) as f:
            contents = f.read().replace("{python_version}", python_version)
        with open(file_name, "w") as f:
            f.write(contents)


def set_license(license: str | None = "MIT") -> None:
    """
    Copy the licese file to LICENSE (if any).

    :param license: name of the license (or None for no license)
    """
    if not license or license == "None":
        logger.debug("No license set")
        return

    license = license.lower()
    licenses = [lic.name for lic in Path("licenses").iterdir()]
    if license not in licenses:
        raise ValueError(f"{license=} is not available yet. Please select from:\n{licenses=}")

    shutil.copy(f"licenses/{license}", "LICENSE")

    with open("LICENSE") as f:
        contents = f.read().replace("{year}", f"{datetime.now().year}")
        contents = contents.replace("{author_name}", "{{cookiecutter.author_name}}")
    with open("LICENSE", "w") as f:
        f.write(contents)

    logger.debug(f"Set {license=}")


def remove_license_dir() -> None:
    """Remove the licenses directory."""
    rmtree("licenses")


def git_init() -> None:
    """Initialize a git repository."""
    call("git init")


def process_dependency(dependency: str) -> str:
    """
    Process a dependency.

    :param dependency: dependency to process

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
    r"""
    Process a space separated list of dependencies.

    :param deps: dependencies to process

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

    with open("pyproject.toml") as f:
        contents = (
            f.read()
            .replace("{pixi_dependencies}\n", dependencies)
            .replace("{pixi_test_dependencies}\n", dev_dependencies)
        )
    with open("pyproject.toml", "w") as f:
        f.write(contents)

    call("pixi update")


def check_program(program: str, install_str: str) -> None:
    """
    Check that a program is installed.

    >>> check_program("python", "https://www.python.org/")
    >>> check_program("this_program_does_not_exist", "nothing")
    Traceback (most recent call last):
    ...
    OSError: this_program_does_not_exist is not installed; install with `nothing`
    """
    try:
        call(program, stdout=subprocess.DEVNULL)
    except FileNotFoundError as e:
        raise OSError(f"{program} is not installed; install with `{install_str}`") from e
    except subprocess.CalledProcessError as e:
        raise OSError(f"Issue with {program} encountered") from e


def allow_direnv() -> None:
    """Allow direnv."""
    check_program("direnv", "pixi global install direnv")
    call("direnv allow .")


def git_hooks() -> None:
    """Install pre-commit and pre-push hooks."""
    check_program("pre-commit", "pixi global install pre-commit")
    call("pixi run pre-commit install")


def git_initial_commit() -> None:
    """Make the initial commit."""
    call("git add .", "git commit -m Setup")


def git_add_remote(remote: str, url: str, protocol: PROTOCOL = "git") -> None:
    """
    Add a remote to the git repository.

    :param remote: name for the remote
    :param url: url of remote
    :param protocol: protocol of the remote ("git" or "https")
    """
    if protocol == "git":
        _, _, hostname, path = url.split("/", 3)
        url = f"{protocol}@{hostname}:{path}"

    call(f"git remote add {remote} {url}")


def github_setup(privacy: str, remote: str) -> None:
    """
    Make a repository on GitHub (requires GitHub CLI).

    :param privacy: privacy of the repository ("private", "internal", "public")
    """
    if privacy not in GITHUB_PRIVACY_OPTIONS:
        raise ValueError(f"{privacy=} not in {GITHUB_PRIVACY_OPTIONS}")

    check_program("gh", "https://cli.github.com/")

    call(f"gh repo create {{cookiecutter.package_name}} --{privacy} --remote {remote} --source .")
    call(f"git branch --set-upstream-to={remote} master")


def notes() -> None:
    """Print notes for the user."""
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
    set_python_version()
    set_license("{{cookiecutter.license}}")
    remove_license_dir()
    git_init()
    update_dependencies()
    allow_direnv()
    git_hooks()
    git_initial_commit()
    git_add_remote("origin", "{{cookiecutter.project_url}}")

    if "{{cookiecutter.github_setup}}" != "None":  # type: ignore [comparison-overlap]  # noqa: PLR0133
        github_setup("{{cookiecutter.github_setup}}", "origin")

    notes()

    print(f"{SUCCESS}Project successfully initialized{TERMINATOR}")


if __name__ == "__main__":
    main()
