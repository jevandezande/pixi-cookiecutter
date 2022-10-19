# Notes

## Configuring Pixi Cookiecutter
Make a config file (see [template_config.yml](template_config.yml)) with
default settings and save it as a `.cookiecutterrc` or use it directly via:
`--config-file cookiecutter.yml`

## Adding project dependencies
Dependencies can be specified in a list, with the @ operator to specify
versions: `dep1@* dep2 dep3@version`. Dependencies that are not tagged to a
specific version (e.g. `dep2`) will have a "\*" appended


## Project Tools
### Direnv
Pixi can be used with [direnv](https://pixi.sh/latest/features/environment/#using-pixi-with-direnv)
to automagically load the environment.

#### Installing direnv
Direnv can be installed many ways:
```shell
pixi global install direnv  # Recommended
apt install direnv
brew install direnv
```

Warning: if installed simultaneously from multiple sources, bad things can happen.

Make sure that direnv is available in your shell by adding the following to your
~/.zshrc/.bashrc/.profile (swap zsh for the name of your shell).
```shell
eval "$(direnv hook zsh)"
```

If installed with pixi (recommended), make sure the ~/.pixi/bin is in your path
by adding the following to your ~/.zshrc/.bashrc/.profile
```
export PATH=$PATH:~/.pixi/bin
```

### Act
[act](https://github.com/nektos/act) allows one to run GitHub Actions locally
in a docker container. This makes sure all tests are independent of system
settings, and should replicate running these actions on Github. One can act as
a variety of different GitHub actions:

```
act push
act pull_request
act schedule
```
