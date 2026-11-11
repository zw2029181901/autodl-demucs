# Demucs 音轨分离 验收

以下项目需要在你的实例完成；勾选前不能宣传“已测试可用”。

1. `bash install.sh` 成功，`pip check`、依赖导入和UI构建均通过。
2. `.venv/bin/python runtime/prefetch.py --project .` 下载完成。
3. `.venv/bin/python runtime/doctor.py --project . --models` 成功；需要GPU的应用还应打印CUDA矩阵运算成功。
4. `bash start.sh` 后，另一个终端运行 `.venv/bin/python runtime/doctor.py --project . --http`。6006网页能打开。
5. 上传有权使用的10秒歌曲片段。应生成vocals/drums/bass/other四个WAV，时长一致，人声预览可播放，ZIP可解压。
6. 再执行第二次任务，确认使用缓存、无报错；记录显卡、显存、内存、模型下载量、首次及第二次耗时。
7. 在平台配置开机命令后关机再开机，**不手动启动**也能从6006访问并完成任务。脚本存在本身不代表自动启动。
8. 保存镜像后用该镜像创建一个新实例（这一步会产生平台费用，按你的预算执行），验证代码、依赖、模型下载/挂载和启动流程。数据盘内容不随镜像复制。

建议把输入、输出和日志存到单独的验收目录，公开前去掉个人文件。不要在没有实测时标注全部GPU均支持。
