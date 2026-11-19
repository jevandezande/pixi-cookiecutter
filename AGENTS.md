# AI Agent Development Guide

Cookiecutter template for pixi-based Python projects. This repository is Python (>=3.13).

## Skills

Read the relevant `SKILL.md` files in `.agents/skills/` before editing: `write-code`,
`write-docstrings`, `write-tests`, `write-method-docs`, and `cleanup-code`.
`{{cookiecutter.package_name}}/data/.agents/skills/` holds the skills that ship into generated
projects; neither agent loads them here.

## Layout

- `{{cookiecutter.package_name}}/` - template body (generated project)
  - `data/` - post-gen hook staging data (deleted in produced template)
  - `data/AGENTS.md` - `AGENTS.md` every generated project gets
  - `data/.agents/skills/` - skills, copied to `.agents/skills/` for Codex; `.claude/skills/` is a
    symlink to it for Claude Code, since each agent reads only its own directory
  - `data/.claude/settings.json` - Claude Code settings and hooks, copied to `.claude/`
  - `data/.codex/hooks.json` - Codex hooks, copied to `.codex/`; same `hooks` as Claude's
- `hooks/` - cookiecutter hooks and their tests
- `.github/workflows/` - CI that generates projects and runs checks
- `notes.md` - setup notes and optional tools
- `template_config.yml` - example cookiecutter configuration
- `pyproject.toml` - project metadata, dependencies, pixi environments and tasks, and tool
  configuration (ruff, pytest)
- `prek.toml` - git hook configuration

## Rendering

`hooks/` is rendered. `post_gen_project.py` embeds `{{cookiecutter.*}}` in string literals and
in default arguments. Functions that need a cookiecutter value take it as a parameter so tests
can pass their own.

`_copy_without_render` covers `.github/workflows`, because GitHub Actions `${{ ... }}` collides
with Jinja. Anything else under the template root is rendered.

Placeholders the post-gen hook fills (`{python_version}`, `{pixi_dependencies}`,
`{pixi_test_dependencies}`)
go through `read_write`, which raises when the placeholder is absent rather than leaving the file
untouched.

## Testing

Hooks: `pixi run all`, or `pixi run -e dev prek run -a --stage pre-push` (same plus whitespace
and TOML/YAML).

`test_template_renders_to_well_formed_files` in `hooks/test_post_gen_project.py` renders every
non-verbatim template file, and the two generation hooks, for each option combination and parses
the TOML, JSON, and Python. It is the only local check that an edit did not take a Jinja tag with
it, since the root `prek.toml` has to exclude the template's `pyproject.toml` from `check-toml`.

Full generation is not side-effect free; when `github_setup` is not `"None"`, `gh repo create` is
run, which creates a repository on GitHub. CI generates projects with `github_setup=None` only.

## Commits and pull requests

- Create a branch for new work; do not develop on `master`. If another agent is working in this
  directory, offer a worktree (`git worktree add ../<repo>-<feature>`), and remove it once merged.
- Break work into commits that each make sense alone. Prefix messages with a conventional commit
  type: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, or `chore:`.
- Never credit an AI agent as an author or co-author on commits or PR messages. Commits or PRs
  that do will be rejected.
- Do not leave comments in the code detailing what was changed.
- Pass PR descriptions to `gh pr create` with `--body-file`.

PRs are squash-merged. Merge with
`gh pr merge N --squash --subject "<title> (#N)" --body-file <file>` (don't use GitHub's default).
The body expresses the net change and why, measurement summaries, known limits, and breaking changes.
Branch history, verification, questions, and follow-ups stay in PR. Small PRs need only subject.
