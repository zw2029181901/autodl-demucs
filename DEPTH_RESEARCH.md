# 本批轻量深度模型的来源

本批以Depth Anything V2 Small替代需要大体积完整权重的Wan视频项目，原Wan源码作为备选保留，不计入本批十个ZIP。

- 官方代码：https://github.com/DepthAnything/Depth-Anything-V2/tree/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf
- 官方模型：https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf/tree/5426e4f0f36572d16453bbda7a8389317b1bef99
- Small许可Apache-2.0；不替换为带非商业限制的Base/Large/Giant。
- 权重99,173,660字节，SHA256为3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70。
- Transformers4.57.1原生AutoImageProcessor（use_fast=False）及AutoModelForDepthEstimation，后处理target_sizes使用(height,width)。
- 官方接口：https://github.com/huggingface/transformers/blob/v4.57.1/docs/source/en/model_doc/depth_anything_v2.md
- 输出为相对深度/视差，可逐图归一化，不能解释为米制距离。常量图和非有限值均有保护。

元数据与权重经hf-mirror传输，固定revision并校验文件摘要；云端实际推理记录见validation/cloud-report.json。
