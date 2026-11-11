"""Explicit model download, never hidden inside installation or UI startup."""
import argparse
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
args = parser.parse_args()
os.environ["APP_ROOT"] = str(Path(args.project).resolve())
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime.common import config, model_path, asset_path

for name, spec in config()["models"].items():
    print(f"Preparing {name}", flush=True)
    if spec["kind"] == "hf":
        print(model_path(name), flush=True)
    else:
        print(asset_path(name), flush=True)
print("Model download complete. Run doctor with --models, then a real sample task.")
