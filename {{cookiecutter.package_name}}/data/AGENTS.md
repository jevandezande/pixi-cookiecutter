# AI Agent Development Guide

This file covers the tooling, conventions, and workflows a contributor needs. Read it before
changing code or committing.

Keep it current: when you add a top-level directory or a configuration file, update the matching
section in the same change.

## AI Skills

This project ships agent skills in `.agents/skills/`, where Codex reads them. Claude Code reads
`.claude/skills/`, a symlink to `.agents/skills/`; edit skills through `.agents/skills/`. Load
`write-code`, `write-docstrings`, `write-tests`, `write-method-docs`, and `cleanup-code` for
detailed instructions on conventions, formatting, tests, and git workflows. Do not make code
changes without consulting the relevant skills.

## When in doubt

- Check the relevant skills in `.agents/skills/`
- Run individual tools to identify issues
- Ask user for clarification on ambiguous requirements

## Repository overview

Purpose: not yet written; ask the user and record it here

Structure:

- `{{cookiecutter.package_name}}/` - source code (this is a flat layout)
- `tests/` - test suite
- `.github/workflows/` - CI/CD (test)
- `.agents/skills/` - agent skills
- `.claude/` - Claude Code settings and hooks; `.claude/skills/` is a symlink to `.agents/skills/`
- `.codex/` - Codex hooks

Python Version: >={{cookiecutter.python_version}}

Key configuration files:

- `pyproject.toml` - project metadata, dependencies, all tool configuration (ruff, pytest, coverage)
- `prek.toml` - Prek hook configuration
- `.editorconfig` - editor formatting settings

## Agent hooks

Claude Code (`.claude/settings.json`) and Codex (`.codex/hooks.json`) each run `pixi run fmt`
and `pixi run lint` after every file edit, so edits need no manual `pixi run fmt`. Keep the two
hooks identical. Codex runs a project hook only once the project is trusted and the hook approved
in `/hooks`. Pre-commit checks still run on commit.

Claude Code's `attribution` setting is empty, so its commits and PRs carry no agent trailer.
Machine-local Claude Code overrides go in `.claude/settings.local.json` (gitignored).

## Pull requests

Follow `.github/pull_request_template.md` for PR descriptions. Fill the applicable sections,
remove empty optional sections, and pass the text to `gh pr create` with `--body-file`.

PRs are squash-merged. Merge with
`gh pr merge N --squash --subject "<title> (#N)" --body-file <file>` (don't use GitHub's default).
The body expresses the net change and why, measurement summaries, known limits, and breaking changes.
Branch history, verification, questions, and follow-ups stay in PR. Small PRs need only subject.
