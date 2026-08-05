---
name: write-docstrings
description: Writes and reviews docstrings in this repo. Use when writing new docstrings, reviewing existing docstrings, or editing docstrings.
argument-hint: "[source code]"
---

# Writing Docstrings

Required for: all public modules, classes, functions, and methods

## Format: Google-style

1. First line is a simple summary in imperative or indicative mood, ending in a period
2. Use sections when relevant: `Args`, `Returns`, `Raises`, `Examples`
3. Do not place type information in docstrings, use type annotations only
4. Do not use leading articles in parameter, return, and error descriptions "a", "an", or "the"
5. Only use single backticks (e.g. `Spam`, not ``Spam``)

## Example

```python
def process_spam(input_data: list[tuple[str, int]], threshold: int = 2) -> dict[str, int]:
    """Process spam counts, dropping those below threshold.

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
    """spam counts, dropping those below threshold                 # ❌ Missing trailing period, needs sentence case, should be in imperative or indicative mood

    Args:
        input_data (list[str]): A list of spam counts to process.  # ❌ Has type, article, and unnecessary trailing period
        threshold (int): Minimum count threshold for inclusion     # ❌ Has type, article, and sentence-case description

    Returns:
        dict[str, int]: A dictionary mapping categories.           # ❌ Has type, article, and unnecessary trailing period
    """
```

## Module and class docstrings

- **Module docstrings:** single sentence describing the module's purpose; placed at the top of the file before any imports.
- **Class docstrings:** describe the class's purpose and any important attributes or invariants; placed immediately after the `class` line.

## Miscellaneous

- Prefer Unicode superscripts for single digit superscripts, e.g. Å²
- Never add ignores to the `pyproject.toml` formatting, linting, or type checking without explicitly asking
