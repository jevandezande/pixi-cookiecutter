---
name: cleanup-code
description: Polishes recently written or modified Python code for style, dead code, docstrings, type annotations, and checks. Use when coding task is completed.
argument-hint: [directory or file]
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Bash
---

Do a final cleanup polish pass on the code in $ARGUMENTS (or the current package if no argument given).

Use the `write-code` skill to understand code conventions.

1. Re-read every file that was created or modified.
2. Check for Pythonic style:
   - Use comprehensions instead of loops where clearer
   - Use f-strings instead of `.format()` or `%`
   - Use `pathlib` instead of `os.path`
   - Use dataclasses or named tuples for structured data
3. Remove dead code, unused imports, and commented-out code
4. Remove unecessary tests, such as one that simply check types or were used for development
5. Verify docstrings on all public APIs (follow `write-docstrings` skill conventions).
6. Verify complete type annotations on all public functions and methods.
7. Run the full check suite:
   - `ruff format .`
   - `ruff check .`
   - `ty check`
   - `pytest`
8. All checks must pass before finishing.
