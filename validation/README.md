# 验证状态

本地环境：Windows，Python3.12；没有连接AutoDL实例，没有使用收费云GPU。

`local-report.json` 是工具真实启动后的结果：10个中文页面构建、根页面HTTP200、/config及任务入口检查。`tests` 包含字幕边界、分块边界、透明图合成、输出路径、损坏模型、Wan禁下载、模型缺分片共8项检查。

本地额外安装了PyTorch2.8.0 CPU、Diffusers0.35.2、Transformers4.57.1、faster-whisper1.2.1、rembg2.0.67、Demucs4.0.1等依赖，验证类可以导入；Real-ESRGAN的兼容RRDB网络完成8×12→32×48随机张量前向检查。这不证明预训练权重质量或云端GPU兼容。

U2Net官方GitHub权重下载在本机直连超时，API方式速度过慢，已停止；没有完成其模型推理。没有为SDXL/Wan下载大型权重。Kokoro英语spaCy数据包和系统espeak-ng/ffmpeg仍需在Linux实例按安装脚本验证。

待云端完成：所有项目的真实输入输出验收；公共模型文件/格式；Linux安装与驱动；服务端口；关机再开机自动启动；镜像保存后的体积；客户新实例复建；平台发布审核。不能将本地UI通过改写为“十个镜像已上线/所有GPU都支持”。
