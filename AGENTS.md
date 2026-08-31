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
- `hooks/` - cookiecutter hooks and tests
- `.github/workflows/` - CI/CD configuration
- `notes.md` - setup notes and optional tools
- `template_config.yml` - example cookiecutter configuration

Python Version: >=3.13

Key configuration files:

- `pyproject.toml` - Project metadata, dependencies, all tool configuration (ruff, pytest, coverage)
- `prek.toml` - Prek hook configuration
- `.editorconfig` - Editor formatting settings
