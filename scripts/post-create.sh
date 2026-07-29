#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
.venv/bin/python -m pip install --requirement agents/requirements.txt
.venv/bin/python -m pip install --requirement .devcontainer/requirements-dev.txt

if [[ -f package-lock.json ]]; then
  npm ci
fi

if [[ -f .pre-commit-config.yaml ]]; then
  .venv/bin/pre-commit install
fi

python scripts/sdlc/traceability.py validate
