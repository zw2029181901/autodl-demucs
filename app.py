import os
import subprocess
import sys
import zipfile
from runtime.common import asset_path, device, guarded, output_dir, output_path, page_header


@guarded
def separate(audio):
    import soundfile as sf
    if not audio:
        raise ValueError("请上传音频")
    # Convert once using ffmpeg to avoid torchaudio backend/version assumptions.
    wav = output_path(".wav")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(audio), "-t", "301", "-ac", "2", "-ar", "44100", str(wav)], check=True, timeout=120)
    info = sf.info(wav)
    if info.duration > 300:
        wav.unlink(missing_ok=True)
        raise ValueError("单次最多5分钟，请先裁剪音频")
    directory = output_dir() / (wav.stem + "-stems")
    directory.mkdir()
    checkpoint = asset_path()  # Only the fixed official file; digest checked before loading.
    (checkpoint.parent / "htdemucs.yaml").write_text("models: ['955717e8']\n", encoding="utf-8")
    # The official command handles peak normalization, shifts, overlapping segments and stems.
    command = [sys.executable, "-m", "demucs", "--repo", str(checkpoint.parent), "-n", "htdemucs", "--device", device(), "--shifts", "0", "--segment", "7", "--float32", "-o", str(directory), str(wav)]
    environment = os.environ.copy()
    environment["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    subprocess.run(command, env=environment, check=True, timeout=1800)
    stem_dir = directory / "htdemucs" / wav.stem
    files = [stem_dir / (name + ".wav") for name in ("vocals", "drums", "bass", "other")]
    if not all(path.is_file() for path in files):
        raise RuntimeError("分离未生成全部声部，请查看服务日志")
    bundle = output_path(".zip")
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.name)
    return str(files[0]), str(bundle)


def build_ui():
    import gradio as gr
    with gr.Blocks(title="Demucs 音轨分离") as ui:
        page_header()
        gr.Markdown("分离人声、鼓、贝斯和其他伴奏。单次最多5分钟。")
        audio = gr.Audio(type="filepath", label="音乐音频")
        button = gr.Button("分离四条音轨", variant="primary")
        vocals = gr.Audio(label="人声试听")
        bundle = gr.File(label="下载四轨 ZIP")
        button.click(separate, audio, [vocals, bundle], api_name="separate")
    return ui
