<div id="top"></div>
<div align="center">
  <h2>Deep-Parser</h2>

[English](README.md) | 简体中文

</div>

______________________________________________________________________

## 功能更新 🎉
 - 支持几乎所有文档格式的解析

______________________________________________________________________

# 简介

**Deep-Parser**，是AI数据平台的核心服务，集成了全格式文档解析的能力，其深度解析效果源自开源界最先进的解析库，本项目做了集成和优化。

这个强大的工具箱提供以下核心功能：

- **高效的解析**：Deep-Parser 底层采用各种最先进的文档解析引擎，集成多种优化技术，包括OCR、双栏PDF、内嵌表格解析等。

- **轻松的管理**：提供在线管理能力。

- **便捷的服务**：提供文件解析API。

它是“风后®AI”服务开发所用的数据解析服务，具备企业级产品支撑能力。
它也可以和其他框架协作和集成。

# 性能

提供离线解析，在线可视化解析进度。

# 支持的格式

| Model | Size |
|:-----:|:----:|
|  文本   | pdf  |
|  文本   | doc  |
|  文本   | docx |
|  表格   | xls  |
|  表格   | xlsx |
|  图片   | png  |
|  图片   | jpg  |

Deep-Parser 支持 30余种文档格式。

另外支持多种解析选项，用户可并根据实际需求选择合适的。

# 快速开始

## 安装

使用 pip ( python 3.8+) 安装 Deep-Parser，或者 推荐 [源码安装]

```shell
pip install deep_parser
```

## 贡献指南

我们感谢所有的贡献者为改进和提升 Deep-Parser 所作出的努力。欢迎参与项目贡献。

## 致谢

- [FasterTransformer](https://github.com/NVIDIA/FasterTransformer)
- [llm-awq](https://github.com/mit-han-lab/llm-awq)
- [vLLM](https://github.com/vllm-project/vllm)
- [DeepSpeed-MII](https://github.com/microsoft/DeepSpeed-MII)
- [FastChat](https://github.com/lm-sys/FastChat)

## License

该项目采用 [Apache 2.0 开源许可证](LICENSE)。

<p align="right"><a href="#top">🔼 Back to top</a></p>