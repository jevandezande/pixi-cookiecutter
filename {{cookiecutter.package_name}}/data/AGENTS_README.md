# AI Agent Development Guide

This file provides guidance to AI agents working with code in this repository.
It covers tooling, conventions, and workflows needed to contribute effectively.

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

## AI Skills

This project uses Claude Skills. Use the `skill` tool to load `write-code`, `write-docstrings`, and `write-tests` for detailed instructions on conventions, formatting, tests, and git workflows. Do not make code changes without consulting the relevant skills.

## When in doubt
- Check the skills loaded via the `skill` tool
- Run individual tools to identify issues
- Ask user for clarification on ambiguous requirements

## Repository overview

Purpose: {AGENT must read from README.md and confirm with user}

Structure:
- `{{cookiecutter.package_name}}/` - source code (this is a flat layout)
- `tests/` - test suite
- `.github/workflows/` - CI/CD (test)
- {AGENT: list other important folders and confirm with user}

Python Version: {AGENT: read from pyproject.toml}

Key configuration files:
- `pyproject.toml` - project metadata, dependencies, all tool configuration
- `prek.toml` - Prek hook configuration
- `.coveragerc` - test coverage settings
- `.editorconfig` - editor formatting settings

{AGENT: If CLAUDE, keep this Claude Code integration section, else delete}
## Claude Code integration

### Auto-formatting hooks

Claude is configured with PostToolUse hooks that run automatically after Edit or Write operations:
1. `pixi run fmt` - Formats all code
2. `pixi run lint` - Applies auto-fixable linting corrections

File edits trigger automatic formatting — no manual `pixi run fmt` needed. Pre-commit checks still run on commit.

To modify permissions, edit `.claude/settings.local.json`.

### Workflow impact

1. File edits trigger automatic formatting - no manual `pixi run fmt` needed
2. Pre-commit checks still run on commit - hooks are complementary, not redundant
3. Permissions reduce interruptions for common development commands
