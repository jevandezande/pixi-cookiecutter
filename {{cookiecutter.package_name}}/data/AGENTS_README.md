# AI Agent Development Guide

This file provides guidance to AI agents working with code in this repository.
It covers tooling, conventions, and workflows needed to contribute effectively.

## How to use this document

### When to read this file

- First time working on this repository
- Before making any code changes or commits
- When unsure about code conventions or tooling

## AI Skills
{% if cookiecutter.coding_agent != "None" %}
Read the relevant `SKILL.md` files in `.agents/skills/` before making changes. The skills are
`write-code`, `write-docstrings`, `write-tests`, `write-method-docs`, and `cleanup-code`; they cover
coding conventions, documentation, tests, checks, and git workflows.
{%- else %}
TODO: no skills were generated; write the conventions this project follows here.
{%- endif %}

## When in doubt
{% if cookiecutter.coding_agent != "None" %}
- Check the relevant skill files in `.agents/skills/`
{%- endif %}
- Run individual tools to identify issues
- Ask user for clarification on ambiguous requirements

## Repository overview

Purpose: TODO: read from README.md and confirm with the user

Structure:

- `{{cookiecutter.package_name}}/` - source code (this is a flat layout)
- `tests/` - test suite
- `.github/workflows/` - CI/CD (test)
{%- if cookiecutter.coding_agent != "None" %}
- `.agents/skills/` - coding conventions
{%- endif %}
- TODO: list other important folders

Python Version: >={{cookiecutter.python_version}}

Key configuration files:

- `pyproject.toml` - project metadata, dependencies, all tool configuration (ruff, pytest, coverage)
- `prek.toml` - Prek hook configuration
- `.editorconfig` - editor formatting settings
{%- if cookiecutter.coding_agent == "Claude" %}

## Claude Code integration

### Auto-formatting hooks

Claude is configured with PostToolUse hooks that run automatically after Edit or Write operations:

1. `pixi run fmt` - Formats all code
2. `pixi run lint` - Applies auto-fixable linting corrections

File edits trigger automatic formatting — no manual `pixi run fmt` needed. Pre-commit checks still run on commit.

Project defaults live in `.claude/settings.json` (tracked by git); machine-specific overrides
belong in `.claude/settings.local.json` (gitignored).
{%- endif %}

## Pull requests

Follow `.github/pull_request_template.md` for PR descriptions. Fill the applicable sections,
remove empty optional sections, and pass the text to `gh pr create` with `--body-file`.

PRs are squash-merged. Merge with
`gh pr merge N --squash --subject "<title> (#N)" --body-file <file>` (don't use GitHub's default).
The body expresses the net change and why, measurement summaries, known limits, and breaking changes.
Branch history, verification, questions, and follow-ups stay in PR. Small PRs need only subject.
