from __future__ import annotations

import functools
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
import uuid


def root() -> Path:
    return Path(os.environ["APP_ROOT"]).resolve()


@functools.lru_cache(maxsize=1)
def config() -> dict:
    return json.loads((root() / "app.json").read_text(encoding="utf-8"))


def storage() -> Path:
    configured = os.environ.get("MODEL_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    disk = Path("/root/autodl-tmp")
    return (disk / "autodl-models") if disk.is_dir() else (root() / ".cache" / "models")


def output_dir() -> Path:
    directory = Path(os.environ.get("OUTPUT_DIR", str(root() / "outputs"))).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def output_path(suffix: str) -> Path:
    if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
        raise ValueError("Invalid output extension")
    return output_dir() / f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:12]}{suffix}"


def model_spec(name="main") -> dict:
    return config()["models"][name]


def model_path(name="main") -> str:
    """Use an explicit local model directory or the pinned upstream snapshot."""
    spec = model_spec(name)
    override = os.environ.get("MODEL_PATH_" + name.upper())
    saved_paths = root() / "model-paths.local.json"
    if not override and saved_paths.exists():
        override = json.loads(saved_paths.read_text(encoding="utf-8")).get(name)
    if override:
        path = Path(override).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"模型路径不存在：{path}")
        validate_model_directory(path, spec)
        return str(path)
    if spec.get("local_only"):
        raise RuntimeError("该大模型仅从已核实的公共目录加载，不自动下载。请按 MODEL_STORAGE.md 配置 MODEL_PATH_MAIN 或运行 link_model.py。")
    from huggingface_hub import snapshot_download
    try:
        cached = snapshot_download(repo_id=spec["repo"], revision=spec["revision"], cache_dir=str(storage() / "hub"), local_files_only=True)
        validate_model_directory(Path(cached), spec)
        return cached
    except (OSError, ValueError):
        pass
    reserve_gb = config().get("disk_gb", 1)
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        import shutil
        storage().mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(storage()).free < reserve_gb * 1_000_000_000:
            raise RuntimeError(f"模型盘剩余空间不足，建议至少 {reserve_gb}GB；请先配置公共模型路径。")
    downloaded = snapshot_download(
        repo_id=spec["repo"], revision=spec["revision"],
        cache_dir=str(storage() / "hub"),
        allow_patterns=spec.get("allow_patterns"),
        ignore_patterns=spec.get("ignore_patterns"),
        local_files_only=os.environ.get("HF_HUB_OFFLINE") == "1",
    )
    validate_model_directory(Path(downloaded), spec)
    return downloaded


def validate_model_directory(path: Path, spec: dict):
    if not path.is_dir():
        raise ValueError("需要模型目录，而非单个权重文件")
    for pattern in spec.get("required_files", []):
        if not any(path.glob(pattern)):
            raise ValueError(f"模型目录缺少 {pattern}；请选与本应用一致的完整模型及格式")
    for index in path.rglob("*.index.json"):
        metadata = json.loads(index.read_text(encoding="utf-8"))
        for shard in set(metadata.get("weight_map", {}).values()):
            if not (index.parent / shard).is_file():
                raise ValueError(f"模型缺少权重分片：{shard}")


def asset_path(name="main") -> Path:
    """Download one official asset atomically, checking its published digest."""
    from urllib.request import Request, urlopen
    spec = model_spec(name)
    path = storage() / config()["id"] / spec["filename"]
    if path.exists():
        verify_asset(path, spec)
        return path
    if os.environ.get("HF_HUB_OFFLINE") == "1":
        raise FileNotFoundError(f"离线模式下模型不存在：{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + "." + uuid.uuid4().hex + ".part")
    try:
        with urlopen(Request(spec["url"], headers={"User-Agent": "autodl-tools/1.0"}), timeout=60) as src, temporary.open("wb") as dst:
            while block := src.read(1024 * 1024):
                dst.write(block)
        verify_asset(temporary, spec)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def verify_asset(path: Path, spec: dict):
    if spec.get("bytes") and path.stat().st_size != spec["bytes"]:
        raise RuntimeError(f"模型文件大小不符：{path}")
    if spec.get("sha256") and file_digest(path) != spec["sha256"]:
        raise RuntimeError(f"模型 SHA256 校验失败：{path}")
    if spec.get("sha256_prefix") and not file_digest(path).startswith(spec["sha256_prefix"]):
        raise RuntimeError(f"模型 SHA256 前缀校验失败：{path}")
    if spec.get("md5") and file_digest(path, "md5") != spec["md5"]:
        raise RuntimeError(f"模型 MD5 校验失败：{path}")
    if path.stat().st_size < 1024:
        raise RuntimeError("下载内容不像有效模型文件")


def file_digest(path: Path, algorithm="sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_rgb(image, max_pixels=16_000_000):
    from PIL import Image, ImageOps
    if image is None:
        raise ValueError("请先上传图片")
    if image.width * image.height > max_pixels:
        raise ValueError(f"图片超过 {max_pixels // 1_000_000} 百万像素，请先缩小")
    image = ImageOps.exif_transpose(image)
    if image.mode in ("RGBA", "LA") or "transparency" in image.info:
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        image = Image.alpha_composite(background, rgba)
    return image.convert("RGB")


def device():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def require_gpu():
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("这个工具需要 GPU。请用有卡模式开机，再运行任务。")


def seed_generator(seed):
    import torch
    return torch.Generator(device="cpu").manual_seed(int(seed))


def page_header():
    import gradio as gr
    cfg = config()
    gr.Markdown(f"# {cfg['name']}\n\n{cfg['description']}\n\n首次使用需要准备模型；之后会使用缓存。一次处理一个任务。")


def guarded(function):
    """Return useful failures to the UI without losing the traceback in logs."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        import gradio as gr
        try:
            return function(*args, **kwargs)
        except gr.Error:
            raise
        except Exception as exc:
            import traceback
            traceback.print_exc()
            if "out of memory" in str(exc).lower():
                message = "显存不足，请减少图片尺寸、视频帧数或音频长度，再重启服务。"
            else:
                message = str(exc) or type(exc).__name__
            raise gr.Error(message) from exc
    return wrapper


def timestamp_srt(seconds: float) -> str:
    milliseconds = max(0, int(round(float(seconds) * 1000)))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def srt_text(segments) -> str:
    lines = []
    for segment in segments:
        text = str(segment["text"]).strip()
        if not text:
            continue
        start = max(0.0, float(segment["start"]))
        end = max(start + 0.001, float(segment["end"]))
        if not (math.isfinite(start) and math.isfinite(end)):
            raise ValueError("字幕时间无效")
        lines.append(f"{len(lines)+1}\n{timestamp_srt(start)} --> {timestamp_srt(end)}\n{text}\n")
    return "\n".join(lines)


def chunk_text(text: str, size=600, overlap=100):
    if not 0 <= overlap < size:
        raise ValueError("分块重叠必须小于分块长度")
    text = text.replace("\r\n", "\n").strip()
    chunks = []
    for position in range(0, len(text), size - overlap):
        part = text[position:position+size].strip()
        if part:
            chunks.append(part)
        if position + size >= len(text):
            break
    return chunks
