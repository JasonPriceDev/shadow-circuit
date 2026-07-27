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
        git-lfs \
        gh \
        graphviz \
        jq \
        less \
        lsof \
        openssh-client \
        pandoc \
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

# git-delta is not packaged for Debian bookworm; install the .deb release directly.
RUN set -eux; \
    ARCH="$(dpkg --print-architecture)"; \
    case "$ARCH" in \
        amd64) DELTA_ARCH="amd64" ;; \
        arm64) DELTA_ARCH="arm64" ;; \
        *) echo "Unsupported architecture: $ARCH" >&2; exit 1 ;; \
    esac; \
    DELTA_VERSION="0.18.2"; \
    curl -fsSL -o /tmp/git-delta.deb \
        "https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta_${DELTA_VERSION}_${DELTA_ARCH}.deb" \
    && dpkg -i /tmp/git-delta.deb \
    && rm -f /tmp/git-delta.deb

# pre-commit is not available as a Debian package on bookworm; install via pip.
RUN python3 -m pip install --no-cache-dir --break-system-packages pre-commit

USER node