#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
app_dir="$(realpath "${1:-$script_dir}")"
[[ -f "$app_dir/app.json" ]] || { echo 'Usage: bash start.sh projects/<app-id>'; exit 2; }
[[ -x "$app_dir/.venv/bin/python" ]] || { echo 'Run install.sh first.'; exit 1; }
export GRADIO_ANALYTICS_ENABLED=False
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
export PYTHONUNBUFFERED=1
exec "$app_dir/.venv/bin/python" "$script_dir/runtime/serve.py" --project "$app_dir"
