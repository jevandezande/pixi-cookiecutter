---
name: write-docstrings
description: Writes and reviews Google-style Python docstrings. Use when writing new docstrings, reviewing existing ones, or editing them.
argument-hint: "[directory or file]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Bash
---

# Writing Docstrings

Required for: every module, class, function, and method, tests included. ruff's pydocstyle
rules (`D`, Google convention) fail `ruff check` on a missing public one; a private `_helper`
is not checked, but give it one too.

Describe what the code does now. Do not explain why it changed or recount earlier versions.

## Format: Google style

1. The first line is a one-line summary ending in a period. A function takes the imperative
   ("Return", "Parse", "Write"); a class, a record, or a predicate may take a noun phrase ("One
   pinned toolchain.", "Whether the bundle is relocatable.")
2. A blank line between the summary and anything after it
3. Sections, in this order, when they have something to say: `Args`, `Returns` or `Yields`,
   `Raises`, `Examples`. A class or dataclass lists its fields under `Attributes`
4. No types in a docstring. The annotations carry them, and ty checks them
5. No leading article ("a", "an", "the") in an `Args`, `Attributes`, `Returns`, `Yields`, or
   `Raises` description, and no trailing period. Start lowercase in `Args`, `Attributes`, and
   `Raises`; `Returns` and `Yields` start with a capital
6. Name the unit whenever a value has one: `in seconds`, `in bytes`
7. Give a default only when it is not obvious from the signature and the reader needs it
8. Single backticks for code: `Path`, never ``Path``
9. A continuation line is indented four spaces past the parameter name

`Raises` names the condition, not the act of raising: `ValueError: threshold is negative`, not
`ValueError: raised if ...`.

## Example

```python
def process_spam(input_data: list[tuple[str, int]], threshold: int = 2) -> dict[str, int]:
    """Sum spam counts by category, dropping categories that total below `threshold`.

    Args:
        input_data: category and count pairs; a repeated category is summed, so order does
            not matter
        threshold: smallest total kept

    Returns:
        Mapping of category to total count

    Raises:
        ValueError: threshold is negative

    Examples:
        >>> process_spam([("jalapeno", 5), ("regular", 3), ("jalapeno", 9), ("low sodium", 1)])
        {'jalapeno': 14, 'regular': 3}
    """
```

## Incorrect example (do not do this!)

```python
def process_spam(input_data: list[tuple[str, int]], threshold: int = 2) -> dict[str, int]:
    """spam counts                                         # ❌ lowercase, no period, no verb

    Args:
        input_data (list[tuple[str, int]]): The counts.    # ❌ type, article, period
        threshold: Threshold for the counts.               # ❌ restates the name, period

    Returns:
        dict[str, int]: A dictionary.                      # ❌ type, article, says nothing

    Raises:
        ValueError: Raised if the threshold is negative.   # ❌ describes raising, not the condition
    """
```

## Examples are tests

pytest runs with `--doctest-modules` over every `testpaths` entry in `pyproject.toml`, so every
`Examples` block runs on every pytest run. Write one that:

- shows the call a reader would make, with output they can check by eye
- prints the exact `repr` Python gives: single-quoted strings, full float digits
- runs on any machine, so it needs no network and no file outside the repository

Leave out `Examples` when no small call is that self-contained; do not reach for `# doctest:
+SKIP`.

## Modules, classes, and tests

- **Module:** the first statement of the file, before any import. One sentence on what the
  module holds; a script adds how it is run and where its output goes.
- **Class:** immediately after the `class` line: what an instance is, then `Attributes` for a
  dataclass or `TypedDict`. Invariants belong here; the history of the design does not.
- **Test:** see `write-tests`. The summary says what behavior is checked.

## Miscellaneous

- Prefer Unicode superscripts for single-digit powers, e.g. Å².
- Do not restate the signature: "Takes a float and returns a float" says nothing the reader
  cannot see.
- A docstring is for the caller; a `#` comment is for why the implementation does what it does.
- Never add a `# noqa: D...` or a pydocstyle ignore in `pyproject.toml` without asking.
