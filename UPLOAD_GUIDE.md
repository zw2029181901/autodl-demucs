# AutoDL镜像与后续维护

2026-11-12：本批十项已全部保存镜像并提交v1审核，账号全部镜像27.66GB，维护实例已关机。目前等待平台审核，无需再次上传或填表。

## 本批已代操作的流程

源码上传GitHub → 独立环境安装并完成真实任务 → 应用与模型迁移系统盘 → 关机保存镜像 → 在AutoDL.Art关联仓库并提交审核。

十个GitHub仓库属于 `zw2029181901`，AutoDL.Art账号为 `200211（金鳞）`。逐项镜像UUID、平台大小、审核提交链接及最后核验状态见 `validation/publication-report.json`；单项说明见各仓库的 `IMAGE_README.md`、`PUBLICATION.md`、`IMAGE_VALIDATION.json`。

已经完成的上传和提交不需要再做。审核中条目暂不可公开创建实例；页面同时显示“已下架”时，先看是否提示“v1版本镜像正在审核中”，不要因此重复提交。若平台给出驳回原因，再针对具体问题修改。

社区镜像、应用广场APP、ComfyUI工作流API是不同入口。本批交付为十个独立网页应用的镜像与社区条目，不会自动成为工作流API商品。

## 客户使用

1. 审核通过且条目可创建实例后，从相应AutoDL.Art页面创建实例。
2. 实例启动后，打开“自定义服务6006”。模型已在系统盘，无需重新下载。
3. 按中文页面上传输入或填写文字，运行并下载结果。各工具默认运行方式见README；SDXL需要GPU。

镜像内统一路径：

- 应用及依赖：`/root/autodl-active`
- 权重：`/root/autodl-active/models`
- 服务启动：`bash /root/autodl-active/run-service.sh`
- 检查：`/root/autodl-active/.venv/bin/python /root/autodl-active/runtime/doctor.py --project /root/autodl-active --models --http`

U2Net已在全新RTX3080Ti实例验证自动启动、离线权重与真实任务。其余九项在原实例完成独立环境真实HTTP推理及系统盘迁移检查，沿用相同开机机制；没有逐一进行保存镜像的客户新实例恢复测试，也没有验证所有GPU型号。

## 更新某一个工具

1. 修改对应GitHub仓库并保留模型和第三方依赖的许可。
2. 在维护实例准备对应独立环境，检查固定模型版本、依赖及真实任务。避免同时启动十台GPU实例。
3. 确认客户需要的代码、依赖、模型均在系统盘。原实例的数据盘不会随保存镜像分发。
4. 检查自启动与6006服务，关机后“更多 → 保存镜像”，使用新的版本名，记录平台UUID与大小。
5. 在AutoDL.Art更新对应条目并提交新版本，等待审核。不要仅改名称重复上架同一工具。

保存镜像前清理本次个人输入输出，检查发布内容不含密码、登录令牌或SSH私钥。保留必要的模型与许可证。每次保存后核对账号所有镜像总量，免费额度为30GB；不依赖基础层去重的假设，不自动扩容或删除旧镜像。

关机能停止运行计算费，数据盘等保留费用按平台当前规则计算。释放实例会失去该实例中的维护数据；保存镜像和GitHub源码独立存在，但在确认所有待保留内容已备份前不要释放维护实例。

## 从GitHub源码另行安装

以下仅用于重建，已经使用保存镜像的客户无需执行。以U2Net为例，在AutoDL Linux终端运行：

```bash
cd /root
git clone https://github.com/zw2029181901/autodl-u2net.git
cd /root/autodl-u2net
bash install.sh
.venv/bin/python runtime/prefetch.py --project .
.venv/bin/python runtime/doctor.py --project . --models
bash start.sh
```

选择Ubuntu22.04和Python3.11或3.12，其他项目使用对应README和SMOKE_TEST.md。源码安装不会自动生成本批镜像专用的 `run-service.sh`，应使用源码自带的 `start.sh`。前台启动或nohup不等于开机自启动，更新开机机制后须验证。

默认CPU工具不另装CUDA框架。改为GPU加速会增加体积，须重新检查依赖及任务。安装脚本允许在精确版本匹配时通过 `USE_BASE_TORCH=1` 复用基础PyTorch；版本不匹配时不得盲目复用。公共模型路径须按MODEL_STORAGE.md核实，不能假定客户实例含有原数据盘或任意公共模型。

`dist/`中的独立ZIP只含源码与说明，不能直接上传为平台镜像。迁移到另一个GitHub账号时，解压后把源码放在仓库根目录，并修改关联地址。

## 官方说明

- [保存镜像](https://www.autodl.com/docs/image/)：保存系统盘，数据盘不随镜像分发。
- [AutoDL.Art镜像](https://www.autodl.art/docs/image/)：关联GitHub项目与镜像。
- [公共模型](https://www.autodl.art/docs/app_model/)：核实模型文件与路径后使用。
- [镜像存储计费](https://www.autodl.com/docs/price/#_14)：以当前规则及平台实际总容量为准。
- [创作激励](https://www.autodl.art/docs/reward_rule/)：是否符合激励和审核要求以平台为准。
