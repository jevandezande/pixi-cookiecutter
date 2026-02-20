# AI Agent Development Guide

This document provides essential guidance for AI agents working on this repository. It covers tooling, conventions, and workflows needed to contribute effectively.

## How to use this document

### When to read this file
- First time working on this repository
- Before making any code changes or commits
- When unsure about code conventions or tooling

### Understanding {AGENT: ...} directives
- Directives in curly braces starting with "AGENT:" are instructions for you
- Execute these directives when first reading this file
- Update the file with the actual information, replacing the directive
- Directives marked with "must" are required; others are recommended
- Note: This file was generated from a cookiecutter template and pre-filled some configuration, do not treat this as a template, but as the start of a new project, and ask questions where needed to clarify

## Initial setup checklist
1. {AGENT: You will be updating this file, do not stray from directives, do not simplify, do not delete, only improve the file}
2. {AGENT: Read README.md and confirm project purpose with user}
3. {AGENT: Ask for the ability to run necessary development commands, including `git commit`, `prek -a`, `pixi install`, `python`}
4. {AGENT: Verify `pixi install` has been run - check for `.pixi/` directory or run `pixi install`}
5. {AGENT: Verify prek hooks are installed - run `git config --get core.hooksPath` (should be empty/default) or check `.git/hooks/pre-commit` exists}
6. {AGENT: Read pyproject.toml and update repository-specific information below}
7. {AGENT: Run all checks once to verify environment: `prek -a`}
8. {AGENT: After completing setup, notify user of any discrepancies found}
9. {AGENT: Delete this initial setup checklist and the ### Understanding {AGENT: ...} directives section}

## Before every commit
- Ensure all code has type annotations
- Add Google-style docstrings (NO types, NO leading articles)
- Run checks: `prek -a`
- Pre-commit hooks will run automatically and must pass

## When in doubt
- Check code conventions section below
- Run individual tools to identify issues
- Ask user for clarification on ambiguous requirements

## Code conventions

### Docstrings

Required for: all public modules, classes, functions, and methods

#### Format: Google-style
1. Do not place type information in docstrings - use type annotations only
2. Do not use leading articles in parameter, return, and error descriptions "a", "an", or "the"

##### Section order
1. Args
2. Returns
3. Raises
4. Yields
5. Examples
6. Note
7. Warning

#### Example
```python
def process_data(input_data: list[str], threshold: int = 10) -> dict[str, int]:
    """Process input data and return summary statistics.

    Args:
        input_data: strings to process
        threshold: minimum count threshold for inclusion

    Returns:
        Mapping of categories to counts

    Examples:
        >>> process_data(["a", "b"], 5)
        {"valid": 2}
    """
```

#### Incorrect example (do not do this!)
```python
def process_data(input_data: list[str], threshold: int = 10) -> dict[str, int]:
    """Process input data and return summary statistics.

    Args:
        input_data (list[str]): A list of strings to process.  # ❌ Has type and article
        threshold (int): A minimum count threshold.            # ❌ Has type and article

    Returns:
        dict[str, int]: A dictionary mapping categories.       # ❌ Has type and article
    """
```

### Type annotations

Requirements
- All functions must have complete type annotations
- Use modern syntax: `list[str]`, `dict[str, int]` (not `List[str]`, `Dict[str, int]`)
- Use `|` for union types (Python 3.10+): `str | None`
- Import types from `typing` only when necessary (prefer built-ins)

#### Verification
```bash
pixi run types
```

### Code formatting

Via ruff
- Line length: {AGENT: read from pyproject.toml; defaults to 100}
- Indentation: 4 spaces (no tabs except Makefiles)
- Encoding: UTF-8
- Line endings: LF (Unix-style)
- Trailing newline: required
- No trailing whitespace

### Naming conventions
- Functions/methods: snake_case
- Variables: snake_case
- Constants: UPPER_SNAKE_CASE
- Classes: PascalCase
- Modules: snake_case
- Private attributes/methods: _leading_underscore

### Imports
- Absolute imports preferred
- Group imports: standard library, third-party, local
- No wildcard imports (`from module import *`) except in `__init__.py`
- Import sorting handled by ruff (isort)

### Error handling
- Use specific exceptions (ValueError, OSError, etc.) rather than generic Exception
- Avoid bare `except:` clauses; catch specific exceptions
- Use context managers (`with` statements) for resource management
- Log errors appropriately using the `logging` module
- Raise custom exceptions for domain-specific errors

### General style
- Use f-strings for string formatting (Python 3.6+)
- Prefer list/dict comprehensions over loops when appropriate
- Use `pathlib.Path` for file operations instead of `os.path`
- Avoid global variables; use dependency injection
- Write readable code; prefer explicit over implicit

## Repository overview

Purpose: {AGENT must read from README.md and confirm with user}

Structure:
- `{{cookiecutter.package_name}}` - source code (this is a flat layout)
- `tests/` - test suite
- `.github/workflows/` - CI/CD configuration
- {AGENT: list other important folders and confirm with user}

Python Version: {AGENT: read from pyproject.toml}

Key configuration files:
- `pyproject.toml` - Project metadata, dependencies, all tool configuration
- `prek.toml` - Prek hook configuration
- `.coveragerc` - Test coverage settings
- `.editorconfig` - Editor formatting settings

## Essential commands

```bash
# Setup
pixi install                    # Install dependencies
prek install                    # Install git hooks

# Code quality
pixi run fmt                         # Format code
pixi run lint                        # Lint code
pixi run types                       # Type check

# Testing
pixi run test                   # Run tests
pixi run test --cov             # Run tests with coverage
pixi run test -k "pattern"      # Run test matching pattern
pixi run test -v                # Verbose output

# Prek (pre-commit replacement)
prek -a                         # Run all hooks
prek run <hook-id>              # Run specific hook

# Git workflow
git add .
git commit -m "feat: message"   # Hooks run automatically

# Package management
pixi add <package>                # Add a package
pixi add --dev <package>          # Add a package to dev
pixi lock                         # Check the lockfile matches the pyproject.toml (and update if different)
pixi update                       # Update all packges in the lockfile
pixi tree                         # Print the dependencies tree
```

## Development environment

Install dependencies:
```bash
pixi install
```

Install prek hooks:
```bash
prek install
```

Verify environment:
```bash
python --version
prek -a
```

## Dependency management notes

{AGENT: If CLAUDE, keep this Claude Code integration section, else delete}
## Claude Code integration

This project includes Claude Code configuration for AI-assisted development.

### Configuration files

- `.claude/settings.local.json` - Claude permissions and hooks

### Auto-formatting hooks

Claude is configured with PostToolUse hooks that run automatically after Edit or Write operations:
1. `pixi run ruff format .` - Formats all code
2. `pixi run ruff check . --fix` - Applies auto-fixable linting corrections

Effect: When Claude modifies files, formatting and basic lints are applied immediately, reducing pre-commit friction.

To modify permissions, edit `.claude/settings.local.json`.

### Workflow impact

1. File edits trigger automatic formatting - no manual `pixi run ruff format` needed
2. Pre-commit checks still run on commit - hooks are complementary, not redundant
3. Permissions reduce interruptions for common development commands

## Direnv integration

This project uses direnv for automatic virtual environment activation.

### Behavior

When entering the project directory:
1. Checks if `pixi.lock` has changed
2. Runs `pixi shell-hook -e dev` to activate the dev environment automatically

### Setup

Direnv was configured during project initialization. If you encounter "direnv: error" messages:

```bash
direnv allow .
```

This grants permission for direnv to run the `.envrc` script in this directory.

## Code quality tools

### Ruff (formatting & linting)

Enabled rule categories:
- `B` - bugbear (common bugs and design problems)
- `D` - pydocstyle (docstring conventions)
- `E`/`W` - pycodestyle (PEP 8 style errors and warnings)
- `F` - pyflakes (logical errors)
- `I` - isort (import sorting)
- `N` - pep8-naming (naming conventions)
- `C4` - comprehensions (list/dict/set comprehension improvements)
- `PL` - pylint (code quality and error detection)
- `PT` - pytest-style (pytest best practices)
- `PIE` - misc lints (miscellaneous improvements)
- `PYI` - flake8-pyi (stub file best practices)
- `TID` - tidy imports (import hygiene)
- `TCH` - type-checking imports (TYPE_CHECKING block enforcement)
- `RUF` - Ruff-specific rules
- `RSE` - flake8-raise (exception raising improvements)
- `ICN001` - unconventional import aliases

Ignored rules (globally):
- `N806` - Non-lowercase variable in function (allows PascalCase variables)
- `PLR0911` - Too many return statements
- `PLR0912` - Too many branches
- `PLR0913` - Too many arguments to function call
- `PLR0914` - Too many local variables
- `PLR0915` - Too many statements
- `PLR1702` - Too many nested blocks

Per-file ignores:
- `__init__.py`:
  - `F401` - Unused imports (common for `__all__` exports)
  - `F403` - `from module import *` (acceptable in `__init__.py`)

Configuration: `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.lint]`

### Ty (type checking)

Requirements:
- All functions must have complete type annotations
- Modern syntax required (e.g., `list[str]` not `List[str]`)

### Pytest (testing)

Configuration:
- Test paths:
  - `tests/` - Unit and integration tests
  - `{{cookiecutter.package_name}}` - Source code (for doctests)
- Doctests: Enabled automatically via `--doctest-modules` flag
- Doctest normalization: `NORMALIZE_WHITESPACE` applied to all doctests (allows flexible spacing in examples)

Both test files in `tests/` and docstring examples in source code are automatically discovered and run

## Testing

### Test structure

- Location: `tests/` directory
- Naming: test files must start with `test_`
- Doctests: automatically discovered in source code

### Doctests

Include examples in docstrings:
```python
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: first integer
        b: second integer

    Returns:
        Sum of a and b

    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
    """
    return a + b
```

### Coverage configuration

{AGENT: read .coveragerc and update configuration summary here}

- Source: `{{cookiecutter.package_name}}`
- Omitted: `{{cookiecutter.package_name}}/__main__.py`
- Excluded lines: `pragma: no cover`, `__repr__`, `if self.debug`, `raise AssertionError`, `raise NotImplementedError`, `if 0:`, `if __name__ == "__main__":`, ellipsis-only lines (`...`)

## Prek hooks

Configuration: `prek.toml`

Hooks enabled:
{AGENT: read prek.toml and update list of hooks with ids and versions here}

1. check-yaml - Validate YAML syntax
2. check-toml - Validate TOML syntax
3. end-of-file-fixer - Ensure single newline at EOF
4. trailing-whitespace - Remove trailing whitespace
5. ruff-format - Format Python code
6. ruff-check - Lint Python code
7. ty - Type check Python code
8. pytest - Run test suite

Behavior:
- Stages: `pre-commit` and `pre-push`
- All hooks use `pass_filenames: false` (process entire project)
- Hooks must pass before commit succeeds
- Some hooks auto-fix issues (formatting, whitespace)

Manual execution:
```bash
prek -a                 # All hooks
prek run ruff-check     # Specific hook
```

## CI/CD

File: `.github/workflows/test.yml`

Triggers:
- All pull requests
- Pushes to `master` branch

Test matrix:
{AGENT: read from .github/workflows/test.yml and update the test matrix here}

- Python versions: 3.14
- Operating systems: ubuntu-latest
- Total combinations: 1 (single configuration)

Note: Matrix is intentionally minimal; expand if multi-version testing is needed.

Checks performed:
1. `pixi run fmt` - format check
2. `pixi run lint` - lint check
3. `pixi run types` - type check
4. `pixi run test --cov --cov-report=xml` - tests with coverage
5. Upload coverage to Codecov

Ensure local checks pass before pushing to avoid CI failures.

## Troubleshooting

### Pre-commit hook failures

Formatting issues:
- Usually auto-fixed by ruff
- Re-stage files: `git add .`
- Try committing again

Lint issues:
- Read error message for specific rule
- Fix; if `# noqa: <rule>` if absolutely necessary, ask before adding

Type issues:
- Add missing type annotations
- Fix type mismatches
- Use `pixi run types` to verify locally

Test failures:
- Fix failing tests or code
- Run `pixi run test -v` for detailed output
- Run specific test: `pixi run test hooks/test_file.py::test_name`

## Commit guidelines

Format: conventional commits recommended
- `feat:` - new features
- `fix:` - bug fixes
- `docs:` - documentation changes
- `test:` - test changes
- `refactor:` - code refactoring
- `chore:` - maintenance tasks

### Example
```bash
git commit -m "feat: add user authentication

- Implement JWT token generation
- Add login/logout endpoints
- Include comprehensive tests"
```

## Additional resources

- pixi documentation: https://pixi.sh
- ruff documentation: https://docs.astral.sh/ruff
- ty documentation: https://github.com/astral-sh/ty
- pytest documentation: https://docs.pytest.org
- prek documentation: https://prek.j178.dev
- Google docstring style: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
