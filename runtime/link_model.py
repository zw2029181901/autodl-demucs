"""Persist a checked directory pointer. Never copy public weights into the image."""
import argparse
import json
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--path", required=True)
parser.add_argument("--name", default="main")
args = parser.parse_args()
project = Path(args.project).resolve()
os.environ["APP_ROOT"] = str(project)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from runtime.common import model_spec, validate_model_directory

spec = model_spec(args.name)
if spec["kind"] != "hf":
    raise SystemExit("This command links Hugging Face model directories only.")
path = Path(args.path).resolve(strict=True)
validate_model_directory(path, spec)
destination = project / "model-paths.local.json"
mapping = json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else {}
mapping[args.name] = str(path)
destination.write_text(json.dumps(mapping, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(f"Saved {args.name}: {path}. Format checks passed; verify model identity and run a real task.")
print("No model files copied. The target must also exist on customer instances.")
