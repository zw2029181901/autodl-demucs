# 代码与模型归属

本项目独立编写中文页面、任务交互、下载配置、安装检查和部署材料。下列模型与依赖由其原作者提供；界面或项目名改变不改变模型归属。发布页可以突出功能，自主开发范围须具体、准确。

| 项目 | 模型/代码来源 | 许可与说明 |
|---|---|---|
| SDXL | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 | 权重CreativeML Open RAIL++，保留使用限制；Diffusers Apache-2.0 |
| Wan2.1 | https://github.com/Wan-Video/Wan2.1 | Apache-2.0 |
| Whisper | https://github.com/SYSTRAN/faster-whisper | MIT，Systran转换模型亦见模型卡 |
| Kokoro | https://github.com/hexgrad/kokoro | Apache-2.0；Misaki、spaCy及字典保留各自许可 |
| U2Net | https://github.com/xuebinqin/U-2-Net | Apache-2.0；rembg MIT，固定u2net模型 |
| Real-ESRGAN | https://github.com/xinntao/Real-ESRGAN | BSD-3-Clause，见licenses/Real-ESRGAN.LICENSE.txt |
| RRDB架构 | https://github.com/XPixelGroup/BasicSR/blob/master/basicsr/archs/rrdbnet_arch.py | Apache-2.0；独立兼容实现参照此网络拓扑及权重键布局，见licenses/BasicSR.LICENSE.txt |
| SAM2.1 | https://github.com/facebookresearch/sam2 | Apache-2.0 |
| BLIP | https://github.com/salesforce/BLIP | BSD-3-Clause |
| Demucs | https://github.com/facebookresearch/demucs | MIT；使用固定官方htdemucs checkpoint |
| E5 | https://github.com/microsoft/unilm/tree/master/e5 | MIT |
| Depth Anything V2 Small | https://github.com/DepthAnything/Depth-Anything-V2 | Small为Apache-2.0；不替换为有非商业限制的Base/Large/Giant |

Gradio、Diffusers、Transformers与Hugging Face Hub依赖保留其发行包内许可；本仓库未复制其库源码。模型下载保留仓库中的LICENSE/README等说明。不要把本项目LICENSE套用到第三方权重。

Kokoro使用espeak-ng（GPL-3.0-or-later系统组件）和相应语音前端；再分发其二进制镜像时保留包版权及对应源码获取方式。Ubuntu包信息见 https://packages.ubuntu.com/jammy/espeak-ng 。FFmpeg组件的具体许可取决于发行包编译配置，保留系统包版权与来源，不声明整张镜像只有一种许可。

固定仓库revision、单文件大小与上游摘要见每个app.json。尚未发布全SHA256的官方资产不伪造摘要。Demucs只对固定官方且校验过的权重，在隔离子进程允许兼容其旧checkpoint加载；不接受用户上传模型。

完整研究依据见SOURCE_RESEARCH.md（套件根目录）。正式发布前也应检查所选模型当前使用条件及平台审核要求。
