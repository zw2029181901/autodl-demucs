# Demucs 音轨分离

将音乐分成人声、鼓、贝斯和其他伴奏，试听人声并下载四轨ZIP。

这是独立应用源码及部署脚本，不是已经上传的AutoDL云镜像。模型版本固定在 `app.json`。本包没有模型权重；下载来源、校验信息和许可均列在配置与 THIRD_PARTY.md。

## 环境与空间

- Ubuntu 22.04，Python 3.11（也允许3.12），每个应用独立虚拟环境。
- 支持CPU或GPU，推荐GPU；每次最多5分钟，7秒分块。建议8GB内存起测。
- 模型约 0.084GB，模型和输出建议预留 3GB；Python/CUDA依赖另计。系统盘建议至少保留15GB安装余量；最终以 `df -h` 为准。
- 许可：MIT。
- [上游项目](https://github.com/facebookresearch/demucs)。本项目添加中文网页、固定模型下载、部署和检查脚本，上游算法归原作者。

## 独立包部署

以下命令在AutoDL的Linux终端执行，不是在Windows执行。项目仓库为 `zw2029181901/autodl-demucs`；云镜像的部署和发布仍需完成后续验收。

```bash
cd /root
git clone https://github.com/zw2029181901/autodl-demucs.git
cd /root/autodl-demucs
bash install.sh
# 可在无卡模式完成依赖安装和模型下载；GPU应用实际推理须有卡模式。
.venv/bin/python runtime/prefetch.py --project .
.venv/bin/python runtime/doctor.py --project . --models
bash start.sh
```

若Python不是3.11/3.12，先选择合适的基础镜像，或用 `PYTHON_BIN=/你的Python路径 bash install.sh`。
若PyPI下载慢，可显式使用清华源：`PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple bash install.sh`；PyTorch使用官方独立源。
若Hugging Face不可访问，可自行选择镜像端点：`HF_ENDPOINT=https://hf-mirror.com .venv/bin/python runtime/prefetch.py --project .`。这是下载源选项，不保证可达；仓库及revision不变。

打开实例的自定义服务6006。保持前台启动终端运行，或按 UPLOAD_GUIDE.md 的后台启动方式运行。网页出现后必须完成 SMOKE_TEST.md 的真实任务。
如需密码：`APP_USERNAME=user APP_PASSWORD='自行设置' bash start.sh`。公开镜像保存前不要把自己的密码写进代码或脚本。

## 模型和保存镜像

默认把模型放在 `/root/autodl-tmp/autodl-models`（数据盘存在时）。**保存镜像只保存系统盘，数据盘模型不会随镜像分发。** 用户首次运行需要重新下载，或你配置并验证有效的公共模型目录。
按本次30GB账户总额度要求，不把权重复制到系统盘。优先使用已核实的公共模型目录，具体见 MODEL_STORAGE.md；Wan默认禁用自动下载。
系统盘安装依赖仍会增加镜像容量，不能仅凭不含权重就保证10份镜像都在账户剩余额度内。每保存一份要查看平台合计容量。
也可用 `MODEL_PATH_MAIN=/实际模型快照目录` 指向已存在的Hugging Face格式目录（仅适用本包kind=hf模型），或用link_model.py保存该路径。CPU可用的工具默认安装CPU版PyTorch，选择CUDA环境后才使用GPU。
权重不会自动由网址变成零占用。公共路径必须实际存在。

## 验收与发布

看 SMOKE_TEST.md、PUBLICATION.md 和 UPLOAD_GUIDE.md。本地网页启动通过不等于云端GPU推理通过。正式公开前至少完成真实任务、新实例复建与开机启动测试。
安装会保存 `installed-requirements.txt`，请在云端验收后保留它作为该镜像的依赖记录。没有自动更新依赖或模型的后台任务。
