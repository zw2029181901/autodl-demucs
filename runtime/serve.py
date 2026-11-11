from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--check-ui", action="store_true")
    args = parser.parse_args()
    path = Path(args.project).resolve()
    os.environ["APP_ROOT"] = str(path)
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.path.insert(0, str(path))
    from runtime.common import config, output_dir, storage
    os.environ.setdefault("HF_HOME", str(storage() / "hf"))
    os.environ.setdefault("TORCH_HOME", str(storage() / "torch"))
    os.environ.setdefault("GRADIO_TEMP_DIR", str(output_dir() / ".gradio"))
    spec = importlib.util.spec_from_file_location("task_app", path / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.build_ui()
    if args.check_ui:
        print(f"UI_OK {config()['id']}: {len(app.config['components'])} components")
        return
    password = os.environ.get("APP_PASSWORD")
    app.queue(max_size=8, default_concurrency_limit=1).launch(
        server_name=os.environ.get("LISTEN", "0.0.0.0"),
        server_port=int(os.environ.get("PORT", "6006")),
        share=False, show_error=False, max_file_size="200mb",
        auth=(os.environ.get("APP_USERNAME", "user"), password) if password else None,
        allowed_paths=[str(output_dir())],
    )


if __name__ == "__main__":
    main()
