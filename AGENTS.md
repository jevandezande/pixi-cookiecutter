# AI Agent Development Guide

This document provides essential guidance for AI agents working on this repository.
It covers tooling, conventions, and workflows needed to contribute effectively.

## How to use this document

### When to read this file

- First time working on this repository
- Before making any code changes or commits
- When unsure about code conventions or tooling

## AI Skills

This project uses Claude Skills. You must use the `skill` tool to load `write-code`, `write-docstrings`, `write-tests`, `write-method-docs`, and `cleanup-code` for detailed instructions on conventions, formatting, tests, and git workflows. Do not make code changes without consulting the relevant skills.

## When in doubt

- Check the skills loaded via the `skill` tool
- Run individual tools to identify issues
- Ask user for clarification on ambiguous requirements

## Repository overview

Purpose: Cookiecutter template for pixi-based Python projects.

Structure:

- `{{cookiecutter.package_name}}/` - cookiecutter template root (generated project)
  - `data/` - post-gen hook staging data, deleted from the generated project
  - `data/AGENTS_README.md` - the `AGENTS.md` every generated project gets
  - `data/skills/` - skills copied to `.claude/skills/` when an agent is set up
- `hooks/` - cookiecutter hooks and tests
- `.github/workflows/` - CI/CD configuration
- `notes.md` - setup notes and optional tools
- `template_config.yml` - example cookiecutter configuration

Python Version: >=3.13

## Rendering

`hooks/` is rendered, so `post_gen_project.py` embeds `{{cookiecutter.*}}` in string literals and
in default arguments. Functions that need a cookiecutter value take it as a parameter, so tests
can pass their own.

`_copy_without_render` covers `.github/workflows`, because GitHub Actions `${{ ... }}` collides
with Jinja. Anything else under the template root is rendered.

Placeholders the post-gen hook fills (`{python_version}`, `{pixi_dependencies}`,
`{pixi_test_dependencies}`)
go through `read_write`, which raises when the placeholder is absent rather than leaving the file
untouched.

## Testing

`test_template_renders_to_well_formed_files` renders every template file for each option
combination and parses the TOML, JSON, and Python. It is the only local check that an edit did not
take a Jinja tag with it, since the root `prek.toml` has to exclude the template's `pyproject.toml`
from `check-toml`.

Full generation is not side-effect free; when `github_setup` is not `"None"`, `gh repo create` is
run, which creates a repository on GitHub. CI generates projects with `github_setup=None` only.

Key configuration files:

- `pyproject.toml` - Project metadata, dependencies, pixi environments and tasks, all tool configuration (ruff, pytest, coverage)
- `prek.toml` - Prek hook configuration
- `.editorconfig` - Editor formatting settings

## Miscellaneous

Agents are banned from being an author on commits or PR messages.
Commits or PR's that contravene this directive will be rejected.

Do not leave comments in the code detailing what was changed.
