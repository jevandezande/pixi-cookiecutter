# Notes
## Configuring Pixi

If installing programs with pixi (recommended), make sure the `~/.pixi/bin` is
in your path by adding the following to your .zshrc/.bashrc/.profile
```sh
export PATH=$PATH:~/.pixi/bin
```
### Installing pixi
```sh
curl -fsSL https://pixi.sh/install.sh | bash
```

## Cookiecutter
While cookiecutter doesn't need to be installed globally if running the
cookiecutter from within this project, it is needed if you want to run this
cookiecutter without separately downloading it.

### Installing cookiecutter
```sh
pixi global install cookiecutter
```

## Configuring Pixi Cookiecutter
Make a [config file](https://cookiecutter.readthedocs.io/en/stable/advanced/user_config.html)
(see [template_config.yml](template_config.yml)) with default settings and save
it as a `.cookiecutterrc` or use it directly via: `--config-file cookiecutter.yml`

## Adding project dependencies
Dependencies can be specified in a list, with the @ operator to specify
versions: `dep1@* dep2 dep3@version`. Dependencies that are not tagged to a
specific version (e.g. `dep2`) will have a "\*" appended

## Project Tools
### Act
[act](https://github.com/nektos/act) runs GitHub Actions locally in a docker
container. This makes sure all tests are independent of system settings, and
should replicate running these actions on GitHub. One can act as a variety of
different GitHub actions:

```sh
act push
act pull_request
act schedule
```

#### Installing act
```sh
brew install act
```

### Direnv
[direnv](https://pixi.sh/latest/features/environment/#using-pixi-with-direnv)
can automagically load environment variables and the pixi shell.

#### Installing direnv
```sh
pixi global install direnv
```

Warning: if installed simultaneously from multiple sources, bad things can happen.

Make sure that direnv is available in your shell by adding the following to your
.zshrc/.bashrc/.profile (swap zsh for the name of your shell).
```sh
eval "$(direnv hook zsh)"
```

### GitHub-CLI
[GitHub-CLI](https://cli.github.com/) can create a new repository on GitHub and
provides many useful additional tools. My favorites:

- [copilot](https://github.com/github/gh-copilot) - chat interface for questions about the command line
- [dash](https://github.com/dlvhdr/gh-dash) - displays a dashboard with pull requests and issues
- [gh-f](https://github.com/gennaro-tedesco/gh-f) - fuzzy finder for gh-cli
- [gh-notify](https://github.com/meiji163/gh-notify) - shows your GitHub notifications
- [markdown-preview](https://github.com/yusukebe/gh-markdown-preview) - renders markdown documents in your browser
- [poi](https://github.com/seachicken/gh-poi) - safely cleans up old local branches

#### Installing GitHub-CLI
```sh
curl -sS https://webi.sh/gh | sh
```

### Pre-commit
[pre-commit](https://pre-commit.com/) runs formatting, linting, and other hooks
on `git commit`.

#### Installing pre-commit
Pre-commit comes installed with the pixi package, but if you want to install it
globally:
```sh
pixi global install pre-commit
```

### Alternative installation methods
#### Act
```sh
gh extension install https://github.com/nektos/gh-act
```

#### Cookiecutter
```sh
# Apt
apt install cookiecutter
# Brew
brew install cookiecutter
```

#### Direnv
```sh
# Apt
apt install direnv
# Brew
brew install direnv
```

#### GitHub-CLI
```sh
# Apt
apt install gh
# Brew
brew install gh
```

#### Pre-commit
```sh
# Apt
apt install pre-commit
# Brew
brew install pre-commit
```
