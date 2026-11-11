"""Distinct dependency, GPU, model, HTTP and generation validation stages."""
import argparse
import importlib
import json
import os
from pathlib import Path
import shutil
import sys
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--models", action="store_true")
parser.add_argument("--http", action="store_true")
parser.add_argument("--dependencies-only", action="store_true")
args = parser.parse_args()
os.environ["APP_ROOT"] = str(Path(args.project).resolve())
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime.common import config, storage, model_path, verify_asset

failed = []
cfg = config()
print(f"Project: {cfg['id']}")
for module in ["gradio", *cfg["imports"]]:
    try:
        imported = importlib.import_module(module)
        print(f"IMPORT OK {module} {getattr(imported, '__version__', '')}")
    except Exception as exc:
        failed.append(f"IMPORT FAIL {module}: {exc}")
try:
    import torch
    print(f"TORCH {torch.__version__}; CUDA runtime {torch.version.cuda}")
    if torch.cuda.is_available():
        print(f"GPU {torch.cuda.get_device_name()}; capability {torch.cuda.get_device_capability()}; architectures {torch.cuda.get_arch_list()}")
        a = torch.randn(32, 32, device="cuda")
        value = (a @ a.T).sum().item()
        print(f"CUDA matrix multiplication OK {value:.2f}")
    elif cfg["requires_gpu"] and not args.dependencies_only:
        failed.append("GPU unavailable; this application requires a GPU for inference")
    else:
        print("GPU check deferred" if cfg["requires_gpu"] else "GPU unavailable; CPU mode supported")
except ImportError:
    if cfg.get("torch", True):
        failed.append("PyTorch unavailable")
if cfg.get("ffmpeg") and not shutil.which("ffmpeg"):
    failed.append("ffmpeg unavailable")
if cfg.get("espeak") and not shutil.which("espeak-ng"):
    failed.append("espeak-ng unavailable")
if args.models:
    os.environ["HF_HUB_OFFLINE"] = "1"
    for name, spec in cfg["models"].items():
        try:
            if spec["kind"] == "hf":
                path = model_path(name)
                if not any(Path(path).rglob("*.safetensors")) and not any(Path(path).rglob("*.bin")) and not any(Path(path).rglob("*.pth")):
                    raise RuntimeError("No weight files in cached snapshot")
            else:
                path = storage() / cfg["id"] / spec["filename"]
                if not path.is_file():
                    raise FileNotFoundError(path)
                verify_asset(path, spec)
            print(f"MODEL OK {name}: {path}")
        except Exception as exc:
            failed.append(f"MODEL FAIL {name}: {exc}")
if args.http:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{os.environ.get('PORT','6006')}/config", timeout=10) as response:
            info = json.load(response)
        print(f"HTTP OK: {len(info['components'])} UI components")
    except Exception as exc:
        failed.append(f"HTTP FAIL: {exc}")
for error in failed:
    print(error, file=sys.stderr)
print("This check does not prove model generation works. Complete the sample in SMOKE_TEST.md.")
raise SystemExit(1 if failed else 0)
