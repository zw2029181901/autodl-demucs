#!/usr/bin/env bash
set -Eeuo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
app_dir="$(realpath "${1:-$script_dir}")"
[[ -f "$app_dir/app.json" ]] || { echo 'Usage: bash install.sh projects/<app-id>'; exit 2; }
export PIP_NO_CACHE_DIR=1
export PIP_DEFAULT_TIMEOUT=60
python_bin="${PYTHON_BIN:-python3}"
"$python_bin" -c 'import sys; assert (3,11) <= sys.version_info[:2] <= (3,12), "Use Python 3.11 or 3.12"'
system_packages=(git libsndfile1)
if [[ "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("ffmpeg",False))' "$app_dir/app.json")" == True ]]; then
    system_packages+=(ffmpeg)
fi
if [[ "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("espeak",False))' "$app_dir/app.json")" == True ]]; then
    system_packages+=(espeak-ng)
fi
if [[ "${SKIP_APT:-0}" != 1 ]]; then
    [[ "$EUID" == 0 ]] || { echo 'Run as root, or install system dependencies and set SKIP_APT=1.'; exit 1; }
    apt-get update
    apt-get install -y --no-install-recommends "${system_packages[@]}"
fi
if [[ ! -x "$app_dir/.venv/bin/python" ]]; then
    if [[ "${USE_BASE_TORCH:-0}" == 1 ]]; then
        "$python_bin" -c 'import torch,torchvision,torchaudio; assert torch.__version__.split("+")[0]=="2.8.0" and torchvision.__version__.split("+")[0]=="0.23.0" and torchaudio.__version__.split("+")[0]=="2.8.0", "Base must have the exact supported torch/vision/audio versions"'
        "$python_bin" -m venv --system-site-packages "$app_dir/.venv"
    else
        "$python_bin" -m venv "$app_dir/.venv"
    fi
fi
venv_python="$app_dir/.venv/bin/python"
"$venv_python" -m pip install --upgrade pip==25.2
if [[ "$("$python_bin" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("torch",True))' "$app_dir/app.json")" == True ]]; then
    if [[ "${USE_BASE_TORCH:-0}" != 1 ]]; then
        torch_flavor="$("$python_bin" -c 'import json,sys; print("cu128" if json.load(open(sys.argv[1]))["requires_gpu"] else "cpu")' "$app_dir/app.json")"
        "$venv_python" -m pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url "${TORCH_INDEX_URL:-https://download.pytorch.org/whl/$torch_flavor}"
    fi
fi
"$venv_python" -m pip install -r "$script_dir/requirements-base.txt" -r "$app_dir/requirements.txt"
"$venv_python" -m pip check
"$venv_python" "$script_dir/runtime/serve.py" --project "$app_dir" --check-ui
"$venv_python" "$script_dir/runtime/doctor.py" --project "$app_dir" --dependencies-only
"$venv_python" -m pip freeze > "$app_dir/installed-requirements.txt"
echo 'Dependencies installed. Weights not downloaded. See README.md for prefetch, startup and validation.'
