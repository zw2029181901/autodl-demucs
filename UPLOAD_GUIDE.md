# 从源码包到AutoDL发布

## 先记住这个逻辑

**源码上传GitHub → 在AutoDL实例安装、运行并验收 → 关机保存系统盘镜像 → 到AutoDL.Art关联项目提交 → 按平台要求配置APP入口及审核。**

ZIP是源码交付物，不能直接上传成AutoDL镜像。社区镜像、应用广场APP、平台维护的ComfyUI工作流API是不同入口。本批是独立网页应用；公开镜像不会自动出现在工作流API市场。

## 1. 上传GitHub源码

登录 `zw2029181901`。建议先做模型最小的 `U2Net 抠图` 验证流程，成功后重复其他九项。

1. 解压 `autodl-u2net.zip`。打开里面的 `autodl-u2net` 文件夹，应直接看到 `app.py`、`app.json`、`install.sh`、`start.sh`、`runtime`。
2. 在GitHub右上角“+ → New repository”，名称填 `autodl-u2net`，Owner选 `zw2029181901`，可见性选Public。
3. 创建后选“uploading an existing file”，上传解压后文件夹中的全部源码文件和子目录，提交。不要上传venv、缓存、模型、密码或输入输出。
4. 打开仓库首页，应能直接看见README和 `app.py`，不能多套一层目录。其他九个仓库名在各包的PUBLICATION.md里。

如果使用GitHub CLI，也可在登录后执行本源码套件的 `tools/publish-github.ps1`。它会核对账号，默认只预览；加 `-Publish` 才创建公开仓库并推送，遇到同名仓库会停止，不覆盖旧项目。

## 2. 安装到AutoDL实例

继续使用此前已成功发布的普通容器流程。选择Ubuntu22.04、Python3.11或3.12；GPU版需要支持CUDA12.8的驱动。不要同时开十台收费GPU实例。

先用无卡模式安装/下载（若当前实例支持），真实GPU推理验收时再有卡开机。以下是U2Net独立仓库的完整命令：

```bash
cd /root
git clone https://github.com/zw2029181901/autodl-u2net.git
cd /root/autodl-u2net
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple bash install.sh
.venv/bin/python runtime/prefetch.py --project .
.venv/bin/python runtime/doctor.py --project . --models
bash start.sh
```

在实例里打开自定义服务6006，上传一张商品图运行，再下载透明PNG检查。其他项目使用各自README的命令和SMOKE_TEST验收样例。Wan需要先按MODEL_STORAGE.md绑定已有公共模型目录，不执行下载。

默认不安装第二份GPU框架给CPU工具。若确实需要把CPU工具改成GPU版：

```bash
TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128 bash install.sh
```

修改现有CPU环境时，先检查 `.venv/bin/python -c "import torch; print(torch.__version__, torch.version.cuda)"`。pip可能把同版本CPU包认作已满足；必要时用该索引显式安装 `torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128`，再重新执行依赖和任务验收。扩展CUDA环境会增加体积。

若基础镜像本身精确提供torch2.8.0、torchvision0.23.0，可在首次安装时 `USE_BASE_TORCH=1 bash install.sh` 复用基础环境。Demucs还需torchaudio2.8.0。脚本会验证版本；其它版本不盲目复用。该选项可能继承基础环境的依赖，仍须通过pip check和真实任务。平台是否对多份镜像去重收费没有官方保证。

## 3. 后台启动与开机检查

前台的 `bash start.sh` 需要保持终端；如需后台运行，在项目目录执行：

```bash
nohup bash start.sh > app.log 2>&1 < /dev/null &
.venv/bin/python runtime/doctor.py --project . --http
```

这只维持本次开机运行，**不等于重启后自启动**。若当前平台有“启动命令/开机命令”字段，填 `bash /root/autodl-u2net/start.sh`（对应其他项目替换目录）。若没有该字段，不要在不存在的位置操作；需要根据当前实例的官方开机机制另行设置。

必须关机再开机验证：没有手动敲启动命令也能打开6006并完成任务，才可宣传“开箱即用”。没有通过这一步的包只应注明手动启动。不要把 `nohup` 当成开机自启动。

## 4. 保存镜像，并守住30GB总额

1. 确认代码/venv在 `/root/项目名`，模型缓存放数据盘或用已核实公共目录。数据盘不进镜像；小模型可按MODEL_STORAGE.md打包在项目models目录，并计入额度。不要把大模型复制到系统盘。
2. 保存真实任务验收结果和 `installed-requirements.txt`，清理自己本次测试的个人输入输出；保留许可文件。不要把个人登录令牌、SSH私钥、密码写进发布内容。
3. 关机，然后实例“更多 → 保存镜像”。按项目名填写，比如 `autodl-u2net`。
4. “我的镜像”显示就绪后，记录该镜像大小以及所有镜像合计。你截图已有3.83GB；新镜像合计预算约26.17GB，建议再留至少1GB余量。接近总30GB就停止新增，调整依赖或合并环境；不自动扩容。
5. 有预算时用保存的镜像创建新实例验收。它不会继承原实例数据盘，因此这一步必须检查公共模型是否仍可见、首次下载是否正常。验证完按自己的计划关闭收费实例。

## 5. AutoDL.Art提交

登录 `200211（金鳞）`，确认页面账号。用“+ 发布”里的对应镜像入口，选择已就绪镜像并关联你的GitHub项目。字段直接参考该项目的PUBLICATION.md。

名称只写模型名与功能；说明写输入、输出、运行方式和已实测硬件。自主编写的界面、交互与部署增量可以具体列出。第三方模型和许可在仓库保留，不把上游算法写成原创。

若还需成为应用广场APP，继续平台对应APP配置/审核；是否允许10条应用共用一个镜像，需要当前后台确认。不要为同一模型仅改名字重复上架，也不承诺勾选“原创”一定通过。

## 官方依据

- [AutoDL保存镜像](https://www.autodl.com/docs/image/)：保存系统盘；不支持直接导入任意自定义Docker镜像。
- [AutoDL.Art镜像](https://www.autodl.art/docs/image/)：关联可运行的GitHub项目。
- [公共模型路径](https://www.autodl.art/docs/app_model/)：检查实际文件后使用软链接。
- [镜像存储计费](https://www.autodl.com/docs/price/#_14)：按所有镜像总容量计费，30GB以下免费，以当日最大值计算。
- [创作激励规则](https://www.autodl.art/docs/reward_rule/)：最终以上架审核及当前规则为准。
