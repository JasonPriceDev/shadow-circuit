FROM mcr.microsoft.com/vscode/devcontainers/typescript-node:1-22-bookworm

USER root

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        bash-completion \
        bat \
        build-essential \
        ca-certificates \
        curl \
        fd-find \
        git \
        git-delta \
        git-lfs \
        gh \
        graphviz \
        jq \
        less \
        lsof \
        openssh-client \
        pandoc \
        pre-commit \
        procps \
        python3 \
        python3-pip \
        python3-venv \
        ripgrep \
        shellcheck \
        tree \
        unzip \
        wget \
        yamllint \
        zip \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

USER node