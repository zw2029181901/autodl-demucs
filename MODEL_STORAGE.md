# 30GB额度与公共模型

30GB是账号下所有已保存镜像的总免费存储额度，不是每个模型都可以占30GB，也不等于运行实例的内存或显存。

本包不携带权重；模型默认位于数据盘 `/root/autodl-tmp/autodl-models`。数据盘不进系统盘镜像，因而镜像可以小，但用户运行时仍需要真实权重。数据盘的可用空间、持久化规则及收费另看平台。

已验收的小模型可以放在项目内 `models/应用id/文件名`，或将 Hugging Face 缓存放在 `models/hub`，随系统盘保存。运行时按 `MODEL_ROOT` 显式设置、项目 `models` 目录、数据盘缓存的顺序选择存储位置。这样新实例不需要原数据盘，但会增加保存镜像体积；必须计入账号总额度。不要把指向原数据盘的软链接当成已打包权重。

## 使用公共模型

平台公共模型可用时，不复制权重进系统盘。必须在当前实例中取得真实路径，核对模型名、版本和格式；本包没有编造公共路径。

官方示例 `/.autodl/...` 指向具体模型文件；`/root/autodl-pub` 则是公共数据目录。它们不保证包含本批10个模型。尤其**ComfyUI的单个safetensors不是Diffusers完整目录**。

对于SDXL/Wan等Hugging Face格式模型，准备完整目录，包含model_index/config、tokenizer、所有组件权重。逐文件软链接组合目录也是可行形式，但须确认链接源在客户新实例中仍存在。随后运行：

```bash
.venv/bin/python runtime/link_model.py --project . --path /实际的完整模型目录
.venv/bin/python runtime/doctor.py --project . --models
```

脚本检查必需文件，再保存 `model-paths.local.json` 这个小路径文件，不复制权重。也可临时使用 `MODEL_PATH_MAIN=/实际目录 bash start.sh`。结构检查不等于模型身份校验，必须按app.json核对来源并实际运行。

对于U2Net/Real-ESRGAN/Demucs单文件模型，可将平台真实文件软链接到 `MODEL_ROOT/应用id/app.json里的filename`；模型大小和已有摘要会校验。不要替换为同名但不同结构的权重。

## Wan的特殊限制

Wan2.1 Diffusers固定版本原始文件约28.9GB，需要额外余量。根据你的限制，配置 `local_only=true`，默认禁止下载。没有匹配的现有模型目录时，页面能打开，但生成会明确报“需配置公共模型目录”。在确认该目录和实际生成之前，不应公开为可用应用。

## 省空间安装

- Whisper和U2Net不安装PyTorch。
- Kokoro/Real-ESRGAN/SAM2/BLIP/Demucs/E5默认安装CPU版PyTorch，省空间；要GPU加速需自行改用cu128并再次验收体积。
- SDXL/Wan安装cu128版PyTorch，或通过USE_BASE_TORCH=1复用精确匹配的基础版本。
- pip下载缓存关闭；源码ZIP只收录白名单，不收venv、权重、输出、凭据。
- 不会自动扩容或删除已有镜像。最终以平台每次保存后显示的总容量为准，没有“十份必然共用基础层只收一份”的保证。

镜像大于剩余额度时，先停下；可考虑共用一份运行环境、减少重复依赖或只保留需要的版本。删除旧镜像需由你确认具体对象，不由部署脚本自动执行。
