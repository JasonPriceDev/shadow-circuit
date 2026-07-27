#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
workspace_dir="$(dirname "$script_dir")"
env_file="$workspace_dir/.env"

cd "$workspace_dir"

if [[ ! -f "$env_file" ]]; then
	printf 'Missing environment file: %s\n' "$env_file" >&2
	exit 1
fi

set -a
source "$env_file"
set +a

: "${GIT_USER_NAME:?GIT_USER_NAME must be set in .env}"
: "${GIT_USER_EMAIL:?GIT_USER_EMAIL must be set in .env}"

git config --global user.name "$GIT_USER_NAME"
git config --global user.email "$GIT_USER_EMAIL"
npm ci

# ---------------------------------------------------------------------------
# Python agent dependencies
# ---------------------------------------------------------------------------
agent_venv="$workspace_dir/agents/.venv"
if [[ ! -d "$agent_venv" ]]; then
  python3 -m venv "$agent_venv"
fi
"$agent_venv/bin/pip" install -q -r "$workspace_dir/agents/requirements.txt"