"""Hooks to run before generating the project."""

import keyword
from re import match


def main() -> None:
    """Run the hooks."""
    check_module_name("{{cookiecutter.package_name}}")


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

    MODULE_REGEX = r"^[a-zA-Z][_a-zA-Z0-9]+$"
    if not match(MODULE_REGEX, module_name):
        raise ValueError(f"{module_name=} is not a valid Python module name.")


if __name__ == "__main__":
    main()
