FROM mcr.microsoft.com/vscode/devcontainers/typescript-node:1-22-bookworm

USER root

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        bash-completion \
        build-essential \
        ca-certificates \
        curl \
        fd-find \
        git \
        git-lfs \
        gh \
        jq \
        less \
        lsof \
        openssh-client \
        procps \
        ripgrep \
        tree \
        unzip \
        wget \
        zip \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

USER node