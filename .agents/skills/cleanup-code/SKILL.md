---
name: cleanup-code
description: Polishes recently written Python for style, dead code, docstrings, type annotations, and checks. Use when a coding task is done.
argument-hint: "[directory or file]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Bash
---

# Cleaning Up Code

Do a final cleanup pass on the code in $ARGUMENTS (or the current package if no argument is given).
Focus on the changed code and the project gate rather than rerunning every tool after every edit.

Use the `write-code` skill to understand code conventions, `write-tests` for tests, and
`write-docstrings` for docstrings.

Review the diff for:

- Dead code, unused imports, commented-out code, and avoidable complexity.
- Loops that read better as comprehensions, `.format()` or `%` instead of f-strings, `os.path`
  instead of `pathlib`, and loose tuples or dicts that should be dataclasses.
- Temporary tests, and tests that do not protect lasting behavior.
- Public APIs whose names, errors, type annotations, or docstrings are unclear or incomplete.

Check changed public items against `write-docstrings`. Run `prek run -a --stage pre-push` as the
final local gate. It covers formatting, linting, type checking, markdown, and tests. Run a
narrower check again only when its failure or a later edit calls for it. Report any check that
could not run.
