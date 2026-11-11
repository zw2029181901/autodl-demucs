# 10 个 AutoDL 应用：上游与发布核查

核查日期：2026-11-10。范围：官方代码、发行包、模型卡与 AutoDL 文档；未开机租用 GPU，未执行云端推理，不代表十个应用已通过 GPU 验收。

网络情况：GitHub API、PyPI、AutoDL 官方文档可直接访问；本次 `huggingface.co` 超时，模型元数据和模型卡经 `https://hf-mirror.com` 获取。这是原仓库的镜像传输，下面引用仍指向原作者的 Hugging Face 页面；SHA、非 gated 状态需要在构建时重新向所用端点校验。不能把镜像站可访问等同于 AutoDL 实例下载已验证。

## 一、平台流程与本次实施边界

- AutoDL 官方明确：当前不支持导入自定义 Docker 镜像。应在实例内安装环境，关机，再用“更多 → 保存镜像”保存整个系统盘。数据盘不会因此成为镜像内容。不能把源码 ZIP 或 Dockerfile 直接称为已保存的云镜像。[AutoDL 镜像文档](https://www.autodl.com/docs/image/)
- AutoDL.Art 的镜像用于运行一个具体 GitHub 项目；来源是 AutoDL 已保存的镜像，两个平台共用账号。发布入口在页头“+”。[AutoDL.Art 镜像文档](https://www.autodl.art/docs/image/)
- 上述官方文档没有给出“所有 Pro 镜像不能发布”的规则。因此可沿用用户此前成功的普通容器实例流程，但不能断言 Pro 永久不兼容。
- 公共模型方式是对平台已有真实路径创建软链接。官方要求检查链接源文件是否存在；不存在时需要下载模型。**不能假设新实例一定有 MiniMax、SDXL、Wan 或其他模型挂载。** 本批应用应可从明确来源下载，并显示下载和空间需求。[公共模型说明](https://www.autodl.art/docs/app_model/)
- “镜像发布”“APP 入口”“创作激励”是不同步骤。激励文档要求先有已审核上架的镜像；算法原创与代码原创由社区判断。自建 GitHub 仓库不自动构成原创算法或原创核心代码。[激励规则](https://www.autodl.art/docs/reward_rule/)
- 规则页本次显示镜像基础 0.05 元/小时、原创代码加 0.01、原创论文加 0.02；与用户截图显示值不完全相同。不要承诺固定收益，提交时以平台当前审核和结算规则为准。文档还列出超过 6 个月未更新可能退出激励活动、不得自行消费套取奖励。[激励规则](https://www.autodl.art/docs/reward_rule/)

## 二、统一依赖基线

采用 Python 3.11、PyTorch 2.8.0、torchvision 0.23.0、torchaudio 2.8.0 的 CUDA 12.8 wheel，是可复现的候选基线。官方发布了这一精确组合；PyTorch 2.7 已开始提供 Blackwell/cu128 支持。**这只说明框架支持，不能替代每个应用在 4090D/4080/5090/PRO6000 上的实际测试。** [官方版本安装表](https://pytorch.org/get-started/previous-versions/) · [Blackwell 支持说明](https://pytorch.org/blog/pytorch-2-7/)

```bash
python -m pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
```

经过发行包元数据检查的候选依赖：

| 包 | 候选固定版本 | Python 与关键约束 | 原始证据 |
|---|---:|---|---|
| diffusers | 0.35.2 | Python ≥3.8，huggingface-hub ≥0.34 | [PyPI 元数据](https://pypi.org/pypi/diffusers/0.35.2/json) |
| transformers | 4.57.1 | Python ≥3.9，huggingface-hub ≥0.34,<1.0；tokenizers ≥0.22,≤0.23 | [PyPI 元数据](https://pypi.org/pypi/transformers/4.57.1/json) |
| faster-whisper | 1.2.1 | Python ≥3.9，ctranslate2 ≥4,<5；onnxruntime ≥1.14,<2 | [PyPI 元数据](https://pypi.org/pypi/faster-whisper/1.2.1/json) |
| kokoro | 0.9.4 | Python ≥3.10,<3.13；依赖 misaki[en] ≥0.9.4 | [PyPI 元数据](https://pypi.org/pypi/kokoro/0.9.4/json) |
| rembg | 2.0.67 | Python ≥3.10,<3.14；cpu extra 安装 onnxruntime | [PyPI 元数据](https://pypi.org/pypi/rembg/2.0.67/json) |
| demucs | 4.0.1 | Python ≥3.8；需要处理 PyTorch 新版 checkpoint 加载差异 | [PyPI 元数据](https://pypi.org/pypi/demucs/4.0.1/json) |

这些是候选锁定版本，不是已经做过完整 GPU 测试的兼容保证。每种任务单独运行，避免把十个模型同时常驻显存。

## 三、10 个不同任务与来源

### 1. SDXL：文字生成图片

- 模型：[`stabilityai/stable-diffusion-xl-base-1.0`](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)。元数据 `gated=false`，revision `462165984030d82259a11f4367a4eed129e94a7b`。
- 代码：Diffusers，Apache-2.0；权重：CreativeML Open RAIL++（模型卡标识 `openrail++`），有使用条件，不能宣传成无条件 MIT 模型。[Diffusers LICENSE](https://github.com/huggingface/diffusers/blob/main/LICENSE) · [SDXL 模型卡](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
- API：`StableDiffusionXLPipeline.from_pretrained(..., torch_dtype=torch.float16, variant="fp16", use_safetensors=True, revision=...)`。需要低显存时用 `enable_model_cpu_offload()`，而不是同时 `.to("cuda")` 后再重复卸载。[SDXL 官方示例](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0#usage)
- 只下载 fp16 组件约 6.94 GB：文本编码器 0.246 + 1.389 GB，UNet 5.135 GB，VAE 0.167 GB。整仓库包含 fp32、单文件和 OpenVINO 等重复格式，不应全部下载。[模型文件元数据](https://huggingface.co/api/models/stabilityai/stable-diffusion-xl-base-1.0?blobs=true)

### 2. Wan 2.1：文字生成短视频

- 模型：[`Wan-AI/Wan2.1-T2V-1.3B-Diffusers`](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B-Diffusers)，revision `0fad780a534b6463e45facd96134c9f345acfa5b`，`gated=false`。
- 官方仓库 [`Wan-Video/Wan2.1`](https://github.com/Wan-Video/Wan2.1) 与权重标注 Apache-2.0。[LICENSE](https://github.com/Wan-Video/Wan2.1/blob/main/LICENSE.txt) · [模型卡](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B-Diffusers)
- Diffusers 0.35.2 明确支持这个模型。API：`AutoencoderKLWan.from_pretrained(..., subfolder="vae", torch_dtype=torch.float32)`，随后 `WanPipeline.from_pretrained(..., vae=vae, torch_dtype=torch.bfloat16)`；可配 CPU offload。输出 `.frames[0]`，用 `export_to_video(..., fps=16)`。[固定版本 Wan 文档](https://github.com/huggingface/diffusers/blob/v0.35.2/docs/source/en/api/pipelines/wan.md)
- 帧数选 `4k+1`，例如 17/33/49/81。文档某处把帧数表述成 fps，实际应按 pipeline 输入约束处理，不能把 16fps 当成非法值。[固定版本 pipeline](https://github.com/huggingface/diffusers/blob/v0.35.2/src/diffusers/pipelines/wan/pipeline_wan.py)
- 该 Diffusers 仓库原始权重约 **28.9 GB**（UMT5 约22.72 GB、transformer 约5.68 GB、VAE约0.51 GB）；`torch_dtype=bfloat16` 影响加载，不能让服务器上原始下载自动减半。推荐单独预留 40 GB 模型/工作空间，这个数是工程余量，非 GPU 实测。[文件元数据](https://huggingface.co/api/models/Wan-AI/Wan2.1-T2V-1.3B-Diffusers?blobs=true)

### 3. Faster Whisper：语音转文字和字幕

- 候选模型：[`Systran/faster-whisper-small`](https://huggingface.co/Systran/faster-whisper-small)，revision `536b0662742c02347bc0e980a01041f333bce120`，`gated=false`，MIT；`model.bin` 483,546,902 bytes。[模型元数据](https://huggingface.co/api/models/Systran/faster-whisper-small?blobs=true)
- 代码 [`SYSTRAN/faster-whisper`](https://github.com/SYSTRAN/faster-whisper) 是 MIT。[LICENSE](https://github.com/SYSTRAN/faster-whisper/blob/master/LICENSE)
- API：先把固定 revision 下载到本地，再 `WhisperModel(local_dir, device="cuda", compute_type="float16")`；CPU 使用 `device="cpu", compute_type="int8"`。`segments` 是惰性 generator，必须迭代/转 list 才实际运行。[官方 README](https://github.com/SYSTRAN/faster-whisper#usage)
- GPU 使用 **CTranslate2**，不能只因为 PyTorch CUDA 正常就保证它正常。官方要求 cuBLAS CUDA12 和 cuDNN9，Linux 需要把库目录加入 `LD_LIBRARY_PATH`；应单独验证初始化和一段音频。PyAV 已带音频解码库。[官方要求](https://github.com/SYSTRAN/faster-whisper#requirements)
- CTranslate2 4.6.0 可用但其 release notes 没有明示 Blackwell 验证；不要作“四种显卡全测”宣传。当前硬件文档也强调预编译包与源码编译的差异。[4.6.0 release](https://github.com/OpenNMT/CTranslate2/releases/tag/v4.6.0) · [硬件文档](https://opennmt.net/CTranslate2/hardware_support.html)

### 4. Kokoro：文字配音

- 模型：[`hexgrad/Kokoro-82M`](https://huggingface.co/hexgrad/Kokoro-82M)，revision `f3ff3571791e39611d31c381e3a41a3af07b4987`，`gated=false`，Apache-2.0；权重 `kokoro-v1_0.pth` 327,212,226 bytes。[模型元数据](https://huggingface.co/api/models/hexgrad/Kokoro-82M?blobs=true)
- 代码也是 Apache-2.0。[代码与示例](https://github.com/hexgrad/kokoro) · [LICENSE](https://github.com/hexgrad/kokoro/blob/main/LICENSE)
- `kokoro==0.9.4` 发布 wheel 的 `KModel` 支持 `repo_id, config, model`；`config` 可以是本地 JSON 路径，`model` 可以是本地权重路径。`KPipeline` 可接受这个已创建的 KModel。使用以下形式不会退回未固定 revision 的默认模型下载：[0.9.4 发布包](https://pypi.org/project/kokoro/0.9.4/)

```python
from kokoro import KModel, KPipeline
model = KModel(repo_id="hexgrad/Kokoro-82M", config=str(local_dir / "config.json"),
               model=str(local_dir / "kokoro-v1_0.pth")).to(device).eval()
pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", model=model)
generator = pipeline(text, voice=str(local_dir / "voices/af_heart.pt"))
```

- voice 传本地 `.pt` 路径或已加载 tensor；传名字 `af_heart` 会调用内部未带 revision 的下载。输出采样率 24,000 Hz。系统包需要 `espeak-ng`；中文语言码 `z` 需要 `misaki[zh]`。[上游使用说明](https://github.com/hexgrad/kokoro#advanced-usage)
- `af_heart.pt` 523,425 bytes，SHA256 `0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff`；`zf_xiaobei.pt` 523,435 bytes，SHA256 `9b76be63dab4f4f96962030acc0126a9aee9728608fbbe115e2b58a2bd504df6`。[文件元数据](https://huggingface.co/api/models/hexgrad/Kokoro-82M?blobs=true)

### 5. U²-Net / rembg：透明背景抠图

- 代码 [`danielgatis/rembg`](https://github.com/danielgatis/rembg) 是 MIT；选用上游 [`xuebinqin/U-2-Net`](https://github.com/xuebinqin/U-2-Net) 的 Apache-2.0 模型项目。[rembg LICENSE](https://github.com/danielgatis/rembg/blob/main/LICENSE.txt) · [U²-Net LICENSE](https://github.com/xuebinqin/U-2-Net/blob/master/LICENSE)
- 必须显式 `new_session("u2net", providers=["CPUExecutionProvider"])`，然后 `remove(image, session=session)`。新版 rembg 主分支已把默认模型改为 BRIA RMBG2.0，其商业条件不同；不能随上游默认值漂移。[rembg 说明](https://github.com/danielgatis/rembg#models)
- 固定文件：[u2net.onnx](https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx)，175,997,641 bytes。官方 release API 没有 SHA256 digest；rembg 2.0.67 源码校验 MD5 `60024c5c889badc19c04ad937298a77b`。[固定版本下载逻辑](https://github.com/danielgatis/rembg/blob/v2.0.67/rembg/sessions/u2net.py) · [release API](https://api.github.com/repos/danielgatis/rembg/releases/tags/v0.0.0)
- CPU ONNX 路径能避免额外 CUDA 后端兼容问题；若提供 GPU 模式，需要另验 onnxruntime-gpu，不应仅按 torch.cuda 判断它可用。

### 6. Real-ESRGAN：图片四倍超分

- 模型文件：[RealESRGAN_x4plus.pth](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth)，67,040,989 bytes；release API 未提供 digest，不伪造 SHA256。[release API](https://api.github.com/repos/xinntao/Real-ESRGAN/releases/tags/v0.1.0)
- 官方模型参数 `RRDBNet(num_in_ch=3,num_out_ch=3,num_feat=64,num_block=23,num_grow_ch=32,scale=4)`。[官方 inference](https://github.com/xinntao/Real-ESRGAN/blob/master/inference_realesrgan.py)
- Real-ESRGAN 项目是 BSD-3-Clause；**其引用的 BasicSR RRDBNet 源码项目目前是 Apache-2.0**。若复制 BasicSR 网络结构需保留相应许可与归属，不能简单把全部代码标成 BSD。[Real-ESRGAN LICENSE](https://github.com/xinntao/Real-ESRGAN/blob/master/LICENSE) · [BasicSR LICENSE](https://github.com/XPixelGroup/BasicSR/blob/master/LICENSE.txt) · [网络源码](https://github.com/XPixelGroup/BasicSR/blob/master/basicsr/archs/rrdbnet_arch.py)
- 可以只实现/采用这个小网络推理结构，避免导入整套旧 BasicSR 训练依赖。权重加载优先 `params_ema`，其次 `params`；分块推理时必须有 overlap/padding 并正确裁边，输出拼回原尺寸×4。[官方 utils](https://github.com/xinntao/Real-ESRGAN/blob/master/realesrgan/utils.py)

### 7. SAM 2.1：点击或框选分割图片

- 模型 [`facebook/sam2.1-hiera-small`](https://huggingface.co/facebook/sam2.1-hiera-small)，revision `ee5bba1d82bb8749febdf90f45e84b687142ba03`，`gated=false`，Apache-2.0。元数据约46.06M参数；配置架构已标为 `Sam2VideoModel`，不要因此用 AutoModel 误选视频入口，图片任务显式用 Sam2Model。[模型卡与元数据](https://huggingface.co/api/models/facebook/sam2.1-hiera-small)
- 原项目和 Transformers 均 Apache-2.0。[SAM2 LICENSE](https://github.com/facebookresearch/sam2/blob/main/LICENSE) · [Transformers LICENSE](https://github.com/huggingface/transformers/blob/main/LICENSE)
- **Transformers 4.57.1 已有原生 Sam2Model / Sam2Processor**，不需要 `trust_remote_code=True` 或安装官方自定义 CUDA 扩展。[固定版本代码目录](https://github.com/huggingface/transformers/tree/v4.57.1/src/transformers/models/sam2)
- 官方固定版本图片例子：`input_points=[[[[x,y]]]]`，`input_labels=[[[1]]]`，输出处理 `processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"])[0]`。这里不使用旧 SAM 的 `reshaped_input_sizes` 参数。多候选用 `iou_scores` 选择最高分。[4.57.1 用法](https://github.com/huggingface/transformers/blob/v4.57.1/docs/source/en/model_doc/sam2.md)

### 8. BLIP：图片内容描述

- 模型 [`Salesforce/blip-image-captioning-base`](https://huggingface.co/Salesforce/blip-image-captioning-base)，revision `82a37760796d32b1411fe092ab5d4e227313294b`，`gated=false`，模型卡标 BSD-3-Clause。`pytorch_model.bin` 989,820,849 bytes；此 revision 未见 safetensors，不能硬编码 `use_safetensors=True`。[文件元数据](https://huggingface.co/api/models/Salesforce/blip-image-captioning-base?blobs=true)
- 代码 [`salesforce/BLIP`](https://github.com/salesforce/BLIP) BSD-3-Clause；实际运行可用 Transformers 原生 `BlipProcessor` 和 `BlipForConditionalGeneration`，无需 remote code。[BLIP LICENSE](https://github.com/salesforce/BLIP/blob/main/LICENSE.txt) · [模型卡](https://huggingface.co/Salesforce/blip-image-captioning-base)
- 图片处理后 `model.generate(**inputs, max_new_tokens=...)`，`processor.decode(..., skip_special_tokens=True)`；基础模型主要输出英文，不承诺中文图片说明或 OCR。[模型卡用法](https://huggingface.co/Salesforce/blip-image-captioning-base)

### 9. Demucs：人声、伴奏与音轨分离

- 官方 [`facebookresearch/demucs`](https://github.com/facebookresearch/demucs)，MIT；`htdemucs` 是四音轨模型，输出 vocals/drums/bass/other。官方仓库未额外列出不同的该 checkpoint 许可。[README](https://github.com/facebookresearch/demucs#license) · [LICENSE](https://github.com/facebookresearch/demucs/blob/main/LICENSE)
- `htdemucs.yaml` 对应 `955717e8`，官方文件为 [`955717e8-8726e21a.th`](https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/955717e8-8726e21a.th)，HTTP HEAD 成功，84,141,911 bytes。文件名包含校验前缀；官方对象元数据 MD5 `b57e3704651588e6702539cd7e8f87f6`。此处不是完整 SHA256。[模型表](https://github.com/facebookresearch/demucs/blob/main/demucs/remote/files.txt) · [模型配置](https://github.com/facebookresearch/demucs/blob/main/demucs/remote/htdemucs.yaml)
- 安装 `demucs==4.0.1`。CLI：`python -m demucs -n htdemucs --two-stems vocals --segment 7 INPUT`。HT 模型 segment 不超过7.8秒。wav/flac 保存使用 `torchaudio.save`，音频解码路径还使用 ffmpeg/ffprobe。[用法](https://github.com/facebookresearch/demucs#separating-tracks) · [audio.py](https://github.com/facebookresearch/demucs/blob/main/demucs/audio.py)
- **PyTorch2.6+兼容问题**：Demucs `states.py` 调用 `torch.load(path,'cpu')`，checkpoint 含模型类，不是纯 state_dict；新 torch 默认 `weights_only=True` 可能失败。只对固定来源且校验过的模型，在隔离 Demucs 子进程设置 `TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1`；不要对用户提供的 checkpoint 执行这种加载，也不要全局 monkeypatch 所有应用。[Demucs 加载源码](https://github.com/facebookresearch/demucs/blob/main/demucs/states.py) · [PyTorch 序列化说明](https://docs.pytorch.org/docs/stable/notes/serialization.html#environment-variables)

### 10. Multilingual E5：中英文文档语义检索

- 模型 [`intfloat/multilingual-e5-small`](https://huggingface.co/intfloat/multilingual-e5-small)，revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`，`gated=false`，MIT；`model.safetensors` 470,641,600 bytes。[模型元数据](https://huggingface.co/api/models/intfloat/multilingual-e5-small?blobs=true)
- E5 官方代码在 [`microsoft/unilm/e5`](https://github.com/microsoft/unilm/tree/master/e5)，MIT；可使用 Transformers 原生 AutoTokenizer/AutoModel，无需 sentence-transformers。[LICENSE](https://github.com/microsoft/unilm/blob/master/LICENSE) · [模型卡用法](https://huggingface.co/intfloat/multilingual-e5-small#usage)
- 查询必须加 `query: `，文档段落加 `passage: `，中文也一样；attention-mask mean pooling 后 L2 normalize，再算内积。模型最大512 token，需要对上传文档分段，并给命中结果保留文件名/段落来源。[模型卡 FAQ 和用法](https://huggingface.co/intfloat/multilingual-e5-small)
- 这是搜索工具，不是问答大模型；结果应是相关段落和相似度，不能把其分数包装成“事实正确概率”。

## 四、下载与容量预算

以下 GPU 建议均为**初始测试配置建议，未测量**。模型大小来自上文元数据，预留空间是人为工程余量；CUDA、Python依赖、缓存和输出另计，保存镜像的系统盘空间也要单独核对。

| 应用 | 权重下载概算 | 独立模型/输出预留建议 | 首测建议 |
|---|---:|---:|---|
| SDXL | fp16约6.94GB | 12GB | 24GB GPU，单张，1024边长，CPU offload可选 |
| Wan | 原始约28.9GB | 40GB | 24GB GPU，短片低分辨率，CPU offload |
| Whisper-small | 0.49GB | 2GB | CPU可用；CUDA后端单独验收 |
| Kokoro | 0.33GB＋音色 | 2GB | CPU或GPU，先短文本 |
| U2net | 0.176GB | 1GB | CPU ONNX |
| Real-ESRGAN | 0.067GB | 2GB | GPU分块或CPU |
| SAM2-small | 约0.185GB safetensors | 2GB | GPU单图或CPU |
| BLIP-base | 0.99GB | 3GB | GPU单图或CPU |
| Demucs | 0.084GB | 3GB | GPU或CPU；7秒分块 |
| E5-small | 0.47GB＋tokenizer | 2GB | CPU小批次可用 |

本批以十种真实不同用途组织；不要声称上游算法原创，不把同一应用改十个名称充数。公开发布前需要留下每个应用的实际输入、输出、依赖检查、服务端口检查与新实例启动验证记录。完成本地源码与安装脚本并不等于已经创建、发布或完成十份云镜像。

## 五、安装兼容与离线启动补充核查

### Kokoro / misaki 的附加资源

- 核查的是 `misaki==0.9.4` PyPI wheel，SHA256 `90e2eeb169786c014c429e5058d2ea6bcd02d651f2a24450ba6c9ffc0f8da15a`，以及上游版本号同为0.9.4的 commit `e820629b96334db28227df37f280e4836d46fadb`。不是用当前主分支推断旧版本行为。[PyPI元数据](https://pypi.org/pypi/misaki/0.9.4/json) · [固定版本代码](https://github.com/hexgrad/misaki/tree/e820629b96334db28227df37f280e4836d46fadb)
- 英文 `G2P(trf=False)` 使用 `en_core_web_sm`；若该模型包未安装，会调用 `spacy.cli.download`。因此应在制作镜像时预装，避免客户首次点击才下载。[en.py](https://github.com/hexgrad/misaki/blob/e820629b96334db28227df37f280e4836d46fadb/misaki/en.py)
- 兼容公共 `numpy==1.26.4` 的版本组合为 `spacy==3.7.5`、`thinc==8.2.5`、`spacy-curated-transformers==0.2.2`、`en_core_web_sm==3.7.1`。这是依赖约束核对结论，完整安装和发音效果仍须在目标环境验证。spaCy3.7.5要求thinc>=8.2.2,<8.3；thinc8.2.5在Python3.9+要求numpy>=1.19,<2；该英语模型要求spaCy>=3.7.2,<3.8。[spaCy元数据](https://pypi.org/pypi/spacy/3.7.5/json) · [thinc元数据](https://pypi.org/pypi/thinc/8.2.5/json) · [curated-transformers元数据](https://pypi.org/pypi/spacy-curated-transformers/0.2.2/json)
- 官方英语模型wheel为 [en_core_web_sm-3.7.1-py3-none-any.whl](https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl)，12,803,381 bytes，官方公布SHA256 `86cc141f63942d4b2c5fcee06630fd6f904788d2f0ab005cce45aadb8fb73889`，MIT。[release说明](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.7.1)
- 0.9.4英文词典从misaki包内JSON读取，fallback默认为None；当前主分支后来增加的BART fallback下载不适用于这个固定版本。中文使用jieba、pypinyin、pypinyin-dict安装包数据；`zh_frontend.py` 导入包内 `large_pinyin`，未见独立神经模型下载。应固定 `misaki[en,zh]==0.9.4`，不要安装无版本上限的latest。[中文前端](https://github.com/hexgrad/misaki/blob/e820629b96334db28227df37f280e4836d46fadb/misaki/zh_frontend.py)
- Kokoro主模型需传本地config和权重路径，音色传本地 `.pt` 路径；仅传音色名仍可能触发huggingface_hub下载。镜像内预留英语包、系统espeak-ng或对应运行库，不把模型权重已就绪等同于所有发音资源已就绪。

### Demucs 本地模型仓库

已核查 `v4.0.1` 源码，以下布局可供 `python -m demucs --repo /模型目录 -n htdemucs ...` 使用：

```text
模型目录/
  htdemucs.yaml                 # 内容：models: ['955717e8']
  955717e8-8726e21a.th
```

`LocalRepo` 将文件名拆为模型签名 `955717e8` 与SHA256校验前缀 `8726e21a`；`BagOnlyRepo` 根据yaml文件名找到 `htdemucs`，再读 `models` 列表。不要改成无法匹配签名的任意文件名。[固定版本repo.py](https://github.com/facebookresearch/demucs/blob/v4.0.1/demucs/repo.py)

### 随包许可证

已从两个上游仓库的GitHub license接口取得完整原文，保存至 `autodl-ten-apps/licenses/Real-ESRGAN.LICENSE.txt` 和 `autodl-ten-apps/licenses/BasicSR.LICENSE.txt`。前者BSD-3-Clause，后者Apache-2.0。复制BasicSR网络代码时需保留来源、许可和修改说明。[Real-ESRGAN接口](https://api.github.com/repos/xinntao/Real-ESRGAN/license) · [BasicSR接口](https://api.github.com/repos/XPixelGroup/BasicSR/license)

## 六、30GB免费镜像额度与公共模型约束

用户最新约束为所有保存镜像合计不超30GB；用户界面显示已有3.83GB、余量26.17GB，此界面数值由主任务核对。本节修正前面容量表的适用范围：表中是模型/输出所需空间估算，不是“十份镜像能装进免费额度”的承诺。

- 官方规定：“镜像计费以所有镜像存储总容量大小进行计费，与镜像数量无关。”30GB以下免费，超出部分0.01元/GB/日，按当日最大容量计算。已检索官方文档全文索引，没有查到“十份镜像的相同torch/CUDA基础层只计一份”或“只计算增量”的明确保证，因此不能用Docker通常有分层机制代替平台实际账单规则。[镜像计费](https://www.autodl.com/docs/price/#_14)
- 保存镜像保留系统盘；`/root/autodl-tmp` 数据盘不入镜像；`/root/autodl-pub` 是平台只读公共数据目录。三个位置不能混淆。[目录说明](https://www.autodl.com/docs/env/#_3) · [保存镜像](https://www.autodl.com/docs/image/)
- AutoDL.Art明确支持公共模型软链接。官方例子是文件 `/.autodl/23/73/8c/23738c26b548113ea2d392abd91d3fd0` 链接为 `flux1-dev-fp8.safetensors`，并说明目标只占很少空间。**这个路径只是官方Flux示例，不能挪作本批SDXL/Wan模型。**[使用公共模型](https://www.autodl.art/docs/app_model/)
- 此文档展示的是逐文件软链接，没有保证存在本批各模型的完整Hugging Face Diffusers目录，也没有公布足以核实的完整公共模型清单。公共目录中是否有某模型，必须在目标实例或模型库核实文件和格式。源文件不存在时，官方文档也明确需要下载，建立一个不存在目标的链接不能解决问题。
- Diffusers `from_pretrained` 所需目录通常包含 `model_index.json`、各组件config、tokenizer词表、全部分片权重。可以把公共库中的对应文件链接成目录，但必须逐一验证；单个ComfyUI checkpoint或不同量化格式的safetensors不等价于完整Diffusers目录。不得把未知公共目录写死为可用路径。
- Wan原始下载约28.9GB，已经超过当前26.17GB余量，且尚未包含软件依赖。为遵守约束，默认禁止自动下载整份Wan到镜像；应要求明确指定并验证 `MODEL_PATH_MAIN` 的完整本地/挂载目录。其余应用同样优先使用已核实公共资源，不能因体积小而跳过用户的总量限制。
- 单份共享运行环境加十个应用入口可减少本地软件重复，但“十条公开应用能否绑定同一个镜像”需要在平台发布界面核实。若必须十份独立镜像，应逐份保存观察账户实际占用，不能先保存超额再删除，因为当日最大值可能已经产生费用。
- 本批自行编写的界面、部署脚本和业务整合可如实标注自有实现；模型和算法仍归上游。不能把界面改造表述为原创模型/原创算法，不能预先保证平台原创奖励资格。
