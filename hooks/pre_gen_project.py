"""Hooks to run before generating the project."""

import keyword
import logging
import re

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("pre_gen_project")

MINIMUM_PYTHON_MINOR_VERSION = 12

MODULE_REGEX = r"[a-zA-Z][_a-zA-Z0-9]+"

# GitHub's rule for user and organization names
GITHUB_USERNAME_REGEX = r"[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}"


def main() -> None:
    """Run the hooks."""
    check_module_name("{{cookiecutter.package_name}}")
    check_line_length("{{cookiecutter.line_length}}")
    check_python_version("{{cookiecutter.python_version}}")
    check_github_username("{{cookiecutter.github_username}}", "{{cookiecutter.github_setup}}")
    check_toml_string("project_name", "{{cookiecutter.project_name}}")
    check_toml_string("author_name", "{{cookiecutter.author_name}}")


def check_line_length(line_length: str) -> None:
    """Check that the line length is an integer.

    Args:
        line_length: line length to check

    Raises:
        ValueError: if the line length is not an integer or is too short

    Examples:
        >>> check_line_length("100")
        >>> check_line_length("60")
        Traceback (most recent call last):
        ...
        ValueError: line_length='60' is too short (80 is the minimum).
        >>> check_line_length("abc")
        Traceback (most recent call last):
        ...
        ValueError: line_length='abc' is not an integer.
    """
    try:
        length = int(line_length)
    except ValueError as e:
        raise ValueError(f"{line_length=} is not an integer.") from e

    if length < 80:
        raise ValueError(f"{line_length=} is too short (80 is the minimum).")


def check_python_version(python_version: str) -> None:
    """Check that the python version is a supported `major.minor` version.

    Args:
        python_version: python version to check

    Raises:
        ValueError: if the version is not a `major.minor` version of Python 3

    Examples:
        >>> check_python_version("3.14")
        >>> check_python_version("3.14.2")
        Traceback (most recent call last):
        ...
        ValueError: python_version='3.14.2' is not a 'major.minor' version (e.g. 3.14).
        >>> check_python_version("abc")
        Traceback (most recent call last):
        ...
        ValueError: python_version='abc' is not a 'major.minor' version (e.g. 3.14).
        >>> check_python_version("2.7")
        Traceback (most recent call last):
        ...
        ValueError: python_version='2.7' is not supported; Python 3 is required.
    """
    try:
        major, minor = (int(part) for part in python_version.split("."))
    except ValueError as e:
        raise ValueError(f"{python_version=} is not a 'major.minor' version (e.g. 3.14).") from e

    if major != 3:
        raise ValueError(f"{python_version=} is not supported; Python 3 is required.")

    if minor < MINIMUM_PYTHON_MINOR_VERSION:
        logger.warning(f"{python_version=} should be upgraded to the latest available python.")


def check_github_username(github_username: str, github_setup: str) -> None:
    """Check the GitHub username, which is required when GitHub setup is requested.

    A blank username otherwise yields a malformed remote (e.g. `git@github.com:/package`), and
    `gh repo create` needs the owner it qualifies the new repository with.

    Args:
        github_username: GitHub username
        github_setup: privacy of the GitHub repository to create (or "None")

    Raises:
        ValueError: if a repository is requested without a username, or the username is not one
            GitHub would accept

    Examples:
        >>> check_github_username("octocat", "private")
        >>> check_github_username("my-org", "internal")
        >>> check_github_username("", "None")
        >>> check_github_username("", "private")
        Traceback (most recent call last):
        ...
        ValueError: github_username is required when github_setup='private'.
        >>> check_github_username("-octocat", "None")
        Traceback (most recent call last):
        ...
        ValueError: github_username='-octocat' is not a valid GitHub user or organization name.
    """
    if not github_username:
        if github_setup != "None":
            raise ValueError(f"github_username is required when {github_setup=}.")
        return

    if not re.fullmatch(GITHUB_USERNAME_REGEX, github_username):
        raise ValueError(f"{github_username=} is not a valid GitHub user or organization name.")


def check_toml_string(name: str, value: str) -> None:
    r"""Check that a value survives being written into a basic TOML string.

    `project_name` (the package description) and `author_name` both land in `pyproject.toml`
    between double quotes, unescaped, and `author_name` also lands in `LICENSE`.

    Args:
        name: option being checked, for the error message
        value: option value to check

    Raises:
        ValueError: if the value contains a character that would break `pyproject.toml`

    Examples:
        >>> check_toml_string("author_name", "")
        >>> check_toml_string("author_name", "Jane Doe")
        >>> check_toml_string("project_name", 'Spam "Deluxe"')
        Traceback (most recent call last):
        ...
        ValueError: project_name cannot contain quotes or backslashes.
        >>> check_toml_string("author_name", "Jane \\ Doe")
        Traceback (most recent call last):
        ...
        ValueError: author_name cannot contain quotes or backslashes.
    """
    if set(value) & {'"', "\\"}:
        raise ValueError(f"{name} cannot contain quotes or backslashes.")


def check_module_name(module_name: str) -> None:
    """Check if the module name is a valid Python module name.

    Args:
        module_name: name of the module to check

    Raises:
        ValueError: if module name is not a valid Python module name

    Examples:
        >>> check_module_name("valid_module_name")
        >>> check_module_name("valid_module_name2")
        >>> check_module_name("invalid module name")
        Traceback (most recent call last):
        ...
        ValueError: module_name='invalid module name' is not a valid Python module name.
        >>> check_module_name("")
        Traceback (most recent call last):
        ...
        ValueError: Module name cannot be empty.
        >>> check_module_name("class")
        Traceback (most recent call last):
        ...
        ValueError: module_name='class' is a Python keyword and cannot be used as a module name.
    """
    if not module_name:
        raise ValueError("Module name cannot be empty.")

    if module_name in keyword.kwlist:
        raise ValueError(f"{module_name=} is a Python keyword and cannot be used as a module name.")

    if not re.fullmatch(MODULE_REGEX, module_name):
        raise ValueError(f"{module_name=} is not a valid Python module name.")


if __name__ == "__main__":
    main()
