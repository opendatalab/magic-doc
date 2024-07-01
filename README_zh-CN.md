<div id="top"></div>
<div align="center">

[![license](https://img.shields.io/github/license/InternLM/magic-doc.svg)](https://github.com/InternLM/magic-doc/tree/main/LICENSE)
[![issue resolution](https://img.shields.io/github/issues-closed-raw/InternLM/magic-doc)](https://github.com/InternLM/magic-doc/issues)
[![open issues](https://img.shields.io/github/issues-raw/InternLM/magic-doc)](https://github.com/InternLM/magic-doc/issues)

[English](README.md) | [简体中文](README_zh-CN.md)

</div>

<div align="center">

</div>


### 安装
前置依赖： python3.10 + 

安装依赖

**linux/osx** 

```bash
apt-get/yum/brew install libreoffice
```

**windows**
```text
安装 libreoffice 
添加 "install_dir\LibreOffice\program" to 环境变量 PATH
```


安装 Magic-Doc


```bash
pip install fairy-doc[cpu] # 安装 cpu 版本 
或 
pip install fairy-doc[gpu] # 安装 gpu 版本
```


## 简介

Magic-Doc 是一个轻量级、开源的用于将多种格式的文档（PPT/PPTX/DOC/DOCX/PDF) 转化为 markdown 格式的工具。支持转换本地文档或者位于 AWS S3 上的文件


## 使用示例

```python
# for local file
from magic_doc.docconv import DocConverter, S3Config
converter = DocConverter(s3_config=None)
markdown_cotent, time_cost = converter.convert("some_doc.pptx", conv_timeout=300)
```

```python
# for remote file located in aws s3
from magic_doc.docconv import DocConverter, S3Config

s3_config = S3Config(ak='${ak}', sk='${sk}', endpoint='${endpoint}')
converter = DocConverter(s3_config=s3_config)
markdown_cotent, time_cost = converter.convert("s3://some_bucket/some_doc.pptx", conv_timeout=300)
```


## 性能
环境：AMD EPYC 7742 64-Core Processor, NVIDIA A100, Centos 7

| 文件类型        | 转化速度| 
| ------------------ | -------- | 
| PDF (digital)      | 347 (page/s)   | 
| PDF (ocr)          | 2.7 (page/s)   | 
| PPT                | 20 (page/s)    | 
| PPTX               | 149 (page/s)   | 
| DOC                | 600 (page/s)   | 
| DOCX               | 1482 (page/s)  | 



## 开源许可证

该项目采用[Apache 2.0 开源许可证](LICENSE)。

<p align="right"><a href="#top">🔼 Back to top</a></p>
