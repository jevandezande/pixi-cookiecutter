---
name: write-docstrings
description: Write or review docstrings for code in this repo. Use when writing new docstrings, reviewing existing docstrings, or editing docstrings.
argument-hint: "[source code]"
---

# Writing Docstrings

Required for: all public modules, classes, functions, and methods

## Format: Google-style

1. Do not place type information in docstrings - use type annotations only
2. Do not use leading articles in parameter, return, and error descriptions "a", "an", or "the"
3. Only use single backticks (e.g. `Spam`, not ``Spam``)

## Example
```python
def process_spam(input_data: list[tuple[str, int]], threshold: int = 2) -> dict[str, int]:
    """Process spam counts, dropping those below threshold

    Args:
        input_data: spam counts to process
        threshold: minimum count threshold for inclusion

    Returns:
        Mapping of categories to counts

    Raises:
        ValueError: threshold is negative

    Examples:
        >>> process_spam([("jalapeno", 5), ("regular", 3), ("jalapeno", 9), ("low sodium", 1)], 2)
        {"jalapeno": 14, "regular": 3}
    """
```

## Incorrect example (do not do this!)
```python
def process_spam(input_data: list[tuple[str, int]], threshold: int = 2) -> dict[str, int]:
    """Process spam counts, dropping those below threshold

    Args:
        input_data (list[str]): A list of spam counts to process.  # ❌ Has type and article
        threshold (int): A minimum count threshold for inclusion.  # ❌ Has type and article

    Returns:
        dict[str, int]: A dictionary mapping categories.       # ❌ Has type and article
    """
```

## Module and class docstrings

- **Module docstrings:** single sentence describing the module's purpose; placed at the top of the file before any imports.
- **Class docstrings:** describe the class's purpose and any important attributes or invariants; placed immediately after the `class` line.

## Miscellaneous

- Prefer Unicode superscripts for single digit superscripts, e.g. Å²
- Never add ignores to the `pyproject.toml` formatting, linting, or type checking without explicitly asking
