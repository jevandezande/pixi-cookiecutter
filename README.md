# Pixi Cookiecutter

[![License](https://img.shields.io/github/license/jevandezande/pixi-cookiecutter)](https://github.com/jevandezande/pixi-cookiecutter/blob/master/LICENSE)
[![Powered by: Pixi](https://img.shields.io/badge/powered_by-pixi-facc15)](https://pixi.sh)
[![Code style: ruff](https://img.shields.io/badge/code_style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Markdown style: rumdl](https://img.shields.io/badge/md%20style-rumdl-000000.svg)](https://rumdl.dev)
[![Typing: ty](https://img.shields.io/badge/typing-ty-EFC621.svg)](https://github.com/astral-sh/ty)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/jevandezande/pixi-cookiecutter/test.yml?branch=master&logo=github-actions)](https://github.com/jevandezande/pixi-cookiecutter/actions/)
[![Codecov](https://img.shields.io/codecov/c/github/jevandezande/pixi-cookiecutter)](https://app.codecov.io/github/jevandezande/pixi-cookiecutter)

[Cookiecutter](https://github.com/cookiecutter/cookiecutter) for setting up [pixi](https://pixi.sh/) projects with all the necessary features for modern python development.

## Features

- Packaging with [pixi](https://prefix.dev/)
- Environment loading with [direnv](https://direnv.net/)
- Formatting and linting of Python with [ruff](https://github.com/astral-sh/ruff)
- Formatting and linting of Markdown with [rumdl](http://rumdl.dev)
- Static typing with [ty](https://github.com/astral-sh/ty)
- Testing with [pytest](https://docs.pytest.org/en/latest/)
- Git hooks that run all the above with [prek](https://prek.j178.dev)
- Continuous integration with [GitHub Actions](https://github.com/features/actions)
- Code coverage with [Codecov](https://docs.codecov.com/docs)

## Setup

While all of the steps are automated, you will need to first install `pixi`, `cookiecutter`, and `direnv`, and optionally install the [GitHub-CLI](https://cli.github.com/).

```sh
curl -fsSL https://pixi.sh/install.sh | sh
curl -sfL https://direnv.net/install.sh | bash

# Optional
curl -sS https://webi.sh/gh | sh
```

See [notes.md](notes.md#Project-Tools) for optional dependencies and [alternative installation methods](notes.md#Alternative-installation-methods).

```sh
# Use cookiecutter to create a project from this template
cookiecutter gh:jevandezande/pixi-cookiecutter
```

The cookiecutter will automagically

- Generate a project with the input configuration
- Initialize git
- Setup environment
- Setup pre-commit and pre-push hooks (via prek)
- Setup your preferred coding agent (if any)
- Make initial commit
- Sets up remote on GitHub (optional)

## Recommendations

- Make a custom config file (see [template_config.yml](template_config.yml)).
- Install [act](https://github.com/nektos/act) to run GitHub Actions locally.
- Install [direnv](https://pixi.sh/latest/integration/third_party/direnv) to automagically load the environment.

Read [notes](notes.md) for more tips.

If you don't need packages from conda, check out `uv` and the [uv-cookiecutter](https://github.com/jevandezande/uv-cookiecutter).
