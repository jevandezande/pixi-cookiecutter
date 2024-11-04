FROM ghcr.io/prefix-dev/pixi:0.33.0-bookworm AS build

WORKDIR /app
COPY {{cookiecutter.package_name}} {{cookiecutter.package_name}}
COPY pyproject.toml pyproject.toml
COPY pixi.lock pixi.lock

ENV PIXI_ENV=default
RUN pixi install --locked -e $PIXI_ENV

FROM ubuntu:24.10 AS production
WORKDIR /app

ENV PIXI_ENV=default
ENV PATH=/app/.pixi/envs/$PIXI_ENV/bin:$PATH
ENV CONDA_PREFIX=/app/.pixi/envs/$PIXI_ENV
COPY --from=build /app/.pixi/envs/$PIXI_ENV /app/.pixi/envs/$PIXI_ENV
COPY ./{{cookiecutter.package_name}} /app/{{cookiecutter.package_name}}

ENTRYPOINT []
