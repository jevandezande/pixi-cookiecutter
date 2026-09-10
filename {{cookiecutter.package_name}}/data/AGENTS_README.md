# AI Agent Development Guide

This file provides guidance to AI agents working with code in this repository.
It covers tooling, conventions, and workflows needed to contribute effectively.

## How to use this document

### When to read this file

- First time working on this repository
- Before making any code changes or commits
- When unsure about code conventions or tooling

## AI Skills
{% if cookiecutter.coding_agent == "Claude" %}
This project uses Claude Skills. Use the `skill` tool to load `write-code`, `write-docstrings`, and `write-tests` for detailed instructions on conventions, formatting, tests, and git workflows. Do not make code changes without consulting the relevant skills.
{% else %}
Conventions live in `.agent/skills/<name>/SKILL.md`. Read `write-code`, `write-docstrings`, and `write-tests` for detailed instructions on conventions, formatting, tests, and git workflows. Do not make code changes without consulting the relevant skills.
{% endif %}
## When in doubt
{% if cookiecutter.coding_agent == "Claude" %}
- Check the skills loaded via the `skill` tool
{%- else %}
- Check the skills in `.agent/skills/`
{%- endif %}
- Run individual tools to identify issues
- Ask user for clarification on ambiguous requirements

## Repository overview

Purpose: TODO: read from README.md and confirm with the user

Structure:

- `{{cookiecutter.package_name}}/` - source code (this is a flat layout)
- `tests/` - test suite
- `.github/workflows/` - CI/CD (test)
- `{% if cookiecutter.coding_agent == "Claude" %}.claude{% else %}.agent{% endif %}/skills/` - coding conventions
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
